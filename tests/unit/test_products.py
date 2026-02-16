import logging
from decimal import Decimal

import pytest

from domain import Tile, TileImages
from services.tile import add_tile, delete_tile, update_tile
from tests.conftest import domain_handbooks_models
from tests.fakes import (FakeProductImagesManager, FakeUoW,
                         generate_products_images)

from .conftest import manager, manager_with_handbooks
from .helpers import product_catalog_path, product_details_path

log = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_tile_success_when_all_handbooks_exists(
    manager_with_handbooks, domain_handbooks_models
):
    manager = manager_with_handbooks
    fs = {}
    file_manager = FakeProductImagesManager(fs=fs)
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
        uow_class=FakeUoW,
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

    # 2. Все изображения записались во фейковую ФС
    paths_funcs = (
        file_manager.base_product_path,
        product_catalog_path(file_manager),
        product_details_path(file_manager),
    )
    file_names = (f"{tile_id}-0", f"{tile_id}-1", f"{tile_id}-2")
    expected_paths = [
        str(func(file_name)) for func in paths_funcs for file_name in file_names
    ]

    assert set(fs) == set(expected_paths)

    assert fs[expected_paths[0]] == b"MAIN"
    assert fs[expected_paths[1]] == b"A"
    assert fs[expected_paths[2]] == b"B"
    images_table = await manager.read(TileImages)
    assert len(images_table) == 3


@pytest.mark.asyncio
async def test_create_tile_success_when_all_handbooks_not_exists(
    manager, domain_handbooks_models
):
    manager = manager
    fs = {}
    file_manager = FakeProductImagesManager(fs=fs)
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
        uow_class=FakeUoW,  # поддельная транзакция
        file_manager=file_manager,
        generate_images=generate_products_images,
    )

    # 1. Tile создан
    assert record is not None
    assert "id" in record

    # проверка всех справочников
    for model in domain_handbooks_models:
        handbook = await manager.read(model)
        assert len(handbook) == 1, f"model: {model}"

    # 3. Все изображения записались во фейковую ФС
    tile_id = record["id"]
    paths_funcs = (
        file_manager.base_product_path,
        product_catalog_path(file_manager),
        product_details_path(file_manager),
    )
    file_names = (f"{tile_id}-0", f"{tile_id}-1", f"{tile_id}-2")
    expected_paths = [
        str(func(file_name)) for func in paths_funcs for file_name in file_names
    ]

    assert set(fs) == set(expected_paths)

    assert fs[expected_paths[0]] == b"MAIN"
    assert fs[expected_paths[1]] == b"A"
    assert fs[expected_paths[2]] == b"B"

    images_table = await manager.read(TileImages)

    assert len(images_table) == 3


@pytest.mark.asyncio
async def test_update_tile_success_when_new_attributes_in_handbooks(
    manager_with_handbooks, domain_handbooks_models
):
    manager = manager_with_handbooks
    file_manager = FakeProductImagesManager()
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
        uow_class=FakeUoW,
        file_manager=file_manager,
        generate_images=generate_products_images,
    )
    article = record["id"]  # фильтр для обновления по артикулу

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

    await update_tile(manager, article, uow_class=FakeUoW, **new_filters)
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
    for table_name in domain_handbooks_models:
        rows = await manager.read(table_name)
        assert len(rows) == 2, f"{table_name.__name__} should have at least one row"


@pytest.mark.asyncio
async def test_delete_tile_by_article(manager_with_handbooks, domain_handbooks_models):
    manager = manager_with_handbooks
    fs = {}
    file_manager = FakeProductImagesManager(fs=fs)
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
        uow_class=FakeUoW,
        file_manager=file_manager,
        generate_images=generate_products_images,
    )

    tile_id = record["id"]
    paths_funcs = (
        file_manager.base_product_path,
        product_catalog_path(file_manager),
        product_details_path(file_manager),
    )
    file_names = (f"{tile_id}-0", f"{tile_id}-1", f"{tile_id}-2")
    expected_paths = [
        str(func(file_name)) for func in paths_funcs for file_name in file_names
    ]
    log.debug("FS: %s", fs)
    records = await delete_tile(
        manager, uow_class=FakeUoW, id=tile_id, file_manager=file_manager
    )
    assert len(records) == 1

    for path in expected_paths:
        assert path not in fs.keys()

    for i in records:
        assert i["id"] == tile_id

    new_records = await manager.read(Tile, id=tile_id)
    assert new_records == []

    for table_name in domain_handbooks_models:
        rows = await manager.read(table_name)
        assert len(rows) == 1
