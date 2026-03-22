from decimal import Decimal
from tests.fakes import FakeUoW
from services.tile import add_tile
from services.collections import add_collection


async def add_tile_helper(manager, file_manager, generate_products_images, need_params: bool = False):
    # обёртка на сервисным методом add_tile, которая создана для многоразового использования одного и того же вызова функции
    # для уменьшения объёма кода
    params = dict(
        name = "Tile",
        length = Decimal(300),
        width = Decimal(200),
        height = Decimal(10),
        color_name = "color",
        producer_name = "producer",
        box_weight = Decimal(30),
        box_area = Decimal(1),
        boxes_count = 3,
        main_image = b"MAIN",
        category_name = "category",
        manager = manager,
        images = [b"A", b"B"],
        color_feature = "feature",
        surface = "surface",
        uow_class = FakeUoW,
        file_manager = file_manager,
        generate_images = generate_products_images,
    )
    return await add_tile(**params), params if need_params else await add_tile(**params)


def assert_tile_fields(tile, expected):
    for k, v in expected.items():
        assert tile[k] == v, f"{k}: expected {v}, got {tile[k]}"


def assert_size(size: dict, expected: dict):
    # функция для вынесения логики проверки размеров
    assert size["length"] == expected["length"]
    assert size["width"] == expected["width"]
    assert size["height"] == expected["height"]


def assert_box(box, expected):
    # функция для вынесения логики проверки размеров данных о коробке
    assert box["weight"] == expected["weight"]
    assert box["area"] == expected["area"]


async def assert_handbooks_count(manager, models, expected_count):
    for model in models:
        rows = await manager.read(model)
        assert len(rows) == expected_count, f"model: {model}"


async def add_collection_helper(manager, file_manager, generate_collections_images):
    params = dict(
        name="collection1",
        image=b"MAIN",
        category_name="category1",
        manager=manager,
        uow_class=FakeUoW,
        generate_images=generate_collections_images,
        file_manager=file_manager,
    )
    return await add_collection(**params)