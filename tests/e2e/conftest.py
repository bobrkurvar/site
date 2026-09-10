import asyncio
import logging
import threading

import pytest
from playwright.sync_api import sync_playwright
from sqlalchemy import text

from adapters.uow import UnitOfWork
from db.mapper import registry
from adapters.db_provider import DbProvider
from adapters.images import CollectionImagesManager, ProductImagesManager
from core import conf
from core.logger import setup_test_logging
from domain import Category
from tests.fakes.fs_fakes import FakeImageGenerator
from tests.helpers import add_collection_helper

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
    """Создает реальные, но крошечные файлы картинок, которые Pillow поймет"""
    # Это байты валидного 1x1 JPEG белого цвета
    tiny_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"

    main_img = tmp_path / "main.jpg"
    main_img.write_bytes(tiny_jpeg)

    additional_img = tmp_path / "additional.jpg"
    additional_img.write_bytes(tiny_jpeg)

    return str(main_img), str(additional_img)


_BACKGROUND_LOOP = None
_BACKGROUND_THREAD = None


@pytest.fixture(scope="session", autouse=True)
def shared_background_loop():
    global _BACKGROUND_LOOP, _BACKGROUND_THREAD

    _BACKGROUND_LOOP = asyncio.new_event_loop()
    _BACKGROUND_THREAD = threading.Thread(
        target=_BACKGROUND_LOOP.run_forever, daemon=True
    )
    _BACKGROUND_THREAD.start()

    yield _BACKGROUND_LOOP

    _BACKGROUND_LOOP.call_soon_threadsafe(_BACKGROUND_LOOP.stop)
    _BACKGROUND_THREAD.join()


def run_in_shared_loop(coro):
    future = asyncio.run_coroutine_threadsafe(coro, _BACKGROUND_LOOP)
    return future.result()


@pytest.fixture(scope="session")
async def db_provider():
    provider = DbProvider(conf.db_url)
    yield provider
    await provider.close()


@pytest.fixture(autouse=True)
def clean_database_after_test(db_provider):
    uow = UnitOfWork(registry=registry, provider=db_provider)
    yield uow

    async def do_truncate():
        try:
            async with db_provider.engine.begin() as conn:
                await conn.execute(
                    text(
                        """
                        TRUNCATE
                            tile_images, categories, producers, tile_sizes, 
                            boxes, tiles, tile_colors, collections, 
                            tile_surface, collection_category
                        RESTART IDENTITY CASCADE;
                        """
                    )
                )
        finally:
            await db_provider.close()

    run_in_shared_loop(do_truncate())




@pytest.fixture()
def add_categories(crud):
    def add_categories(*categories):
        categories = [Category(name=category) for category in categories]
        if not categories:
            categories = [Category("category1")]
        return run_in_shared_loop(crud.create(seq_data=categories))

    return add_categories

