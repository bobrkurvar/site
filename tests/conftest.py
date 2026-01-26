from decimal import Decimal
import pytest
from .fakes import FakeUoW, FakeStorage, Table, FakeCRUD
from services.tile import add_tile
from domain import TileSize, TileColor, Box, Categories, Producer, TileSurface, TileImages, Tile, Collections

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
        {"weight": Decimal(i * 10), "area": Decimal(i)}
        for i in range(1, count + 1)
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
                rows=[],
                defaults={"id": 1},
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
                defaults={"id": 1},
            ),
            Table(
                name=Collections,
                columns=["name", "category_name", "image_path"],
                rows=[],
                defaults={},
                unique=["name", "category_name"],
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
def fake_manager(storage):
    return FakeCRUD(storage)

@pytest.fixture
def manager_factory(fake_manager):

    async def _manage_with_items(n: int = 0, color_fix: bool = False):
        sizes = generate_tile_sizes(n)
        colors = generate_tile_colors(n, True) if color_fix else generate_tile_colors(n)
        boxes = generate_boxes(n)

        for i in range(n):
            await add_tile(
                manager=fake_manager,
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
                boxes_count=i+1,
                main_image=b"MAIN",
                category_name="category",
                images=[b"A", b"B"],
                surface="surface1",
                generate_image_variant_callback=noop,
                save_files=noop
            )
        return fake_manager
    return _manage_with_items