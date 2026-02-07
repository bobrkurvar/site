import logging
from decimal import Decimal

import pytest

import core.logger
from adapters.crud import get_db_manager
from adapters.images import ProductImagesManager
from domain import Tile, TileImages
from services.tile import add_tile, delete_tile, update_tile
from tests.fakes import generate_products_images
from tests.conftest import domain_handbooks_models

from .helpers import product_files_count, fill_handbooks

log = logging.getLogger(__name__)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_integrate_create_tile_success_when_handbooks_not_exists(domain_handbooks_models):
    manager = get_db_manager(test=True)
    file_manager = ProductImagesManager(root="tests/images")
    # выполнение add_tile
    record = await add_tile(
        name="Tile",
        length=Decimal(300),
        width=Decimal(200),
        height=Decimal(10),
        color_name="color",
        producer_name="producer",
        box_weight=Decimal(30),
        box_area=Decimal(1),
        boxes_count=3,
        main_image=b"MAIN",
        category_name="category",
        manager=manager,
        images=[b"A", b"B"],
        color_feature="feature",
        surface="surface",
        file_manager=file_manager,
        generate_images=generate_products_images,
    )

    # 1. Tile создан
    assert record is not None
    assert "id" in record
    tile_id = record["id"]

    # проверка всех справочников
    for model in domain_handbooks_models:
        handbook = await manager.read(model)
        assert len(handbook) == 1, f"model: {model}"

    images = await manager.read(TileImages, tile_id=tile_id)
    assert len(images) == 3
    names = {f"{tile_id}-{i}" for i in range(3)}
    log.debug("names: %s", names)
    assert product_files_count(file_manager) == 9



@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_tile_success_when_all_handbooks_exists(domain_handbooks_models):
    manager = get_db_manager(test=True)
    file_manager = ProductImagesManager(root="tests/images")

    # заполняю справочники данными, которые будут использоваться при создании
    await fill_handbooks(
        length=Decimal(300),
        width=Decimal(200),
        height=Decimal(10),
        color_name="color",
        producer_name="producer",
        box_weight=Decimal(30),
        box_area=Decimal(1),
        category_name="category",
        manager=manager,
        color_feature="feature",
        surface="surface",
    )
    # выполнение add_tile
    record = await add_tile(
        name="Tile",
        length=Decimal(300),
        width=Decimal(200),
        height=Decimal(10),
        color_name="color",
        producer_name="producer",
        box_weight=Decimal(30),
        box_area=Decimal(1),
        boxes_count=3,
        main_image=b"MAIN",
        category_name="category",
        manager=manager,
        images=[b"A", b"B"],
        color_feature="feature",
        surface="surface",
        file_manager=file_manager,
        generate_images=generate_products_images,
    )

    # 1. Tile создан
    assert record is not None
    assert "id" in record


    # 1. Tile создан
    assert record is not None
    assert "id" in record
    tile_id = record["id"]

    # проверка всех справочников
    for model in domain_handbooks_models:
        handbook = await manager.read(model)
        assert len(handbook) == 1, f"model: {model}"

    images = await manager.read(TileImages, tile_id=tile_id)
    assert len(images) == 3
    names = {f"{tile_id}-{i}" for i in range(3)}
    log.debug("names: %s", names)
    assert product_files_count(file_manager) == 9


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_tile_success_when_new_attributes_in_handbooks(domain_handbooks_models):
    manager = get_db_manager(test=True)
    file_manager = ProductImagesManager(root="tests/images")

    # выполнение add_tile
    record = await add_tile(
        name="Tile",
        length=Decimal(300),
        width=Decimal(200),
        height=Decimal(10),
        color_name="color",
        producer_name="producer",
        box_weight=Decimal(30),
        box_area=Decimal(1),
        boxes_count=3,
        main_image=b"MAIN",
        category_name="category",
        manager=manager,
        images=[b"A", b"B"],
        color_feature="feature",
        surface="surface",
        file_manager=file_manager,
        generate_images=generate_products_images,
    )

    article = record["id"] # фильтр для обновления по артикулу

    # новые данные
    new_filters = dict(
        name="NewTile",
        size="500 300 20",
        color_name="NewColor",
        producer_name="NewProducer",
        box_weight=Decimal(50),
        box_area=Decimal(5),
        boxes_count=5,
        category_name="NewCategory",
        feature_name="NewFeature",
        surface_name="NewSurface",
    )

    await update_tile(manager, article, **new_filters)
    new_record = await manager.read(Tile, id=article, to_join=["box", "size"])

    # новый размер принимается на ввод как три числа через пробел, но для проверки данных и базы нужен их вид как чисел - длина, ширина, высота
    new_filters.pop("size")
    (
        new_filters["size_length"],
        new_filters["size_width"],
        new_filters["size_height"],
    ) = (Decimal(500), Decimal(300), Decimal(20))

    # 1 проверка всех новых полей
    for f, v in new_filters.items():
        assert new_record[0][f] == v

    # 2. Проверка всех справочников, поля в справочниках не должны изменятся, а должны появится новые
    for model in domain_handbooks_models:
        rows = await manager.read(model)
        assert len(rows) == 2, f"{model} should have at least one row"
#
#
# @pytest.mark.asyncio
# async def test_delete_tile_by_article(
#     manager_with_handbooks
# ):
#     manager = manager_with_handbooks
#     fs = {}
#
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
#         manager=manager,
#         images=[b"A", b"B"],
#         color_feature="feature",
#         surface="surface",
#         uow_class=FakeUoW,
#         save_files=get_fake_save_files_function_with_fs(fs),
#         generate_image_variant_callback=get_fake_save_bg_products_and_details_with_fs(fs)
#     )
#
#     article = record["id"]
#     expected_paths = [
#         f"static/images/base/products/{article}-0",
#         f"static/images/base/products/{article}-1",
#         f"static/images/base/products/{article}-2",
#     ]
#     log.debug("FS: %s", fs)
#
#     records = await delete_tile(manager, uow_class=FakeUoW, id=article, delete_files=get_fake_delete_files_function_with_fs(fs))
#     assert len(records) == 1
#
#     for path in expected_paths:
#         assert path not in fs.keys()
#
#     for i in records:
#         assert i['id'] == article
#
#     new_records = await manager.read(Tile, id=article)
#     assert new_records == []
#
#     should_be_handbooks = [
#         table
#         for table in manager.storage.tables
#         if table is not Tile and table is not TileImages
#     ]
#     for table_name in should_be_handbooks:
#         rows = await manager.read(table_name)
#         assert len(rows) == 1
#
#
