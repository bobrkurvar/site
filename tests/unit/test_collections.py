import logging

import pytest

from domain import CollectionCategory, Collections, NotFoundError, Slug
from services.collections import delete_collection
from tests.fakes import FakeUoW, FakeImageGenerator
from .helpers import collection_catalog_path
from .conftest import collection_env
from tests.helpers import add_collection_helper

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_collection_category_when_collection_not_exists_success(collection_env):
    # когда создаётся раздел коллекции-категории, но нет коллекции в таблице коллекций, создаётся коллекция
    manager, file_manager, fs = collection_env
    collection = await add_collection_helper(manager, file_manager, FakeImageGenerator())
    # сервисная функция должна вернуть запись
    assert collection is not None
    collection_in_db = await manager.read(Collections, name="collection1")
    collection_category = await manager.read(
        CollectionCategory, collection_id=collection["id"]
    )
    slug = await manager.read(Slug, name=collection["name"])
    # действительно в базе есть запись коллекции
    assert len(collection_in_db) == 1
    # действительно в базе есть запись коллекции-категории
    assert len(collection_category) == 1
    # действительно в базе есть запись slug коллекции
    assert len(slug) == 1


@pytest.mark.asyncio
async def test_file_exists_when_create_new_collection(collection_env):
    manager, file_manager, fs = collection_env
    collection = await add_collection_helper(manager, file_manager, FakeImageGenerator())
    collection_path_with_manager = collection_catalog_path(file_manager)
    file_name = str(collection["id"])
    paths_funcs = (file_manager.base_collection_path, collection_path_with_manager)
    expected_paths = [str(func(file_name)) for func in paths_funcs]
    log.debug("expected_paths: %s, fs: %s", expected_paths, fs)
    assert set(fs) == set(expected_paths)
    assert fs[str(file_manager.base_collection_path(file_name))] == b"MAIN"
    assert fs[str(collection_path_with_manager(file_name))] == b"aaa"


@pytest.mark.asyncio
async def test_create_collection_category_when_collection_exists_success(collection_env):
    # когда создаётся раздел коллекции-категории и коллекция в таблице коллекций есть, коллекция не создаётся
    manager, file_manager, fs = collection_env
    collection = await add_collection_helper(manager, file_manager, FakeImageGenerator())
    await add_collection_helper(manager, file_manager, FakeImageGenerator())
    collection_in_db = await manager.read(Collections, name="collection1")
    slug = await manager.read(Slug, name=collection["name"])
    collection_category = await manager.read(
        CollectionCategory, collection_id=collection["id"]
    )

    # действительно в базе есть запись одной коллекции
    assert len(collection_in_db) == 1
    # действительно в базе создались две записи коллекция-категория
    assert len(collection_category) == 2
    # действительно в базе есть запись slug одной коллекции
    assert len(slug) == 1
    # в файловой системе два изображения, а не 4, так как коллекция одна и та же только в разных категориях
    assert len(fs) == 2


@pytest.mark.asyncio
async def test_delete_collection_success(collection_env):
    manager, file_manager, fs = collection_env
    collection = await add_collection_helper(manager, file_manager, FakeImageGenerator())
    await delete_collection(
        collection_name=collection["name"],
        manager=manager,
        uow_class=FakeUoW,
        file_manager=file_manager,
    )

    collection_in_db = await manager.read(Collections, name=collection["name"])
    slug = await manager.read(Slug, name=collection["name"])
    # так как в отличие от tile коллекция содержит одно изображение оно хранится вместе с ней, поэтому можно проверить её удаление без join
    assert len(collection_in_db) == 0
    assert len(slug) == 0
    assert not fs


@pytest.mark.asyncio
async def test_delete_collection_fail(collection_env):
    manager, file_manager, _ = collection_env
    with pytest.raises(NotFoundError):
        await delete_collection(
            collection_name="collection1",
            manager=manager,
            uow_class=FakeUoW,
            file_manager=file_manager,
        )
