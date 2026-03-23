import logging

import pytest

from domain import *
from services.tile import delete_tile, update_tile
from tests.conftest import domain_handbooks_models_for_products
from tests.fakes import FakeUoW, FakeImageGenerator
from .conftest import products_env, products_env_with_handbooks
from .helpers import product_catalog_path, product_details_path
from tests.helpers import add_tile_helper, assert_size, assert_box, assert_tile_fields, assert_handbooks_count, update_filters

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_tile_success_when_all_handbooks_exists(
    products_env_with_handbooks, domain_handbooks_models_for_products
):
    manager, file_manager, fs = products_env_with_handbooks
    record = await add_tile_helper(manager, file_manager, FakeImageGenerator())
    log.debug("tile: %s", record)
    assert record is not None
    assert "id" in record
    tile_id = record["id"]

    # # проверка всех справочников
    await assert_handbooks_count(manager, domain_handbooks_models_for_products, 1)

    images_table = await manager.read(TileImages, tile_id=tile_id)
    assert len(images_table) == 3


@pytest.mark.asyncio
async def test_expected_file_paths_exists_after_success_created(products_env_with_handbooks):
    manager, file_manager, fs = products_env_with_handbooks
    record = await add_tile_helper(manager, file_manager, FakeImageGenerator())
    paths_funcs = (
        file_manager.base_product_path,
        product_catalog_path(file_manager),
        product_details_path(file_manager),
    )
    tile_id = record["id"]
    file_names = (f"{tile_id}-0", f"{tile_id}-1", f"{tile_id}-2")
    expected_paths = [
        str(func(file_name)) for func in paths_funcs for file_name in file_names
    ]
    assert set(fs) == set(expected_paths)

    assert fs[expected_paths[0]] == b"MAIN"
    assert fs[expected_paths[1]] == b"A"
    assert fs[expected_paths[2]] == b"B"



@pytest.mark.asyncio
async def test_create_tile_success_when_all_handbooks_not_exists(
    products_env, domain_handbooks_models_for_products
):
    manager, file_manager, fs = products_env
    record = await add_tile_helper(manager, file_manager, FakeImageGenerator())

    # 1. Tile создан
    assert record is not None
    assert "id" in record

    # проверка всех справочников
    await assert_handbooks_count(manager, domain_handbooks_models_for_products, 1)

    images_table = await manager.read(TileImages)
    assert len(images_table) == 3


@pytest.mark.asyncio
async def test_update_tile_success_when_new_attributes_in_handbooks(
    products_env_with_handbooks, domain_handbooks_models_for_products
):
    manager, file_manager, fs = products_env_with_handbooks
    record = await add_tile_helper(manager, file_manager, FakeImageGenerator())

    log.debug("old_tile: %s", record)
    article = record["id"]  # фильтр для обновления по артикулу

    new_filters = update_filters()
    await update_tile(manager, article, uow_class=FakeUoW, **new_filters)

    new_tile = (await manager.read(Tile, id=article))[0]
    expected_box, expected_size, color = new_filters.pop("box"), new_filters.pop("size"), new_filters.pop("color")
    new_filters["color_name"], new_filters["feature_name"] = color["color_name"], color["feature_name"]
    box = (await manager.read(Box, id=new_tile["box_id"]))[0]
    size = (await manager.read(TileSize, id=new_tile["size_id"]))[0]

    # 1 проверка всех новых полей с помощью функций, в которых вынесена логика assert
    assert_size(size, expected_size)
    assert_box(box, expected_box)
    assert_tile_fields(new_tile, new_filters)

    # 2. Проверка всех справочников, поля в справочниках не должны изменятся, а должны появится новые
    await assert_handbooks_count(manager, domain_handbooks_models_for_products, 2)



@pytest.mark.asyncio
async def test_delete_tile_by_article(products_env, domain_handbooks_models_for_products):
    manager, file_manager, fs = products_env
    record = await add_tile_helper(manager, file_manager, FakeImageGenerator())
    tile_id = record["id"]
    records = await delete_tile(
        manager, uow_class=FakeUoW, id=tile_id, file_manager=file_manager
    )
    assert len(records) == 1
    # здесь не тестирую удаление в базе, т.к для чтения в этой базе нужен join с images, а в unit тестах я отказался от реализации join в фейке базы данных

    for i in records:
        assert i["id"] == tile_id

    new_records = await manager.read(Tile, id=tile_id)
    assert not new_records
    await assert_handbooks_count(manager, domain_handbooks_models_for_products, 1)

