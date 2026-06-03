import logging
from pathlib import Path

import pytest

from domain import *
from services.tile import update_tile
from tests.conftest import domain_handbooks_models_for_products
from tests.fakes import FakeImageGenerator, FakeUoW
from tests.helpers import (add_tile_helper, assert_box, assert_handbooks_count,
                           assert_size, assert_tile_fields, update_filters)

from .helpers import product_catalog_path, product_details_path

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_tile_success_when_all_handbooks_exists(
    products_env_with_handbooks, domain_handbooks_models_for_products
):
    manager, file_manager, fs = products_env_with_handbooks
    record = await add_tile_helper(manager, file_manager, FakeImageGenerator())
    log.debug("tile: %s", record)
    # проверка всех справочников
    await assert_handbooks_count(manager, domain_handbooks_models_for_products, 1)


@pytest.mark.asyncio
async def test_expected_file_paths_exists_after_success_created(
    products_env_with_handbooks,
):
    manager, file_manager, fs = products_env_with_handbooks
    record = await add_tile_helper(manager, file_manager, FakeImageGenerator())
    paths_funcs = (
        file_manager.base_product_path,
        product_catalog_path(file_manager),
        product_details_path(file_manager),
    )
    assert len(fs) == 9
    for img in record.images:
        file_name = Path(img.image_path).name
        for func in paths_funcs:
            expected_path = Path(func(file_name)).as_posix()
            assert (
                expected_path in fs
            ), f"Файл не найден по ожидаемому пути: {expected_path}"


@pytest.mark.asyncio
async def test_update_tile_success_when_new_attributes_in_handbooks(
    products_env_with_handbooks, domain_handbooks_models_for_products
):
    manager, file_manager, fs = products_env_with_handbooks
    record = await add_tile_helper(manager, file_manager, FakeImageGenerator())

    log.debug("old_tile: %s", record)
    article = record.id  # фильтр для обновления по артикулу

    new_filters = update_filters()
    await update_tile(
        manager=manager, article=article, uow_class=FakeUoW, **new_filters
    )

    new_tile = await manager.read_one(Tile, id=article)
    expected_box, expected_size, color = (
        new_filters.pop("box"),
        new_filters.pop("size"),
        new_filters.pop("color"),
    )
    new_filters["color_name"], new_filters["feature_name"] = (
        color["color_name"],
        color["feature_name"],
    )
    box = await manager.read_one(Box, id=new_tile.box.id)
    size = await manager.read_one(TileSize, id=new_tile.size.id)

    # 1 проверка всех новых полей с помощью функций, в которых вынесена логика assert
    assert_size(size, expected_size)
    assert_box(box, expected_box)
    assert_tile_fields(new_tile, new_filters)

    # 2. Проверка всех справочников, поля в справочниках не должны изменятся, а должны появится новые
    await assert_handbooks_count(manager, domain_handbooks_models_for_products, 2)
