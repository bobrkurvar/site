import logging

import pytest

import core.logger
from domain import Collections, NotFoundError
from services.collections import add_collection, delete_collection
from tests.fakes import (FakeCollectionImagesManager, FakeCRUD,
                         FakeUoW, generate_collections_images)

from .helpers import collection_catalog_path

log = logging.getLogger(__name__)


@pytest.fixture
def manager_without_handbooks(storage):
    return FakeCRUD(storage)


@pytest.mark.asyncio
async def test_create_collection_success(manager_without_handbooks):
    fs = {}
    manager = manager_without_handbooks
    file_manager = FakeCollectionImagesManager(fs=fs)
    collection = await add_collection(
        name="collection1",
        image=b"MAIN",
        category_name="category1",
        manager=manager,
        uow_class=FakeUoW,
        generate_images=generate_collections_images,
        file_manager=file_manager,
    )
    collection_path_with_manager = collection_catalog_path(file_manager)
    assert collection is not None
    collection_db = await manager.read(
        Collections, name="collection1", category_name="category1"
    )
    assert len(collection_db) != 0
    name = f"{collection["name"]}"
    paths_funcs = (file_manager.base_collection_path, collection_path_with_manager)
    expected_paths = [str(func(name)) for func in paths_funcs]
    log.debug("expected_paths: %s, fs: %s", expected_paths, fs)
    assert set(fs) == set(expected_paths)
    assert fs[str(file_manager.base_collection_path(f"{name}"))] == b"MAIN"
    assert fs[str(collection_path_with_manager(f"{name}"))] == b"aaa"


@pytest.mark.asyncio
async def test_delete_collection_success(manager_without_handbooks):
    manager = manager_without_handbooks
    fs = {}
    file_manager = FakeCollectionImagesManager(fs=fs)
    await add_collection(
        name="collection1",
        image=b"MAIN",
        category_name="category1",
        manager=manager,
        uow_class=FakeUoW,
        generate_images=generate_collections_images,
        file_manager=file_manager,
    )
    collection = await manager.read(
        Collections, name="collection1", category_name="category1"
    )
    assert len(collection) != 0
    file_manager = FakeCollectionImagesManager(fs=fs)
    await delete_collection(
        collection_name="collection1",
        category_name="category1",
        manager=manager_without_handbooks,
        uow_class=FakeUoW,
        file_manager=file_manager,
    )

    collection = await manager.read(
        Collections, name="collection1", category_name="category1"
    )
    assert len(collection) == 0
    assert not fs


@pytest.mark.asyncio
async def test_delete_collection_fail(manager_without_handbooks):
    file_manager = FakeCollectionImagesManager()
    with pytest.raises(NotFoundError):
        await delete_collection(
            collection_name="collection1",
            category_name="category1",
            manager=manager_without_handbooks,
            uow_class=FakeUoW,
            file_manager=file_manager,
        )
