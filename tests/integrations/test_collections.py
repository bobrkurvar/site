import logging

import pytest

from domain import (
    AlreadyExistsError,
    Collection,
    CollectionCategory,
    NotFoundError,
    Slug,
)
from services.collections import delete_collection
from tests.fakes import FakeImageGenerator
from tests.helpers import add_collection_helper

from .helpers import collection_files_count

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_collection_category_when_collection_not_exists_success(
    collections_env_with_categories,
):
    # когда создаётся раздел коллекции-категории, но нет коллекции в таблице коллекций, создаётся коллекция
    manager, file_manager, categories = await collections_env_with_categories()
    category_name = categories[0]
    collection = await add_collection_helper(
        manager=manager,
        file_manager=file_manager,
        images_generator=FakeImageGenerator(),
        category_name=category_name,
        test_uow_class=False,
    )
    # сервисная функция должна вернуть запись
    assert collection is not None
    collection_in_db = await manager.read(Collection, name=collection.name)
    collection_category = await manager.read(
        CollectionCategory, collection_id=collection.id
    )
    slug = await manager.read(Slug, name=collection.name)
    # действительно в базе есть запись коллекции, запись коллекции-категории, запись slug коллекции
    assert (
        len(collection_in_db) == 1 and len(collection_category) == 1 and len(slug) == 1
    )
    # создались файлы изображений
    assert collection_files_count(file_manager) == 2


@pytest.mark.asyncio
async def test_create_collection_category_when_collection_exists_success(
    collections_env_with_categories,
):
    # когда создаётся раздел коллекции-категории и коллекция в таблице коллекций есть, коллекция не создаётся
    manager, file_manager, categories = await collections_env_with_categories(2)
    collection = None
    for category_name in categories:
        collection = await add_collection_helper(
            manager=manager,
            file_manager=file_manager,
            images_generator=FakeImageGenerator(),
            category_name=category_name,
            test_uow_class=False,
        )
    collection_in_db = await manager.read(
        Collection, name=collection.name, loaded="categories"
    )
    slug = await manager.read(Slug, name=collection.name)
    collection_category = await manager.read(
        CollectionCategory, collection_id=collection.id
    )
    # действительно в базе есть запись одной коллекции, создались две записи коллекция-категория, slug одной коллекции
    assert (
        len(collection_in_db) == 1
        and len(collection_category) == len(collection_in_db[0].categories) == 2
        and len(slug) == 1
    )


@pytest.mark.asyncio
async def test_create_collection_category_idempotency(
    collections_env_with_categories,
):
    # Проверяем, что повторное добавление одной и той же категории не плодит сущности и не падает
    manager, file_manager, categories = await collections_env_with_categories()

    # Добавляем первый раз
    collection = await add_collection_helper(
        manager=manager,
        file_manager=file_manager,
        images_generator=FakeImageGenerator(),
        category_name=categories[0],
        test_uow_class=False,
    )

    # Добавляем ТОЙ ЖЕ коллекции ТУ ЖЕ категорию второй раз
    await add_collection_helper(
        manager=manager,
        file_manager=file_manager,
        images_generator=FakeImageGenerator(),
        category_name=categories[0],
        test_uow_class=False,
    )

    collection_category = await manager.read(
        CollectionCategory, collection_id=collection.id
    )

    # Проверяем, что в базе по-прежнему ровно ОДНА запись связи (дубликат не создался)
    assert len(collection_category) == 1
    # И файлы не перезаписались лишний раз (или их количество осталось корректным)
    assert collection_files_count(file_manager) == 2


@pytest.mark.asyncio
async def test_create_collection_category_when_collection_not_exists_failure(
    collections_env_with_categories,
):
    # когда создаётся раздел коллекции-категории и коллекция в таблице коллекций есть, коллекция не создаётся
    manager, file_manager, categories = await collections_env_with_categories()
    category_name, collection_name = categories[0], "collection1"
    # заранее создаю slug что бы при создании коллекции вылетело исключение посреди транзакции
    await manager.create(Slug(name=collection_name, slug=collection_name))
    with pytest.raises(AlreadyExistsError):
        await add_collection_helper(
            manager=manager,
            file_manager=file_manager,
            images_generator=FakeImageGenerator(),
            category_name=category_name,
            collection_name=collection_name,
            test_uow_class=False,
        )
    collections = await manager.read(Collection)
    collection_category = await manager.read(CollectionCategory)
    assert collection_files_count(file_manager) == 0
    assert len(collections) == 0 and len(collection_category) == 0


@pytest.mark.asyncio
async def test_delete_collection_success(collections_env_with_categories):
    manager, file_manager, categories = await collections_env_with_categories(1)
    category_name = categories[0]
    collection = await add_collection_helper(
        manager=manager,
        file_manager=file_manager,
        images_generator=FakeImageGenerator(),
        category_name=category_name,
        test_uow_class=False,
    )
    await delete_collection(
        collection_name="collection1",
        manager=manager,
        file_manager=file_manager,
    )
    collection_in_db = await manager.read(Collection, name=collection.name)
    slug = await manager.read(Slug, name=collection.name)
    collection_category = await manager.read(CollectionCategory)
    assert len(collection_in_db) == 0
    assert len(slug) == 0
    # здесь вместе с коллекцией каскадно удаляются и все записи вида коллекция-категория
    assert len(collection_category) == 0
    # удалились файлы изображений
    assert collection_files_count(file_manager) == 0


@pytest.mark.asyncio
async def test_delete_collection_fail(collections_env_with_categories):
    manager, file_manager, _ = await collections_env_with_categories(1)
    with pytest.raises(NotFoundError):
        await delete_collection(
            collection_name="collection1",
            manager=manager,
            file_manager=file_manager,
        )
