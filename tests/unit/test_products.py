import logging
from decimal import Decimal

import pytest

from domain import *
from services.tile import add_tile, delete_tile, update_tile
from tests.conftest import domain_handbooks_models_for_products
from tests.fakes import FakeUoW, generate_products_images
from .conftest import products_env, products_env_with_handbooks
from .helpers import product_catalog_path, product_details_path, add_tile_helper, assert_size, assert_box, assert_tile_fields, assert_handbooks_count

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_tile_success_when_all_handbooks_exists(
    products_env_with_handbooks, domain_handbooks_models_for_products
):
    manager, file_manager, fs = products_env_with_handbooks
    record = await add_tile_helper(manager, file_manager, generate_products_images)

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
    record = await add_tile_helper(manager, file_manager, generate_products_images)
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
    record = await add_tile_helper(manager, file_manager, generate_products_images)

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
    record = await add_tile_helper(manager, file_manager, generate_products_images)

    log.debug("old_tile: %s", record)
    article = record["id"]  # фильтр для обновления по артикулу

    # новые данные
    new_filters = dict(
        name="NewTile",
        size={"length": Decimal(500), "width": Decimal(300), "height": Decimal(20)},
        color={"color_name": "NewColor", "feature_name": "NewFeature"},
        box={"area": Decimal(5), "weight": Decimal(50)},
        producer_name="NewProducer",
        boxes_count=5,
        category_name="NewCategory",
        surface_name="NewSurface",
    )
    await update_tile(manager, article, uow_class=FakeUoW, **new_filters)

    new_tile = (await manager.read(Tile, id=article))[0]
    expected_box = new_filters.pop("box")
    expected_size = new_filters.pop("size")
    box = (await manager.read(Box, id=new_tile["box_id"]))[0]
    size = (await manager.read(TileSize, id=new_tile["size_id"]))[0]
    color = new_filters.pop("color")
    new_filters["color_name"], new_filters["feature_name"] = color["color_name"], color["feature_name"]

    # 1 проверка всех новых полей с помощью функций, в которых вынесена логика assert
    assert_size(size, expected_size)
    assert_box(box, expected_box)
    assert_tile_fields(new_tile, new_filters)

    # 2. Проверка всех справочников, поля в справочниках не должны изменятся, а должны появится новые
    await assert_handbooks_count(manager, domain_handbooks_models_for_products, 2)


# @pytest.mark.asyncio
# async def test_update_tile_success_when_composite_half_composite_color_name_box_weight_param(
#     manager_with_handbooks, domain_handbooks_models_for_products
# ):
#     file_manager = FakeProductImagesManager()
#     record = await add_tile(
#         name="Tile",
#         length=Decimal(300),
#         width=Decimal(200),
#         height=Decimal(10),
#         color_name="color",
#         producer_name="producer",
#         box_weight=Decimal(30),
#         box_area=Decimal(1),
#         boxes_count=3,
#         main_image=b"MAIN",
#         category_name="category",
#         manager=manager_with_handbooks,
#         images=[b"A", b"B"],
#         color_feature="feature",
#         surface="surface",
#         uow_class=FakeUoW,
#         file_manager=file_manager,
#         generate_images=generate_products_images,
#     )
#     article = record["id"]  # фильтр для обновления по артикулу
#
#     # новые данные
#     new_filters = dict(
#         name="NewTile",
#         size={"length": Decimal(500), "width": Decimal(300), "height": Decimal(20)},
#         color = {"color_name": "NewColor"},
#         box = {"weight": Decimal(50)},
#         producer_name="NewProducer",
#         boxes_count=5,
#         category_name="NewCategory",
#         surface_name="NewSurface",
#     )
#
#     await update_tile(manager_with_handbooks, article, uow_class=FakeUoW, **new_filters)
#
#     # половины композитного ключа берутся из той же записи продукта
#     new_tile = (await manager_with_handbooks.read(Tile, id=article))[0]
#     box = (await manager_with_handbooks.read(Box, id=new_tile["box_id"]))[0]
#     log.debug("box: %s", box)
#     size = (await manager_with_handbooks.read(TileSize, id=new_tile["size_id"]))[0]
#     new_box = new_filters.pop("box")
#     assert box["weight"] == new_box["weight"] and box["area"] == Decimal(1)
#     new_size = new_filters.pop("size")
#     assert size["length"] == new_size["length"] and size["width"] == new_size["width"] and size["height"] == new_size["height"]
#     color = new_filters.pop("color")
#     new_filters["color_name"], new_filters["feature_name"] = color["color_name"], "feature"
#     # 1 проверка всех новых полей
#     for f, v in new_filters.items():
#         assert (
#             new_tile[f] == v
#         ), f"key: {f}, expected value: {v}, real value: {new_tile[f]}"
#
#     # 2. Проверка всех справочников, поля в справочниках не должны изменятся, а должны появится новые
#     for table_name in domain_handbooks_models_for_products:
#         rows = await manager_with_handbooks.read(table_name)
#         assert len(rows) == 2, f"{table_name.__name__} should have at least one row"
#
#
# @pytest.mark.asyncio
# async def test_update_tile_success_when_composite_half_composite_feature_name_box_area_param(
#     manager_with_handbooks, domain_handbooks_models_for_products
# ):
#     file_manager = FakeProductImagesManager()
#     record = await add_tile(
#         name="Tile",
#         length=Decimal(300),
#         width=Decimal(200),
#         height=Decimal(10),
#         color_name="color",
#         producer_name="producer",
#         box_weight=Decimal(30),
#         box_area=Decimal(1),
#         boxes_count=3,
#         main_image=b"MAIN",
#         category_name="category",
#         manager=manager_with_handbooks,
#         images=[b"A", b"B"],
#         color_feature="feature",
#         surface="surface",
#         uow_class=FakeUoW,
#         file_manager=file_manager,
#         generate_images=generate_products_images,
#     )
#     article = record["id"]  # фильтр для обновления по артикулу
#
#     # новые данные
#     new_filters = dict(
#         name="NewTile",
#         size={"length": Decimal(500), "width": Decimal(300), "height": Decimal(20)},
#         feature_name="NewFeature",
#         producer_name="NewProducer",
#         box_area=Decimal(50),
#         boxes_count=5,
#         category_name="NewCategory",
#         surface_name="NewSurface",
#     )
#
#     await update_tile(manager_with_handbooks, article, uow_class=FakeUoW, **new_filters)
#     new_record = (
#         await manager_with_handbooks.read(Tile, id=article, to_join=["box", "size"])
#     )[0]
#     log.debug("NEW RECORD: %s", new_record)
#
#     size = new_filters.pop("size")
#     (
#         new_filters["size_length"],
#         new_filters["size_width"],
#         new_filters["size_height"],
#     ) = (size["length"], size["width"], size["height"])
#     new_filters["box_weight"], new_filters["color_name"] = (
#         Decimal(30),
#         "color",
#     )  # другие половины композитного ключа берутся из той же записи продукта
#
#     # 1 проверка всех новых полей
#     for f, v in new_filters.items():
#         assert (
#             new_record[f] == v
#         ), f"key: {f}, expected value: {v}, real value: {new_record[f]}"
#
#     # 2. Проверка всех справочников, поля в справочниках не должны изменятся, а должны появится новые
#     for table_name in domain_handbooks_models_for_products:
#         rows = await manager_with_handbooks.read(table_name)
#         assert len(rows) == 2, f"{table_name.__name__} should have at least one row"




@pytest.mark.asyncio
async def test_delete_tile_by_article(products_env, domain_handbooks_models_for_products):
    manager, file_manager, fs = products_env
    record = await add_tile_helper(manager, file_manager, generate_products_images)
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

