import logging
from decimal import Decimal
import core.logger

import pytest

from domain import (Box, Categories, Producer, Tile, TileColor, TileImages,
                    TileSize, TileSurface)
from services.tile import add_tile, delete_tile, update_tile

from .fakes import (FakeCRUD, FakeFileSystem, FakePath, FakeStorage, FakeUoW,
                    Table)

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
                rows=[],
                foreign_keys={Tile: {"tile_id": "id"}},
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
                rows=[],
                foreign_keys={
                    TileSize: {"size_id": "id"},
                    TileColor: {
                        ("color_name", "feature_name"): ("color_name", "feature_name")
                    },
                    Categories: {"category_name": "name"},
                    TileSurface: {"surface_name": "name"},
                    Producer: {"producer_name": "name"},
                    Box: {"box_id": "id"},
                },
                defaults={"id": 1},
            ),
        ]
    )

    return storage


@pytest.fixture
def manager_with_handbooks(storage_with_filled_handbooks):
    return FakeCRUD(storage_with_filled_handbooks)


@pytest.fixture
def storage():
    storage = FakeStorage()

    storage.register_tables(
        [
            Table(
                name=TileSize,
                columns=["id", "length", "width", "height"],
                rows=[],
                defaults={"id": 2},
            ),
            Table(name=TileSurface, columns=["name"], rows=[{"name": "surface"}]),
            Table(
                name=TileImages,
                columns=["image_id", "tile_id", "image_path"],
                rows=[],
                foreign_keys={Tile: {"tile_id": "id"}},
                defaults={"image_id": 1},
            ),
            Table(
                name=TileColor,
                columns=["color_name", "feature_name"],
                rows=[],
            ),
            Table(name=Producer, columns=["name"], rows=[{"name": "producer"}]),
            Table(name=Categories, columns=["name"], rows=[{"name": "category"}]),
            Table(
                name=Box,
                columns=["id", "weight", "area"],
                rows=[],
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
                rows=[],
                foreign_keys={
                    TileSize: {"size_id": "id"},
                    TileColor: {
                        ("color_name", "feature_name"): ("color_name", "feature_name")
                    },
                    Categories: {"category_name": "name"},
                    TileSurface: {"surface_name": "name"},
                    Producer: {"producer_name": "name"},
                    Box: {"box_id": "id"},
                },
                defaults={"id": 1},
            ),
        ]
    )

    return storage


@pytest.fixture
def manager_without_handbooks(storage):
    return FakeCRUD(storage)


@pytest.fixture
def fs():
    return FakeFileSystem()


@pytest.mark.asyncio
async def test_create_tile_success_when_all_handbooks_exists(
    manager_with_handbooks, fs
):
    upload_root = FakePath("static/images")
    manager = manager_with_handbooks

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
        fs=fs,  # подделанная файловая система
        uow_class=FakeUoW,  # поддельная транзакция
        upload_root=upload_root,  # поддельный путь
        bg=False
    )

    # 1. Tile создан
    assert record is not None
    assert "id" in record

    tile_id = record["id"]

    # 2. Все изображения записались во фейковую ФС
    expected_paths = [
        f"static/images/base/products/{tile_id}-0",
        f"static/images/base/products/{tile_id}-1",
        f"static/images/base/products/{tile_id}-2",
    ]

    assert set(fs.files.keys()) == set(expected_paths)

    assert fs.files[expected_paths[0]] == b"MAIN"
    assert fs.files[expected_paths[1]] == b"A"
    assert fs.files[expected_paths[2]] == b"B"

    images_table = await manager.read(TileImages)

    assert len(images_table) == 3
    stored_paths = [row["image_path"] for row in images_table]
    assert stored_paths == expected_paths


@pytest.mark.asyncio
async def test_create_tile_success_when_all_handbooks_not_exists(
    manager_without_handbooks, fs
):
    upload_root = FakePath("static/images")
    manager = manager_without_handbooks

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
        fs=fs,  # подделанная файловая система
        uow_class=FakeUoW,  # поддельная транзакция
        upload_root=upload_root, # поддельный путь
        bg=False
    )

    # 1. Tile создан
    assert record is not None
    assert "id" in record

    # 2. Проверка всех справочников
    for table_name in manager.storage.tables:
        rows = await manager.read(table_name)
        assert rows, f"{table_name.__name__} should have at least one row"

    # 3. Все изображения записались во фейковую ФС
    tile_id = record["id"]
    expected_paths = [
        f"static/images/base/products/{tile_id}-0",
        f"static/images/base/products/{tile_id}-1",
        f"static/images/base/products/{tile_id}-2",
    ]

    assert set(fs.files.keys()) == set(expected_paths)

    assert fs.files[expected_paths[0]] == b"MAIN"
    assert fs.files[expected_paths[1]] == b"A"
    assert fs.files[expected_paths[2]] == b"B"

    images_table = await manager.read(TileImages)

    assert len(images_table) == 3
    stored_paths = [row["image_path"] for row in images_table]
    assert stored_paths == expected_paths


@pytest.mark.asyncio
async def test_update_tile_success_when_new_attributes_in_handbooks(
    manager_with_handbooks, fs
):
    upload_root = FakePath("root")
    manager = manager_with_handbooks

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
        fs=fs,
        uow_class=FakeUoW,
        upload_root=upload_root,
        bg=False
    )

    article = record["id"]

    new_size = "500 300 20"

    new_filters = dict(
        name="NewTile",
        size=new_size,
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
    new_filters.pop("size")
    (
        new_filters["size_length"],
        new_filters["size_width"],
        new_filters["size_height"],
    ) = (Decimal(500), Decimal(300), Decimal(20))

    # 1 проверка всех новых полей
    for f, v in new_filters.items():
        assert new_record[0][f] == v

    # 2. Проверка всех справочников
    should_new_handbooks = [
        table
        for table in manager.storage.tables
        if table is not Tile and table is not TileImages
    ]
    for table_name in should_new_handbooks:
        rows = await manager.read(table_name)
        assert len(rows) == 2, f"{table_name.__name__} should have at least one row"
