import logging

import pytest

import core.logger
from domain import CollectionCategory, Collections, NotFoundError, Slug
from services.collections import add_collection, delete_collection
from tests.fakes import (FakeCollectionImagesManager, FakeUoW,
                         generate_collections_images)

from .conftest import manager
from .helpers import collection_catalog_path

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_collection_category_when_collection_not_exists_success(manager):
    # когда создаётся раздел коллекции-категории, но нет коллекции в таблице коллекций, создаётся коллекция
    fs = {}
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

    coll_id = str(collection["id"])
    paths_funcs = (file_manager.base_collection_path, collection_path_with_manager)
    expected_paths = [str(func(coll_id)) for func in paths_funcs]
    log.debug("expected_paths: %s, fs: %s", expected_paths, fs)
    assert set(fs) == set(expected_paths)
    assert fs[str(file_manager.base_collection_path(f"{coll_id}"))] == b"MAIN"
    assert fs[str(collection_path_with_manager(f"{coll_id}"))] == b"aaa"


@pytest.mark.asyncio
async def test_create_collection_category_when_collection_exists_success(manager):
    # когда создаётся раздел коллекции-категории и коллекция в таблице коллекций есть, коллекция не создаётся
    fs = {}
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
    await add_collection(
        name="collection1",
        image=b"MAIN",
        category_name="category2",
        manager=manager,
        uow_class=FakeUoW,
        generate_images=generate_collections_images,
        file_manager=file_manager,
    )

    # сервисная функция должна вернуть запись
    assert collection is not None

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
    log.debug("FS: %s:", fs)
    # в файловой системе два изображения, а не 4, так как коллекция одна и та же только в разных категориях
    assert len(fs) == 2


@pytest.mark.asyncio
async def test_delete_collection_success(manager):
    fs = {}
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
    await delete_collection(
        collection_name="collection1",
        manager=manager,
        uow_class=FakeUoW,
        file_manager=file_manager,
    )

    collection_in_db = await manager.read(Collections, name=collection["name"])
    slug = await manager.read(Slug, name=collection["name"])
    assert len(collection_in_db) == 0
    assert len(slug) == 0
    assert not fs


@pytest.mark.asyncio
async def test_delete_collection_fail(manager):
    file_manager = FakeCollectionImagesManager()
    with pytest.raises(NotFoundError):
        await delete_collection(
            collection_name="collection1",
            manager=manager,
            uow_class=FakeUoW,
            file_manager=file_manager,
        )
