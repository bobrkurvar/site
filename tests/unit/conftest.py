from decimal import Decimal

import pytest

from domain import (Box, Categories, CollectionCategory, Collections, Producer,
                    Slug, Tile, TileColor, TileImages, TileSize, TileSurface)
from services.tile import add_tile
from tests.fakes import FakeCRUD, FakeUoW, noop_generate, FakeStorage
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


#
# @pytest.fixture
# def manager_factory(crud):
#
#     async def _manage_with_items(n: int = 0, color_fix: bool = False):
#         sizes = generate_tile_sizes(n)
#         colors = generate_tile_colors(n, True) if color_fix else generate_tile_colors(n)
#         boxes = generate_boxes(n)
#         file_manager = FakeProductImagesManager()
#         for i in range(n):
#             await add_tile(
#                 manager=crud,
#                 uow_class=FakeUoW,
#                 name=f"Tile{i+1}",
#                 length=sizes[i]["length"],
#                 width=sizes[i]["width"],
#                 height=sizes[i]["height"],
#                 color_name=colors[i]["color_name"],
#                 color_feature=colors[i]["feature_name"],
#                 producer_name="producer1",
#                 box_weight=boxes[i]["weight"],
#                 box_area=boxes[i]["area"],
#                 boxes_count=i + 1,
#                 main_image=b"MAIN",
#                 category_name="category",
#                 images=[b"A", b"B"],
#                 surface="surface1",
#                 generate_images=noop_generate,
#                 file_manager=file_manager,
#             )
#         return crud
#
#     return _manage_with_items




@pytest.fixture
async def products_env():
    fs = {}
    manager = FakeCRUD()
    file_manager = ProductImagesManager(root="tests/images", storage=FakeStorage(fs))
    return manager, file_manager, fs


@pytest.fixture
async def products_env_with_handbooks(products_env):
    manager, file_manager, fs = products_env

    await manager.create(TileSize, length=Decimal(300), width=Decimal(200), height=Decimal(10))
    await manager.create(TileColor, color_name="color", feature_name="feature")
    await manager.create(Producer, name="producer")
    await manager.create(Box, weight=Decimal(30), area=Decimal(1))

    return manager, file_manager, fs


@pytest.fixture
async def collection_env():
    fs = {}
    manager = FakeCRUD()
    file_manager = CollectionImagesManager(root="tests/images", storage=FakeStorage(fs))
    return manager, file_manager, fs

