from decimal import Decimal

import pytest

from adapters.images import CollectionImagesManager, ProductImagesManager
from domain import (Box, Category, Producer, Tile, TileColor, TileSize,
                    TileSurface)
from tests.fakes import FakeCRUD, FakeRedisService, FakeStorage


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
        boxes = generate_boxes(n)
        for i in range(n):
            size = await manager.create(TileSize(**sizes[i]))
            box = await manager.create(Box(**boxes[i]))
            color = await manager.create(TileColor(**colors[i]))
            await manager.create(
                Tile(
                    name=f"Tile{i}",
                    size=size,
                    color=color,
                    producer=Producer(f"producer{i}"),
                    box=box,
                    boxes_count=1,
                    category=Category("category"),
                )
            )
        return manager

    return _manage_with_items


@pytest.fixture
def crud():
    return FakeCRUD()


@pytest.fixture
def redis():
    return FakeRedisService()


@pytest.fixture
async def products_env(crud):
    fs = {}
    file_manager = ProductImagesManager(root="tests/images", storage=FakeStorage(fs))
    return crud, file_manager, fs


@pytest.fixture
async def products_env_with_handbooks(products_env):
    manager, file_manager, fs = products_env
    await manager.create(
        seq_data=[
            TileSize(length=300, width=200, height=10),
            TileColor(color_name="color", feature_name="feature"),
            Producer(name="producer"),
            Box(weight=30, area=1),
            TileSurface(name="surface"),
            Category(name="category"),
        ]
    )
    return manager, file_manager, fs


@pytest.fixture
async def collection_env(crud):
    fs = {}
    file_manager = CollectionImagesManager(root="tests/images", storage=FakeStorage(fs))
    return crud, file_manager, fs


@pytest.fixture
def collection_images():
    fs, root = {}, "tests/images"
    return CollectionImagesManager(root=root, storage=FakeStorage(fs)), fs, root


@pytest.fixture
def product_images():
    fs, root = {}, "tests/images"
    return ProductImagesManager(root=root, storage=FakeStorage(fs)), fs, root
