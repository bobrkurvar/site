from decimal import Decimal

import pytest

from domain import (Box, Categories, Collections, Producer, Tile, TileColor,
                    TileImages, TileSize, TileSurface, Slug, CollectionCategory)
from services.tile import add_tile
from tests.fakes import (FakeCRUD, FakeProductImagesManager, FakeStorage,
                         FakeUoW, Table, noop_generate)


async def noop(*args, **kwargs):
    return None


# Генератор размеров
def generate_tile_sizes(count):
    return [
        {"length": Decimal(i), "width": Decimal(i), "height": Decimal(i)}
        for i in range(1, count + 1)
    ]


# Генератор цветов
def generate_tile_colors(count, fix=False):
    if fix:
        return [
            {"color_name": f"color", "feature_name": f"feature{i}"}
            for i in range(1, count + 1)
        ]
    else:
        return [
            {"color_name": f"color{i}", "feature_name": f"feature{i}"}
            for i in range(1, count + 1)
        ]


# Генератор боксов
def generate_boxes(count):
    return [
        {"weight": Decimal(i * 10), "area": Decimal(i)} for i in range(1, count + 1)
    ]


# Генератор категорий
def generate_categories(count):
    return [{"name": f"category{i}"} for i in range(1, count + 1)]


@pytest.fixture
def storage():
    storage = FakeStorage()

    storage.register_tables(
        [
            Table(
                name=TileSize,
                columns=["id", "length", "width", "height"],
                defaults={"id": 1},
            ),
            Table(name=TileSurface, columns=["name"]),
            Table(
                name=TileImages,
                columns=["image_id", "tile_id", "image_path"],
                defaults={"image_id": 1},
            ),
            Table(
                name=TileColor,
                columns=["color_name", "feature_name"],
            ),
            Table(name=Producer, columns=["name"]),
            Table(name=Categories, columns=["name"]),
            Table(
                name=Box,
                columns=["id", "weight", "area"],
                defaults={"id": 1},
            ),
            Table(
                name=Collections,
                columns=["id", "name", "image_path"],
                defaults={"id": 1, "image_path": None}
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
            Table(name=Slug,columns=["name", "slug"]),
            Table(
                name=CollectionCategory,
                columns=["collection_id", "category_name"]
            )
        ]
    )

    return storage



@pytest.fixture
def manager(storage):
    return FakeCRUD(storage)

@pytest.fixture
def manager_factory(manager):

    async def _manage_with_items(n: int = 0, color_fix: bool = False):
        sizes = generate_tile_sizes(n)
        colors = generate_tile_colors(n, True) if color_fix else generate_tile_colors(n)
        boxes = generate_boxes(n)
        file_manager = FakeProductImagesManager()
        for i in range(n):
            await add_tile(
                manager=manager,
                uow_class=FakeUoW,
                name=f"Tile{i+1}",
                length=sizes[i]["length"],
                width=sizes[i]["width"],
                height=sizes[i]["height"],
                color_name=colors[i]["color_name"],
                color_feature=colors[i]["feature_name"],
                producer_name="producer1",
                box_weight=boxes[i]["weight"],
                box_area=boxes[i]["area"],
                boxes_count=i + 1,
                main_image=b"MAIN",
                category_name="category",
                images=[b"A", b"B"],
                surface="surface1",
                generate_images=noop_generate,
                file_manager=file_manager,
            )
        return manager

    return _manage_with_items


@pytest.fixture
def storage_with_filled_handbooks(storage):
    storage.add(
        TileSize,
        length=Decimal(300),
        width=Decimal(200),
        height=Decimal(10)
    )
    storage.add(TileColor, color_name="color", feature_name="feature")
    storage.add(Producer, name="producer")
    storage.add(Box, weight=Decimal(30), area=Decimal(1))

    return storage


@pytest.fixture
def manager_with_handbooks(storage_with_filled_handbooks):
    return FakeCRUD(storage_with_filled_handbooks)


# @pytest.fixture
# def storage_with_collection(storage):
#     storage.add(Collections, name="collection1")
#     return storage
#
# @pytest.fixture
# def manager_with_collection(storage_with_collection):
#     return FakeCRUD(storage_with_collection)