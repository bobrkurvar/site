import logging
from decimal import Decimal

import pytest

import core.logger
from domain import (Box, Categories, Producer, Tile, TileColor, TileImages,
                    TileSize, TileSurface)
from services.tile import add_tile, delete_tile, update_tile

from tests.fakes import (FakeCRUD, FakeStorage, FakeUoW, Table)
from tests.fakes import FakeFileManager, generate_products_images
from tests.conftest import storage

log = logging.getLogger(__name__)


@pytest.fixture
def storage_with_filled_handbooks():
    storage = FakeStorage()

    storage.register_tables(
        [
            Table(
                name=TileSize,
                columns=["id", "length", "width", "height"],
                rows=[
                    {
                        "id": 1,
                        "length": Decimal(300),
                        "width": Decimal(200),
                        "height": Decimal(10),
                    }
                ],
                defaults={"id": 2},
            ),
            Table(name=TileSurface, columns=["name"], rows=[{"name": "surface"}]),
            Table(
                name=TileImages,
                columns=["image_id", "tile_id", "image_path"],
                defaults={"image_id": 1},
            ),
            Table(
                name=TileColor,
                columns=["color_name", "feature_name"],
                rows=[{"color_name": "color", "feature_name": "feature"}],
            ),
            Table(name=Producer, columns=["name"], rows=[{"name": "producer"}]),
            Table(name=Categories, columns=["name"], rows=[{"name": "category"}]),
            Table(
                name=Box,
                columns=["id", "weight", "area"],
                rows=[{"id": 1, "weight": Decimal(30), "area": Decimal(1)}],
                defaults={"id": 2},
            ),
            Table(
                name=Tile,
                columns=[
                    "id",
                    "name",
                    "size_id",
                    "color_name",
                    "feature_name",
                    "category_name",
                    "surface_name",
                    "producer_name",
                    "box_id",
                    "boxes_count",
                ],
                defaults={"id": 1},
            ),
        ]
    )

    return storage


@pytest.fixture
def manager_with_handbooks(storage_with_filled_handbooks):
    return FakeCRUD(storage_with_filled_handbooks)


@pytest.fixture
def manager_without_handbooks(storage):
    return FakeCRUD(storage)


@pytest.mark.asyncio
async def test_create_tile_success_when_all_handbooks_exists(
    manager_with_handbooks
):
    manager = manager_with_handbooks
    fs = {}
    file_manager = FakeFileManager(fs=fs)
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
        generate_images=generate_products_images
    )

    # 1. Tile создан
    assert record is not None
    assert "id" in record

    tile_id = record["id"]

    # 2. Все изображения записались во фейковую ФС
    paths_funcs = (file_manager.base_product_path, file_manager.product_catalog_path, file_manager.product_details_path)
    file_names = (f"{tile_id}-0", f"{tile_id}-1", f"{tile_id}-2")
    expected_paths = [str(func(file_name)) for func in paths_funcs for file_name in file_names]

    assert set(fs) == set(expected_paths)

    assert fs[expected_paths[0]] == b"MAIN"
    assert fs[expected_paths[1]] == b"A"
    assert fs[expected_paths[2]] == b"B"
    images_table = await manager.read(TileImages)
    assert len(images_table) == 3


@pytest.mark.asyncio
async def test_create_tile_success_when_all_handbooks_not_exists(
    manager_without_handbooks
):
    manager = manager_without_handbooks
    fs = {}
    file_manager = FakeFileManager(fs=fs)
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
        generate_images=generate_products_images
    )

    # 1. Tile создан
    assert record is not None
    assert "id" in record


    # 2. Проверка всех справочников
    tables = (Box, Categories, Producer, Tile, TileColor, TileImages, TileSize, TileSurface)

    for table_name in tables:
        rows = await manager.read(table_name)
        assert rows, f"{table_name.__name__} should have at least one row"

    # 3. Все изображения записались во фейковую ФС
    tile_id = record["id"]
    paths_funcs = (file_manager.base_product_path, file_manager.product_catalog_path, file_manager.product_details_path)
    file_names = (f"{tile_id}-0", f"{tile_id}-1", f"{tile_id}-2")
    expected_paths = [str(func(file_name)) for func in paths_funcs for file_name in file_names]

    assert set(fs) == set(expected_paths)

    assert fs[expected_paths[0]] == b"MAIN"
    assert fs[expected_paths[1]] == b"A"
    assert fs[expected_paths[2]] == b"B"

    images_table = await manager.read(TileImages)

    assert len(images_table) == 3


@pytest.mark.asyncio
async def test_update_tile_success_when_new_attributes_in_handbooks(
    manager_with_handbooks
):
    manager = manager_with_handbooks
    file_manager = FakeFileManager()
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
        generate_images=generate_products_images
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
    should_new_handbooks = [
        table
        for table in manager.storage.tables
        if table is not Tile and table is not TileImages
    ]
    for table_name in should_new_handbooks:
        rows = await manager.read(table_name)
        assert len(rows) == 2, f"{table_name.__name__} should have at least one row"


@pytest.mark.asyncio
async def test_delete_tile_by_article(
    manager_with_handbooks
):
    manager = manager_with_handbooks
    fs = {}
    file_manager = FakeFileManager(fs=fs)
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
        generate_images=generate_products_images
    )

    tile_id = record["id"]
    paths_funcs = (file_manager.base_product_path, file_manager.product_catalog_path, file_manager.product_details_path)
    file_names = (f"{tile_id}-0", f"{tile_id}-1", f"{tile_id}-2")
    expected_paths = [str(func(file_name)) for func in paths_funcs for file_name in file_names]

    file_manager = FakeFileManager(fs=fs)
    records = await delete_tile(manager, uow_class=FakeUoW, id=tile_id, file_manager=file_manager)
    assert len(records) == 1

    for path in expected_paths:
        assert path not in fs.keys()

    for i in records:
        assert i['id'] == tile_id

    new_records = await manager.read(Tile, id=tile_id)
    assert new_records == []

    should_be_handbooks = [
        table
        for table in manager.storage.tables
        if table is not Tile and table is not TileImages
    ]
    for table_name in should_be_handbooks:
        rows = await manager.read(table_name)
        assert len(rows) == 1


