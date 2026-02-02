import logging

import pytest
from pathlib import Path

import core.logger
from services.collections import add_collection, delete_collection
from domain.tile import Collections

from tests.fakes import FakeUoW, FakeCRUD, FakeCrudError
from tests.fakes import FakeFileManager, get_fake_save_bg_collections_with_fs

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
        generate_image_variant_callback=get_fake_save_bg_collections_with_fs(fs),
        file_manager=file_manager
    )

    assert collection is not None
    collection_db = await manager.read(Collections, name='collection1', category_name='category1')
    assert len(collection_db) != 0
    name = f"{collection["name"]}-{collection["category_name"]}"
    expected_paths = [
        str(Path(f"static/images/base/collections/{name}")),
        str(Path(f"static/images/collections/catalog/{name}"))
    ]
    assert set(fs) == set(expected_paths)
    assert fs[str(Path(f"static/images/base/collections/{name}"))] == b"MAIN"
    assert fs[str(Path(f"static/images/collections/catalog/{name}"))] == ""



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
        generate_image_variant_callback=get_fake_save_bg_collections_with_fs(fs),
        file_manager=file_manager
    )
    collection = await manager.read(Collections, name='collection1', category_name='category1')
    assert len(collection) != 0
    file_manager = FakeFileManager(fs=fs)
    await delete_collection(
        name="collection1",
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
            name="collection1",
            category_name="category1",
            manager=manager_without_handbooks,
            uow_class=FakeUoW,
            file_manager=file_manager
        )

