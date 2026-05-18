import asyncio
import logging
import threading
from playwright.sync_api import sync_playwright
import pytest
from sqlalchemy import text

from adapters.db_provider import DbProvider
from core import conf
from core.logger import setup_test_logging

setup_test_logging()
log = logging.getLogger(__name__)



@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    page = browser.new_page()
    yield page
    page.close()


@pytest.fixture
def dummy_images(tmp_path):
    """Создает временные файлы картинок для загрузки в форму"""
    main_img = tmp_path / "main.jpg"
    main_img.write_bytes(b"fake_jpeg_main_image_bytes")

    additional_img = tmp_path / "additional.jpg"
    additional_img.write_bytes(b"fake_jpeg_additional_image_bytes")

    return str(main_img), str(additional_img)



_BACKGROUND_LOOP = None
_BACKGROUND_THREAD = None


@pytest.fixture(scope="session", autouse=True)
def shared_background_loop():
    global _BACKGROUND_LOOP, _BACKGROUND_THREAD

    _BACKGROUND_LOOP = asyncio.new_event_loop()
    _BACKGROUND_THREAD = threading.Thread(
        target=_BACKGROUND_LOOP.run_forever,
        daemon=True
    )
    _BACKGROUND_THREAD.start()

    yield _BACKGROUND_LOOP

    _BACKGROUND_LOOP.call_soon_threadsafe(_BACKGROUND_LOOP.stop)
    _BACKGROUND_THREAD.join()


def run_in_shared_loop(coro):
    future = asyncio.run_coroutine_threadsafe(coro, _BACKGROUND_LOOP)
    return future.result()


@pytest.fixture(scope="session")
def db_provider(shared_background_loop):
    provider = DbProvider(conf.test_db_url)
    yield provider
    run_in_shared_loop(provider.close())


@pytest.fixture(autouse=True)
def clean_database_after_test(db_provider):
    yield
    async def do_truncate():
        async with db_provider.engine.begin() as conn:
            await conn.execute(
                text(
                    """
                    TRUNCATE
                        tile_images, categories, producers, tile_sizes, 
                        boxes, catalog, tile_colors, collections, 
                        tile_surface, slugs, collection_category
                    RESTART IDENTITY CASCADE;
                    """
                )
            )
    run_in_shared_loop(do_truncate())