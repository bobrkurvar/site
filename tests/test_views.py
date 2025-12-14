import logging
from decimal import Decimal

import pytest

from domain import (Box, Categories, Producer, Tile, TileColor, TileImages,
                    TileSize, TileSurface, Collections)

from services.tile import add_tile
from services.views import fetch_items

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
                name=Collections,
                columns=["name", "images_path"],
                rows=[],
                defaults={},
                unique=["name"],
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

@pytest.fixture
def manager_factory(storage, fs):
    async def _create(n: int):
        manager = FakeCRUD(storage)
        upload_root = FakePath("root")

        for i in range(n):
            await add_tile(
                name=f"Tile{i}",
                length=Decimal(300),
                width=Decimal(200),
                height=Decimal(10),
                color_name="color",
                producer_name="producer",
                box_weight=Decimal(30),
                box_area=Decimal(1),
                boxes_count=3,
                main_image=b"i_0",
                category_name="category",
                manager=manager,
                images=[b"A", b"B"],
                color_feature="feature",
                surface="surface",
                fs=fs,
                uow_class=FakeUoW,
                upload_root=upload_root,
            )
        return manager

    return _create

@pytest.mark.asyncio
async def test_get_page_catalog_when_loading_one_page(manager_factory):
    manager = await manager_factory(20)
    tiles, count = await fetch_items(manager, 20, 0, category_name="category")


    assert len(tiles) == count == 20


