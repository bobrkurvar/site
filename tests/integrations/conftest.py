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
from adapters.images_http_client import ImageHttpClient


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
                    tiles,
                    tile_colors,
                    collections,
                    tile_surface,
                    collection_category,
                    admins
                RESTART IDENTITY CASCADE;
            """
            )
        )

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
    #images_generator: ImageHttpClient


@dataclass
class CollectionsEnv:
    uow: UnitOfWork
    file_manager: CollectionImagesManager
    images_generator: FakeImageGenerator
    #images_generator: ImageHttpClient


@pytest.fixture
def products_env(uow_fix) -> ProductsEnv:
    file_manager = ProductImagesManager(root="tests/images")
    return ProductsEnv(
        uow=uow_fix,
        file_manager=file_manager,
        images_generator=FakeImageGenerator(),
        #images_generator=ImageHttpClient(base_url=conf.image_service_url)
    )


@pytest.fixture
def collections_env(uow_fix) -> CollectionsEnv:
    file_manager = CollectionImagesManager(root="tests/images")
    return CollectionsEnv(
        uow=uow_fix,
        file_manager=file_manager,
        #images_generator=ImageHttpClient(base_url=conf.image_service_url)
        images_generator=FakeImageGenerator(),
    )


@pytest.fixture
async def collections_env_with_categories(collections_env):
    async def wrapper(categories_cnt: int = 1):
        categories = []
        for i in range(categories_cnt):
            category = Category(name=f"category{i}")
            log.debug("category_name: %s", category.name)
            categories.append(category)
        async with collections_env.uow as uow:
            categories = await uow.db.create(seq_data=categories)
        return collections_env, categories

    return wrapper


@pytest.fixture
async def products_env_with_handbooks(products_env) -> ProductsEnv:
    uow = products_env.uow
    async with uow:
        await uow.db.create(
            seq_data=[
                Size(length=300, width=200, height=10),
                Color(color_name="color", feature_name="feature"),
                Producer(name="producer"),
                Box(weight=30, area=1),
                Surface(name="surface"),
                Category(name="category"),
            ]
        )
    return products_env



@pytest.fixture
def query_service(db_provider):
    return CatalogQueryService(db_provider.session_factory)


@pytest.fixture
async def redis():
    redis_provider = await RedisProvider.create(conf.redis_host)
    return RedisService(redis=redis_provider.client)
