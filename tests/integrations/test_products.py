import logging

import pytest

from tests.fakes import FakeImageGenerator
from domain import Tile, TileImages, TileSize, Box
from services.exceptions import ImageProcessingError
from services.tile import delete_tile, update_tile
from tests.conftest import domain_handbooks_models_for_products

#from .conftest import products_env_with_handbooks, products_env
from .helpers import product_files_count
from tests.helpers import add_tile_helper, assert_handbooks_count, assert_size, assert_box, assert_tile_fields, update_filters

log = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tile_success_when_handbooks_not_exists(
    domain_handbooks_models_for_products, products_env_with_handbooks
):
    manager, file_manager = products_env_with_handbooks
    record = await add_tile_helper(manager, file_manager, FakeImageGenerator(), test_uow_class=False)
    # Tile создан
    assert record is not None
    tile_id = record["id"]
    # проверка всех справочников
    await assert_handbooks_count(manager, domain_handbooks_models_for_products, 1)
    images = await manager.read(TileImages, tile_id=tile_id)
    assert len(images) == 3
    assert product_files_count(file_manager) == 9


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tile_failure(products_env, domain_handbooks_models_for_products):
    manager, file_manager = products_env
    class FakeGenerator:
        async def products_catalog_and_details(*args, **kwargs):
            raise ImageProcessingError

    with pytest.raises(ImageProcessingError):
        await add_tile_helper(manager, file_manager, FakeGenerator(), test_uow_class=False)

    domain_handbooks_models_for_products += (Tile, TileImages)
    await assert_handbooks_count(manager, domain_handbooks_models_for_products, 0)
    assert product_files_count(file_manager) == 0


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_tile_success_when_new_attributes_in_handbooks(
    domain_handbooks_models_for_products, products_env
):
    manager, file_manager = products_env
    record = await add_tile_helper(manager, file_manager, FakeImageGenerator(), test_uow_class=False)
    article = record["id"]  # фильтр для обновления по артикулу

    # новые данные
    new_filters = update_filters()
    await update_tile(manager, article, **new_filters)

    expected_box, expected_size, color = new_filters.pop("box"), new_filters.pop("size"), new_filters.pop("color")
    new_filters["color_name"], new_filters["feature_name"] = color["color_name"], color["feature_name"]
    new_tile = (await manager.read(Tile, id=article))[0]
    box = (await manager.read(Box, id=new_tile["box_id"]))[0]
    size = (await manager.read(TileSize, id=new_tile["size_id"]))[0]
    # 1 проверка всех новых полей с помощью функций, в которых вынесена логика assert
    assert_size(size, expected_size)
    assert_box(box, expected_box)
    assert_tile_fields(new_tile, new_filters)
    # 2. Проверка всех справочников, поля в справочниках не должны изменятся, а должны появится новые
    await assert_handbooks_count(manager, domain_handbooks_models_for_products, 2)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_tile_success_when_composite_half_composite_color_name_box_weight_param(
    products_env_with_handbooks, domain_handbooks_models_for_products
):
    manager, file_manager = products_env_with_handbooks
    record, params = await add_tile_helper(manager, file_manager, FakeImageGenerator(), test_uow_class=False, need_params=True)
    # получил также параметры создания, что бы получить часть композитного ключа без join read иначе из add_tile связанные данные box_area не подтянется
    article = record["id"]  # фильтр для обновления по артикулу
    # новые данные color_feature и box_area остаются старыми
    new_filters = update_filters(feature_name_missing=True, area_missing=True)
    old_color_feature, old_box_area = record["feature_name"], params["box_area"]
    await update_tile(manager, article, **new_filters)
    new_tile = (await manager.read(Tile, id=article))[0]
    # половины композитного ключа берутся из той же записи продукта
    expected_box, expected_size = dict(**new_filters.pop("box"), area=old_box_area), new_filters.pop("size")
    new_filters["color_name"], new_filters["feature_name"] = new_tile["color_name"], record["feature_name"]
    del new_filters["color"]
    box = (await manager.read(Box, id=new_tile["box_id"]))[0]
    size = (await manager.read(TileSize, id=new_tile["size_id"]))[0]

    assert_size(size, expected_size)
    assert_box(box, expected_box)
    # 1 проверка всех новых полей
    assert_tile_fields(new_tile, new_filters)
    # 2. Проверка всех справочников, поля в справочниках не должны изменятся, а должны появится новые
    await assert_handbooks_count(manager, domain_handbooks_models_for_products, 2)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_tile_success_when_input_composite_length_area_feature(
    products_env_with_handbooks, domain_handbooks_models_for_products
):
    manager, file_manager = products_env_with_handbooks
    record, params = await add_tile_helper(manager, file_manager, FakeImageGenerator(), test_uow_class=False, need_params=True)
    # получил также параметры создания, что бы получить часть композитного ключа без join read иначе из add_tile связанные данные box_area не подтянется
    article = record["id"]  # фильтр для обновления по артикулу
    # меняются только size_length, box_area, color_feature
    new_filters = update_filters(color_name_missing=True, weight_missing=True, width_missing=True, height_missing=True)
    old_color_name, old_box_weight, old_width, old_height = record["color_name"], params["box_weight"], params["width"], params["height"]
    await update_tile(manager, article, **new_filters)
    new_tile = (await manager.read(Tile, id=article))[0]
    # половины композитного ключа берутся из той же записи продукта
    expected_box, expected_size = dict(**new_filters.pop("box"), weight=old_box_weight), dict(**new_filters.pop("size"), width=old_width, height=old_height)
    new_filters["color_name"], new_filters["feature_name"] = record["color_name"], new_tile["feature_name"]
    del new_filters["color"]
    box = (await manager.read(Box, id=new_tile["box_id"]))[0]
    size = (await manager.read(TileSize, id=new_tile["size_id"]))[0]

    assert_size(size, expected_size)
    assert_box(box, expected_box)
    # 1 проверка всех новых полей
    assert_tile_fields(new_tile, new_filters)
    # 2. Проверка всех справочников, поля в справочниках не должны изменятся, а должны появится новые
    await assert_handbooks_count(manager, domain_handbooks_models_for_products, 2)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_tile_by_article(products_env_with_handbooks, domain_handbooks_models_for_products):
    manager, file_manager = products_env_with_handbooks
    record = await add_tile_helper(manager, file_manager, FakeImageGenerator(), test_uow_class=False)
    article = record["id"]
    records = await delete_tile(
        manager, id=article, file_manager=file_manager
    )
    assert len(records) == 1
    for i in records:
        assert i["id"] == article
    new_records = await manager.read(Tile, id=article)
    assert not new_records
    # При удалении продукта записи в связанных справочника не должны удаляться
    await assert_handbooks_count(manager, domain_handbooks_models_for_products, 1)
    # изображение должно каскадно удалиться
    images = await manager.read(TileImages)
    assert len(images) == 0
    # файлы изображений удалились
    assert product_files_count(file_manager) == 0
