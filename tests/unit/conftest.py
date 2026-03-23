from decimal import Decimal

import pytest

from domain import (Box, Categories, CollectionCategory, Collections, Producer,
                    Slug, Tile, TileColor, TileImages, TileSize, TileSurface)
from services.tile import add_tile
from tests.fakes import FakeCRUD, FakeUoW, FakeStorage
from infrastructure.images import ProductImagesManager, CollectionImagesManager, SlideImagesManager



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
def manager_factory(crud):
    async def _manage_with_items(n: int = 0, color_fix: bool = False):
        manager = crud
        sizes = generate_tile_sizes(n)
        colors = generate_tile_colors(n, True) if color_fix else generate_tile_colors(n)
        #boxes = generate_boxes(n)
        for i in range(n):
            size = await manager.create(TileSize, **sizes[i])
            #box = await manager.create(Box, **boxes[i])
            color = await manager.create(TileColor, **colors[i])
            await manager.create(Tile, name=f"Tile{i}", size_id=size["id"], **color, producer_name=f"producer{i}")
        return manager

    return _manage_with_items


@pytest.fixture
def crud():
    return FakeCRUD()


@pytest.fixture
async def products_env(crud):
    fs = {}
    file_manager = ProductImagesManager(root="tests/images", storage=FakeStorage(fs))
    return crud, file_manager, fs


@pytest.fixture
async def products_env_with_handbooks(products_env):
    manager, file_manager, fs = products_env

    await manager.create(TileSize, length=Decimal(300), width=Decimal(200), height=Decimal(10))
    await manager.create(TileColor, color_name="color", feature_name="feature")
    await manager.create(Producer, name="producer")
    await manager.create(Box, weight=Decimal(30), area=Decimal(1))
    await manager.create(TileSurface, name="surface")
    await manager.create(Categories, name="category")

    return manager, file_manager, fs


@pytest.fixture
async def collection_env(crud):
    fs = {}
    file_manager = CollectionImagesManager(root="tests/images", storage=FakeStorage(fs))
    return crud, file_manager, fs

