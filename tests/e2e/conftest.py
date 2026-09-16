import logging

import pytest
from playwright.async_api import async_playwright
from sqlalchemy import text

from adapters.uow import UnitOfWork
from db.mapper import registry
from adapters.db_provider import DbProvider
from core import conf
from core.logger import setup_test_logging
from domain import Category, Collection, Image

setup_test_logging()
log = logging.getLogger(__name__)


@pytest.fixture(scope="session")
async def browser():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        yield browser
        await browser.close()


@pytest.fixture
async def page(browser):
    page = await browser.new_page()
    yield page
    await page.close()


#tmp_path - pytest fixture для расположения файлов по отведенному для этого для тестов пути
@pytest.fixture
def image_files(tmp_path):
    """Создает реальные, но крошечные файлы картинок, которые Pillow поймет"""
    # Это байты валидного 1x1 JPEG белого цвета
    tiny_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.' \",#\x1c\x1c(7),01444\x1f'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xbf\x00\xff\xd9"

    main_img = tmp_path / "main.jpg"
    main_img.write_bytes(tiny_jpeg)

    additional_img = tmp_path / "additional.jpg"
    additional_img.write_bytes(tiny_jpeg)

    return str(main_img), str(additional_img)


@pytest.fixture(scope="session")
async def db_provider():
    provider = DbProvider(conf.db_url)
    yield provider
    await provider.close()


@pytest.fixture()
def uow_fix(db_provider):
    return UnitOfWork(provider=db_provider, registry=registry)


@pytest.fixture(autouse=True)
async def clean_database_after_test(db_provider):
    yield

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


@pytest.fixture()
async def category(uow_fix):
    async with uow_fix as uow:
        return await uow.db.create(Category(name="category"))


@pytest.fixture()
async def collection(uow_fix):
    async with uow_fix as uow:
        return await uow.db.create(Collection(name="category", image=Image(image_path="path"), categories=Category(name="category")))


@pytest.fixture()
async def created_tile(uow_fix, tile):
    async with uow_fix as uow:
        tile.size = await uow.db.create(tile.size)
        tile.box = await uow.db.create(tile.box)
        tile.category = await uow.db.create(tile.category)
        tile.producer = await uow.db.create(tile.producer)
        tile.color = await uow.db.create(tile.color)

        if tile.surface:
            tile.surface = await uow.db.create(tile.surface)

        for i, image in enumerate(tile.images):
            image.image_path = f"media/products/test-{i}.jpg"

        return await uow.db.create(tile)
