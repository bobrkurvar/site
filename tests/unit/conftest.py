
import pytest

from adapters.images import CollectionImagesManager, ProductImagesManager
from domain import Box, Category, Producer, TileColor, TileSize, TileSurface
from tests.fakes import FakeCRUD, FakeRedisService, FakeStorage, FakeImageGenerator
from dataclasses import dataclass
from tests.fakes.db_fakes import FakeUoW




@pytest.fixture
def db():
    return FakeCRUD()


@pytest.fixture
def uow(db):
    return FakeUoW(db)


@pytest.fixture
def redis():
    return FakeRedisService()


@pytest.fixture
async def products_env_with_handbooks(products_env):
    await products_env.uow.db.create(
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


@dataclass
class ProductsEnv:
    uow: FakeUoW
    file_manager: ProductImagesManager
    image_generator: FakeImageGenerator
    fs: dict


@dataclass
class CollectionsEnv:
    uow: FakeUoW
    file_manager: CollectionImagesManager
    image_generator: FakeImageGenerator
    fs: dict


@pytest.fixture
def products_env(uow):
    fs = {}
    file_manager = ProductImagesManager(
        root="tests/images",
        storage=FakeStorage(fs),
    )

    return ProductsEnv(
        uow=uow,
        file_manager=file_manager,
        fs=fs,
        image_generator=FakeImageGenerator(),
    )


@pytest.fixture
def collections_env(uow):
    fs = {}
    file_manager = CollectionImagesManager(
        root="tests/images",
        storage=FakeStorage(fs),
    )

    return CollectionsEnv(
        uow=uow,
        file_manager=file_manager,
        fs=fs,
        image_generator=FakeImageGenerator(),
    )
