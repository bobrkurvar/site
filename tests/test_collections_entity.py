import logging

import pytest
from pathlib import Path

import core.logger
from services.collections import add_collection, delete_collection
from domain.tile import Collections

from .fakes import FakeUoW, FakeCRUD, FakeCrudError
from .fakes import get_fake_save_files_function_with_fs, get_fake_delete_files_function_with_fs, get_fake_save_bg_collections_with_fs
from .conftest import noop

log = logging.getLogger(__name__)



@pytest.fixture
def manager_without_handbooks(storage):
    return FakeCRUD(storage)


@pytest.mark.asyncio
async def test_create_collection_success(manager_without_handbooks):
    fs = {}
    manager = manager_without_handbooks
    collection = await add_collection(
        name="collection1",
        image=b"MAIN",
        category_name="category1",
        manager=manager,
        uow_class=FakeUoW,
        generate_image_variant_callback=get_fake_save_bg_collections_with_fs(fs),
        save_files=get_fake_save_files_function_with_fs(fs)
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
async def test_create_collection_fail(manager_without_handbooks):
    fs = {}
    await add_collection(
        name="collection1",
        image=b"MAIN",
        category_name="category1",
        manager=manager_without_handbooks,
        uow_class=FakeUoW,
        generate_image_variant_callback=noop,
        save_files=get_fake_save_files_function_with_fs(fs)
    )

    with pytest.raises(FakeCrudError):
         await add_collection(
            name="collection1",
            image=b"NEWMAIN",
            category_name="category1",
            manager=manager_without_handbooks,
            uow_class=FakeUoW,
            generate_image_variant_callback=noop,
            save_files=get_fake_save_files_function_with_fs(fs)
        )
    expected_path = str(Path(f'static/images/base/collections/collection1-category1'))
    assert fs[expected_path] == b'MAIN'

@pytest.mark.asyncio
async def test_delete_collection_success(manager_without_handbooks):
    manager = manager_without_handbooks
    fs = {}
    await add_collection(
        name="collection1",
        image=b"MAIN",
        category_name="category1",
        manager=manager,
        uow_class=FakeUoW,
        generate_image_variant_callback=get_fake_save_bg_collections_with_fs(fs),
        save_files=get_fake_save_files_function_with_fs(fs)
    )
    collection = await manager.read(Collections, name='collection1', category_name='category1')
    assert len(collection) != 0

    await delete_collection(
        name="collection1",
        category_name="category1",
        manager=manager_without_handbooks,
        uow_class=FakeUoW,
        delete_files=get_fake_delete_files_function_with_fs(fs)
    )

    collection = await manager.read(Collections, name='collection1', category_name='category1')
    assert len(collection) == 0
    assert not fs

@pytest.mark.asyncio
async def test_delete_collection_fail(manager_without_handbooks):
    with pytest.raises(FakeCrudError):
         await delete_collection(
            name="collection1",
            category_name="category1",
            manager=manager_without_handbooks,
            uow_class=FakeUoW,
            delete_files=lambda x: None
        )

