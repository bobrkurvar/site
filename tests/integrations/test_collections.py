import logging
import pytest

from domain import (
    AlreadyExistsError,
    Collection,
    CollectionCategory,
    NotFoundError,
)
from services.collections import delete_collection
from tests.helpers import add_collection_helper
from .helpers import collection_files_count

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_collection_and_category_relation_when_collection_not_exists(
    collections_env_with_categories,
):
    env, categories = collections_env_with_categories
    category_name = categories[0]
    collection = await add_collection_helper(
        uow=env.uow,
        file_manager=env.file_manager,
        images_generator=env.images_generator,
        category_name=category_name,
    )
    # сервисная функция должна вернуть запись
    assert collection is not None
    async with env.uow as uow:
        collection_in_db = await uow.db.read(Collection, name=collection.name)
        collection_category = await uow.db.read(
            CollectionCategory, collection_id=collection.id
        )
    assert len(collection_in_db) == 1 and len(collection_category) == 1
    # создались файлы изображений
    assert collection_files_count(env.file_manager) == 2


@pytest.mark.asyncio
async def test_create_collection_category_when_collection_exists_success(
    collections_env_with_categories,
):
    # когда создаётся раздел коллекции-категории и коллекция в таблице коллекций есть, коллекция не создаётся
    env, categories = await collections_env_with_categories(2)
    collection = None
    for category_name in categories:
        collection = await add_collection_helper(
            uow=env.uow,
            file_manager=env.file_manager,
            images_generator=env.images_generator,
            category_name=category_name,
        )
    async with env.uow as uow:
        collection_in_db = await uow.db.read(
            Collection, name=collection.name, loaded="categories"
        )
        collection_category = await uow.db.read(
            CollectionCategory, collection_id=collection.id
        )
    # действительно в базе есть запись одной коллекции, создались две записи коллекция-категория
    assert (
        len(collection_in_db) == 1
        and len(collection_category) == len(collection_in_db[0].categories) == 2
    )


@pytest.mark.asyncio
async def test_create_collection_category_idempotency(collections_env_with_categories):
    env, categories = await collections_env_with_categories()

    # Добавляем первый раз
    collection = await add_collection_helper(
        uow=env.uow,
        file_manager=env.file_manager,
        images_generator=env.images_generator,
        category_name=categories[0],
    )

    # Добавляем ТОЙ ЖЕ коллекции ТУ ЖЕ категорию второй раз
    await add_collection_helper(
        uow=env.uow,
        file_manager=env.file_manager,
        images_generator=env.images_generator,
        category_name=categories[0],
    )
    async with env.uow as uow:
        collection_category = await uow.db.read(
            CollectionCategory, collection_id=collection.id
        )

    # Проверяем, что в базе по-прежнему ровно ОДНА запись связи (дубликат не создался)
    assert len(collection_category) == 1
    # И файлы не перезаписались лишний раз (или их количество осталось корректным)
    assert collection_files_count(env.file_manager) == 2


@pytest.mark.asyncio
async def test_delete_collection_success(collections_env_with_categories):
    env, categories = await collections_env_with_categories(1)
    category_name = categories[0]
    collection = await add_collection_helper(
        uow=env.uow,
        file_manager=env.file_manager,
        images_generator=env.images_generator,
        category_name=category_name,
    )
    await delete_collection(
        collection_name="collection1",
        uow=env.uow,
        file_manager=env.file_manager,
    )
    async with env.uow as uow:
        collection_in_db = await uow.db.read(Collection, name=collection.name)
        collection_category = await uow.db.read(CollectionCategory)
    assert len(collection_in_db) == 0
    # здесь вместе с коллекцией каскадно удаляются и все записи вида коллекция-категория
    assert len(collection_category) == 0
    # удалились файлы изображений
    assert collection_files_count(env.file_manager) == 0


@pytest.mark.asyncio
async def test_delete_collection_fail(collections_env_with_categories):
    env, _ = await collections_env_with_categories(1)
    with pytest.raises(NotFoundError):
        await delete_collection(
            collection_name="collection1",
            uow=env.uow,
            file_manager=env.file_manager,
        )
