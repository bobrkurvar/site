import logging
import shutil
from pathlib import Path

import pytest
from sqlalchemy import text

from adapters.db import build_crud
from adapters.db_provider import DbProvider
from domain import *
from adapters.images import ProductImagesManager, CollectionImagesManager
from tests.fakes import FakeStorage, FakeImageGenerator
from tests.helpers import add_collection_helper, add_tile_helper_with_control_filters
from core import conf


log = logging.getLogger(__name__)


@pytest.fixture
async def crud(request):
    db_provider = DbProvider(conf.test_db_url)
    manager = build_crud(db_provider.session_factory)
    yield manager
    async with db_provider.engine.begin() as conn:
        await conn.execute(
            text(
                """
            TRUNCATE
                tile_images,
                categories,
                producers,
                tile_sizes,
                boxes,
                catalog,
                tile_colors,
                collections,
                tile_surface,
                slugs,
                collection_category
                
            RESTART IDENTITY CASCADE;
        """
            )
        )
    await db_provider.close()


@pytest.fixture
async def manager_with_categories(crud):
    category_name1, category_name2 = "category1", "category2"
    await crud.create(Category, name=category_name1)
    await crud.create(Category, name=category_name2)
    return crud


@pytest.fixture(autouse=True)
def clean_fs_after_test(request):
    if not any(
        "integration" in marker.name
        for item in request.session.items
        for marker in item.iter_markers()
    ):
        yield
        return

    yield
    images_path = Path("tests/images")
    if images_path.exists() and images_path.is_dir():
        shutil.rmtree(images_path)


@pytest.fixture
def products_env(crud):
    file_manager = ProductImagesManager(root="tests/images")
    return crud, file_manager


@pytest.fixture
async def collections_env(crud):
    file_manager = CollectionImagesManager(root="tests/images")
    return crud, file_manager


@pytest.fixture
async def collections_env_with_categories(collections_env):
    async def wrapper(categories_cnt: int = 1):
        manager, file_manager = collections_env
        categories = []
        for i in range(categories_cnt):
            category_name = f"category{i}"
            log.debug("category_name: %s", category_name)
            categories.append(category_name)
            await manager.create(Category, name=category_name)
        return manager, file_manager, categories

    return wrapper


@pytest.fixture
async def products_env_with_handbooks(products_env):
    manager, file_manager = products_env
    await manager.create(
        TileSize, length=Decimal(300), width=Decimal(200), height=Decimal(10)
    )
    await manager.create(TileColor, color_name="color", feature_name="feature")
    await manager.create(Producer, name="producer")
    await manager.create(Box, weight=Decimal(30), area=Decimal(1))
    await manager.create(TileSurface, name="surface")
    await manager.create(Category, name="category")

    return manager, file_manager


@pytest.fixture
async def products_env_with_tiles(crud):
    async def wrapper(categories: dict, category_with_collection: dict = None):
        manager, product_file_manager, collection_file_manager = (
            crud,
            ProductImagesManager(root="tests/images", storage=FakeStorage()),
            CollectionImagesManager(root="tests/images", storage=FakeStorage()),
        )
        category_with_collection = (
            category_with_collection if category_with_collection else {}
        )
        for category_name, tiles_count in categories.items():
            collection_name = category_with_collection.get(category_name, False)
            for i in range(tiles_count):
                size, color_name, producer = f"{i} {i} {i}", f"color{i}", f"producer{i}"
                await add_tile_helper_with_control_filters(
                    manager,
                    product_file_manager,
                    FakeImageGenerator(),
                    False,
                    category_name=category_name,
                    size=size,
                    color_name=color_name,
                    producer=producer,
                )
            if category_with_collection.get(category_name, False):
                await add_collection_helper(
                    manager,
                    collection_file_manager,
                    FakeImageGenerator(),
                    collection_name=collection_name,
                    category_name=category_name,
                    test_uow_class=False,
                )
        return manager

    return wrapper
