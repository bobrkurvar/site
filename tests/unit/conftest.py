import pytest

from adapters.images import CollectionImagesManager, ProductImagesManager
from tests.fakes import FakeRepo, FakeRedisService, FakeStorage, FakeImageGenerator
from dataclasses import dataclass
from tests.fakes.db_fakes import FakeUoW


@pytest.fixture
def db():
    return FakeRepo()


@pytest.fixture
def uow_fix(db):
    return FakeUoW(db)


@pytest.fixture
def redis():
    return FakeRedisService()


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
def products_env(uow_fix) -> ProductsEnv:
    fs = {}
    file_manager = ProductImagesManager(
        root="tests/images",
        storage=FakeStorage(fs),
    )

    return ProductsEnv(
        uow=uow_fix,
        file_manager=file_manager,
        fs=fs,
        image_generator=FakeImageGenerator(),
    )


@pytest.fixture
def collections_env(uow_fix):
    fs = {}
    file_manager = CollectionImagesManager(
        root="tests/images",
        storage=FakeStorage(fs),
    )

    return CollectionsEnv(
        uow=uow_fix,
        file_manager=file_manager,
        fs=fs,
        image_generator=FakeImageGenerator(),
    )
