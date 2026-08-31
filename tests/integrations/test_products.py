import logging

import pytest

from domain import Box, Image, Tile, TileSize
from services.exceptions import ImageProcessingError
from services.tile import delete_tile, update_tile, add_tile
from tests.helpers import (
    assert_box,
    assert_handbooks_count,
    assert_size,
    assert_tile_fields,
    update_filters,
)

from .helpers import product_files_count

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_tile_success_when_all_handbooks_exists(
    products_env_with_handbooks, domain_handbooks_models_for_products, tile
):
    """
    Product_env_with_handbooks создаёт по одному справочнику, тест проверяет что при создании новых товарных позиций
    с использованием существующих справочных данных не создаются новые
    """
    env = products_env_with_handbooks
    record = await add_tile(
        tile=tile,
        uow=env.uow,
        file_manager=env.file_manager,
        images_generator=env.images_generator,
    )
    log.debug("tile: %s", record)
    # проверка всех справочников
    await assert_handbooks_count(env.uow.db, domain_handbooks_models_for_products, 1)


@pytest.mark.asyncio
async def test_create_tile_success_when_handbooks_not_exists(
    domain_handbooks_models_for_products, products_env, tile
):
    env = products_env
    record = await add_tile(
        tile=tile,
        file_manager=env.file_manager,
        uow=env.uow,
        images_generator=env.images_generator,
    )
    # Tile создан
    assert record is not None
    tile_id = record.id
    # проверка всех справочников
    await assert_handbooks_count(env.uow.db, domain_handbooks_models_for_products, 1)
    async with env.uow:
        images = await env.uow.db.read(Image, tile_id=tile_id)
    assert len(images) == 3
    assert product_files_count(env.file_manager) == 9


@pytest.mark.asyncio
async def test_create_tile_failure(
    products_env, domain_handbooks_models_for_products, tile
):
    env = products_env

    class FakeGenerator:
        async def generate_product_variants(*args, **kwargs):
            raise ImageProcessingError

    with pytest.raises(ImageProcessingError):
        await add_tile(
            tile=tile,
            uow=env.uow,
            file_manager=env.file_manager,
            images_generator=FakeGenerator(),
        )

    domain_handbooks_models_for_products += (Tile, Image)
    await assert_handbooks_count(env.uow.db, domain_handbooks_models_for_products, 0)
    assert product_files_count(env.file_manager) == 0


@pytest.mark.asyncio
async def test_update_tile_success_when_new_attributes_in_handbooks(
    products_env_with_handbooks, domain_handbooks_models_for_products, tile
):
    env = products_env_with_handbooks
    uow = env.uow
    record = await add_tile(
        tile=tile,
        uow=env.uow,
        file_manager=env.file_manager,
        images_generator=env.images_generator,
    )

    log.debug("old_tile: %s", record)
    article = record.id  # фильтр для обновления по артикулу

    new_filters = update_filters()
    await update_tile(uow=uow, article=article, **new_filters)

    new_tile = await uow.db.read_one(Tile, id=article)
    expected_box, expected_size, color = (
        new_filters.pop("box"),
        new_filters.pop("size"),
        new_filters.pop("color"),
    )
    new_filters["color_name"], new_filters["feature_name"] = (
        color["color_name"],
        color["feature_name"],
    )
    box = await uow.db.read_one(Box, id=new_tile.box.id)
    size = await uow.db.read_one(TileSize, id=new_tile.size.id)

    # 1 проверка всех новых полей с помощью функций, в которых вынесена логика assert
    assert_size(size, expected_size)
    assert_box(box, expected_box)
    assert_tile_fields(new_tile, new_filters)

    # 2. Проверка всех справочников, поля в справочниках не должны изменятся, а должны появится новые
    await assert_handbooks_count(uow.db, domain_handbooks_models_for_products, 2)


@pytest.mark.asyncio
async def test_update_tile_success_when_composite_half_composite_color_name_box_weight_param(
    products_env_with_handbooks, domain_handbooks_models_for_products, tile
):
    env = products_env_with_handbooks
    record = await add_tile(
        tile=tile,
        uow=env.uow,
        file_manager=env.file_manager,
        images_generator=env.images_generator,
    )
    # получил также параметры создания, что бы получить часть композитного ключа без join read иначе из add_tile связанные данные box_area не подтянется
    article = record.id  # фильтр для обновления по артикулу
    # новые данные color_feature и box_area остаются старыми
    new_filters = update_filters(feature_name_missing=True, area_missing=True)
    old_color_feature, old_box_area = record.feature_name, tile.box.area
    await update_tile(uow=env.uow, article=article, **new_filters)
    async with env.uow as uow:
        new_tile = await uow.db.read_one(Tile, id=article)
        box = await uow.db.read_one(Box, id=new_tile.box_id)
        size = await uow.db.read_one(TileSize, id=new_tile.size_id)
    # половины композитного ключа берутся из той же записи продукта
    expected_box, expected_size = dict(
        **new_filters.pop("box"), area=old_box_area
    ), new_filters.pop("size")
    new_filters["color_name"], new_filters["feature_name"] = (
        new_tile.color_name,
        record.feature_name,
    )
    del new_filters["color"]

    assert_size(size, expected_size)
    assert_box(box, expected_box)
    # 1 проверка всех новых полей
    assert_tile_fields(new_tile, new_filters)
    # 2. Проверка всех справочников, поля в справочниках не должны изменятся, а должны появится новые
    await assert_handbooks_count(env.uow.db, domain_handbooks_models_for_products, 2)


@pytest.mark.asyncio
async def test_update_tile_success_when_input_composite_length_area_feature(
    products_env, domain_handbooks_models_for_products, tile
):
    env = products_env
    record = await add_tile(
        tile=tile,
        uow=env.uow,
        file_manager=env.file_manager,
        images_generator=env.images_generator,
    )
    # получил также параметры создания, что бы получить часть композитного ключа без join read иначе из add_tile связанные данные box_area не подтянется
    article = record.id  # фильтр для обновления по артикулу
    # меняются только size_length, box_area, color_feature
    new_filters = update_filters(
        color_name_missing=True,
        weight_missing=True,
        width_missing=True,
        height_missing=True,
    )
    old_color_name, old_box_weight, old_width, old_height = (
        record.color_name,
        tile.box.weight,
        tile.size.width,
        tile.size.height,
    )
    await update_tile(uow=env.uow, article=article, **new_filters)
    async with env.uow as uow:
        new_tile = await uow.db.read_one(Tile, id=article)
        box = await uow.db.read_one(Box, id=new_tile.box_id)
        size = await uow.db.read_one(TileSize, id=new_tile.size_id)
    # половины композитного ключа берутся из той же записи продукта
    expected_box, expected_size = dict(
        **new_filters.pop("box"), weight=old_box_weight
    ), dict(**new_filters.pop("size"), width=old_width, height=old_height)
    new_filters["color_name"], new_filters["feature_name"] = (
        record.color_name,
        new_tile.feature_name,
    )
    del new_filters["color"]

    assert_size(size, expected_size)
    assert_box(box, expected_box)
    # 1 проверка всех новых полей
    assert_tile_fields(new_tile, new_filters)
    # 2. Проверка всех справочников, поля в справочниках не должны изменятся, а должны появится новые
    await assert_handbooks_count(env.uow.db, domain_handbooks_models_for_products, 2)


@pytest.mark.asyncio
async def test_delete_tile_by_article(
    products_env, domain_handbooks_models_for_products, tile
):
    env = products_env
    record = await add_tile(
        tile=tile,
        uow=env.uow,
        images_generator=env.images_generator,
        file_manager=env.file_manager,
    )
    article = record.id
    records = await delete_tile(uow=env.uow, id=article, file_manager=env.file_manager)
    assert len(records) == 1
    for i in records:
        assert i.id == article

    async with env.uow:
        new_records = await env.uow.db.read(Tile, id=article)
        assert not new_records
        # При удалении продукта записи в связанных справочника не должны удаляться
        await assert_handbooks_count(
            env.uow.db, domain_handbooks_models_for_products, 1
        )
        # изображение должно каскадно удалиться
        images = await env.uow.db.read(Image)

    assert len(images) == 0
    # файлы изображений удалились
    assert product_files_count(env.file_manager) == 0
