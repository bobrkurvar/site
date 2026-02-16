import logging

import pytest

import core.logger
from adapters.images import (CollectionImagesManager,
                             generate_image_collections_catalog)
from domain import (AlreadyExistsError, CollectionCategory, Collections,
                    NotFoundError, Slug)
from services.collections import add_collection, delete_collection

from .conftest import manager, manager_with_categories
from .helpers import collection_files_count, create_fake_image

log = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_collection_category_when_collection_not_exists_success(
    manager_with_categories,
):
    # когда создаётся раздел коллекции-категории, но нет коллекции в таблице коллекций, создаётся коллекция
    file_manager = CollectionImagesManager(root="tests/images")
    collection = await add_collection(
        name="collection1",
        image=create_fake_image(),
        category_name="category1",
        manager=manager_with_categories,
        generate_images=generate_image_collections_catalog,
        file_manager=file_manager,
    )

    # сервисная функция должна вернуть запись
    assert collection is not None

    collection_in_db = await manager_with_categories.read(
        Collections, name="collection1"
    )
    collection_category = await manager_with_categories.read(
        CollectionCategory, collection_id=collection["id"]
    )
    slug = await manager_with_categories.read(Slug, name=collection["name"])
    # действительно в базе есть запись коллекции
    assert len(collection_in_db) == 1
    # действительно в базе есть запись коллекции-категории
    assert len(collection_category) == 1
    # действительно в базе есть запись slug коллекции
    assert len(slug) == 1
    # создались файлы изображений
    assert collection_files_count(file_manager) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_collection_category_when_collection_exists_success(
    manager_with_categories,
):
    # когда создаётся раздел коллекции-категории и коллекция в таблице коллекций есть, коллекция не создаётся
    file_manager = CollectionImagesManager(root="tests/images")
    collection = await add_collection(
        name="collection1",
        image=create_fake_image(),
        category_name="category1",
        manager=manager_with_categories,
        generate_images=generate_image_collections_catalog,
        file_manager=file_manager,
    )
    await add_collection(
        name="collection1",
        image=create_fake_image(),
        category_name="category2",
        manager=manager_with_categories,
        generate_images=generate_image_collections_catalog,
        file_manager=file_manager,
    )

    # сервисная функция должна вернуть запись
    assert collection is not None

    collection_in_db = await manager_with_categories.read(
        Collections, name="collection1"
    )
    slug = await manager_with_categories.read(Slug, name=collection["name"])
    collection_category = await manager_with_categories.read(
        CollectionCategory, collection_id=collection["id"]
    )
    # действительно в базе есть запись одной коллекции
    assert len(collection_in_db) == 1
    # действительно в базе создались две записи коллекция-категория
    assert len(collection_category) == 2
    # действительно в базе есть запись slug одной коллекции
    assert len(slug) == 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_collection_category_when_collection_exists_failure(
    manager_with_categories,
):
    # когда создаётся раздел коллекции-категории и коллекция в таблице коллекций есть, коллекция не создаётся
    file_manager = CollectionImagesManager(root="tests/images")
    await add_collection(
        name="collection1",
        image=create_fake_image(),
        category_name="category1",
        manager=manager_with_categories,
        generate_images=generate_image_collections_catalog,
        file_manager=file_manager,
    )
    with pytest.raises(AlreadyExistsError):
        await add_collection(
            name="collection1",
            image=create_fake_image(),
            category_name="category1",
            manager=manager_with_categories,
            generate_images=generate_image_collections_catalog,
            file_manager=file_manager,
        )
    assert collection_files_count(file_manager) == 2


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_collection_category_when_collection_not_exists_failure(
    manager_with_categories,
):
    # когда создаётся раздел коллекции-категории и коллекция в таблице коллекций есть, коллекция не создаётся
    file_manager = CollectionImagesManager(root="tests/images")
    # заранее создаю slug что бы при создании коллекции вылетело исключение посреди транзакции
    await manager_with_categories.create(Slug, name="collection1", slug="collection1")

    with pytest.raises(AlreadyExistsError):
        await add_collection(
            name="collection1",
            image=create_fake_image(),
            category_name="category1",
            manager=manager_with_categories,
            generate_images=generate_image_collections_catalog,
            file_manager=file_manager,
        )
    assert collection_files_count(file_manager) == 0
    collections = await manager_with_categories.read(Collections)
    collection_category = await manager_with_categories.read(CollectionCategory)
    assert len(collections) == 0
    assert len(collection_category) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_collection_success(manager_with_categories):
    file_manager = CollectionImagesManager(root="tests/images")
    collection = await add_collection(
        name="collection1",
        image=create_fake_image(),
        category_name="category1",
        manager=manager_with_categories,
        generate_images=generate_image_collections_catalog,
        file_manager=file_manager,
    )
    await delete_collection(
        collection_name="collection1",
        manager=manager_with_categories,
        file_manager=file_manager,
    )

    collection_in_db = await manager_with_categories.read(
        Collections, name=collection["name"]
    )
    slug = await manager_with_categories.read(Slug, name=collection["name"])
    collection_category = await manager_with_categories.read(CollectionCategory)
    assert len(collection_in_db) == 0
    assert len(slug) == 0

    # здесь вместе с коллекцией каскадно удаляются и все записи вида коллекция-категория
    assert len(collection_category) == 0
    # удалились файлы изображений
    assert collection_files_count(file_manager) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_collection_fail(manager):
    file_manager = CollectionImagesManager(root="tests/images")
    with pytest.raises(NotFoundError):
        await delete_collection(
            collection_name="collection1",
            manager=manager,
            file_manager=file_manager,
        )
