import logging

import pytest

import core.logger
from services.collections import add_collection, delete_collection
from domain.tile import Collections

from tests.fakes import FakeUoW, FakeCRUD, FakeCrudError
from tests.fakes import FakeFileManager, generate_collections_images

log = logging.getLogger(__name__)



@pytest.fixture
def manager_without_handbooks(storage):
    return FakeCRUD(storage)


@pytest.mark.asyncio
async def test_create_collection_success(manager_without_handbooks):
    fs = {}
    manager = manager_without_handbooks
    file_manager = FakeFileManager(fs=fs)
    collection = await add_collection(
        name="collection1",
        image=b"MAIN",
        category_name="category1",
        manager=manager,
        uow_class=FakeUoW,
        generate_images=generate_collections_images,
        file_manager=file_manager
    )

    assert collection is not None
    collection_db = await manager.read(Collections, name='collection1', category_name='category1')
    assert len(collection_db) != 0
    name = f"{collection["name"]}-{collection["category_name"]}"
    # expected_paths = [
    #     str(file_manager.resolve_path(name)),
    #     str(file_manager.resolve_path(name))
    # ]
    paths_funcs = (file_manager.base_collection_path, file_manager.collection_catalog_path)
    expected_paths = [str(func(name)) for func in paths_funcs]
    log.debug("expected_paths: %s, fs: %s", expected_paths, fs)
    assert set(fs) == set(expected_paths)
    assert fs[str(file_manager.base_collection_path(f"{name}"))] == b"MAIN"
    assert fs[str(file_manager.collection_catalog_path(f"{name}"))] == b"aaa"



@pytest.mark.asyncio
async def test_delete_collection_success(manager_without_handbooks):
    manager = manager_without_handbooks
    fs = {}
    file_manager = FakeFileManager(fs=fs)
    await add_collection(
        name="collection1",
        image=b"MAIN",
        category_name="category1",
        manager=manager,
        uow_class=FakeUoW,
        generate_images=generate_collections_images,
        file_manager=file_manager
    )
    collection = await manager.read(Collections, name='collection1', category_name='category1')
    assert len(collection) != 0
    file_manager = FakeFileManager(fs=fs)
    await delete_collection(
        collection_name="collection1",
        category_name="category1",
        manager=manager_without_handbooks,
        uow_class=FakeUoW,
        file_manager=file_manager
    )

    collection = await manager.read(Collections, name='collection1', category_name='category1')
    assert len(collection) == 0
    assert not fs

@pytest.mark.asyncio
async def test_delete_collection_fail(manager_without_handbooks):
    file_manager = FakeFileManager()
    with pytest.raises(FakeCrudError):
         await delete_collection(
            collection_name="collection1",
            category_name="category1",
            manager=manager_without_handbooks,
            uow_class=FakeUoW,
            file_manager=file_manager
        )

