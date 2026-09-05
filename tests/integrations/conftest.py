import logging
import shutil
from pathlib import Path

import pytest
from sqlalchemy import text

from adapters.uow import UnitOfWork
from db.mapper import registry
from adapters.db_provider import DbProvider
from adapters.images import CollectionImagesManager, ProductImagesManager
from adapters.query_service import CatalogQueryService
from adapters.redis import RedisService, RedisProvider
from core import conf
from domain import *
from tests.fakes import FakeImageGenerator
from dataclasses import dataclass


log = logging.getLogger(__name__)


@pytest.fixture(scope="session")
async def db_provider():
    provider = DbProvider(conf.db_url)
    yield provider
    await provider.close()


@pytest.fixture
async def uow_fix(request, db_provider):
    uow = UnitOfWork(registry=registry, provider=db_provider)
    yield uow
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


@pytest.fixture(autouse=True)
def clean_fs_after_test(request):
    yield
    images_path = Path("tests/images")
    if images_path.exists() and images_path.is_dir():
        shutil.rmtree(images_path)


@dataclass
class ProductsEnv:
    uow: UnitOfWork
    file_manager: ProductImagesManager
    images_generator: FakeImageGenerator


@dataclass
class CollectionsEnv:
    uow: UnitOfWork
    file_manager: CollectionImagesManager
    images_generator: FakeImageGenerator


@pytest.fixture
def products_env(uow_fix) -> ProductsEnv:
    file_manager = ProductImagesManager(root="tests/images")
    return ProductsEnv(
        uow=uow_fix,
        file_manager=file_manager,
        images_generator=FakeImageGenerator(),
    )


@pytest.fixture
def collections_env(uow_fix) -> CollectionsEnv:
    file_manager = CollectionImagesManager(root="tests/images")
    return CollectionsEnv(
        uow=uow_fix,
        file_manager=file_manager,
        images_generator=FakeImageGenerator(),
    )


@pytest.fixture
async def collections_env_with_categories(collections_env):
    async def wrapper(categories_cnt: int = 1):
        manager, file_manager = collections_env
        categories = []
        for i in range(categories_cnt):
            category = Category(name=f"category{i}")
            log.debug("category_name: %s", category.name)
            categories.append(category)
        await manager.create(seq_data=categories)
        return collections_env, [category.name for category in categories]

    return wrapper


@pytest.fixture
async def products_env_with_handbooks(products_env) -> ProductsEnv:
    uow = products_env.uow
    async with uow:
        await uow.db.create(
            seq_data=[
                TileSize(length=300, width=200, height=10),
                TileColor(color_name="color", feature_name="feature"),
                Producer(name="producer"),
                Box(weight=30, area=1),
                TileSurface(name="surface"),
                Category(name="category"),
            ]
        )
    return products_env


# @pytest.fixture
# async def products_env_with_tiles(crud):
#     async def wrapper(categories: dict, category_with_collection: dict = None):
#         manager, product_file_manager, collection_file_manager = (
#             crud,
#             ProductImagesManager(root="tests/images", storage=FakeStorage()),
#             CollectionImagesManager(root="tests/images", storage=FakeStorage()),
#         )
#         category_with_collection = (
#             category_with_collection if category_with_collection else {}
#         )
#         for category_name, tiles_count in categories.items():
#             collection_name = category_with_collection.get(category_name, False)
#             for i in range(tiles_count):
#                 await add_tile_helper(
#                     manager=manager,
#                     file_manager=product_file_manager,
#                     images_generator=FakeImageGenerator(),
#                     test_uow_class=False,
#                     category_name=category_name,
#                     size=TileSize(length=i, width=i, height=i),
#                     color=TileColor(color_name=f"color{i}", feature_name=f"feature{i}"),
#                     producer_name=f"producer{i}",
#                 )
#             if category_with_collection.get(category_name, False):
#                 await add_collection_helper(
#                     manager=manager,
#                     file_manager=collection_file_manager,
#                     images_generator=FakeImageGenerator(),
#                     collection_name=collection_name,
#                     category_name=category_name,
#                     test_uow_class=False,
#                 )
#         return manager
#
#     return wrapper


@pytest.fixture
def query_service(db_provider):
    return CatalogQueryService(db_provider.session_factory)


@pytest.fixture
async def redis():
    redis_provider = await RedisProvider.create(conf.redis_host)
    return RedisService(redis=redis_provider.client)
