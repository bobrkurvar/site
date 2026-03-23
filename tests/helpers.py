from decimal import Decimal
from tests.fakes import FakeUoW
from services.tile import add_tile
from services.collections import add_collection


async def add_tile_helper_with_control_filters(manager, file_manager, images_generator, test_uow_class: bool=True, need_params: bool=False, category_name=None, size: str = None, producer: str = None, color_name: str=None):
    params = dict(
        name = "Tile",
        length = Decimal(300),
        width = Decimal(200),
        height = Decimal(10),
        color_name = color_name if color_name else "color",
        producer_name = producer if producer else "producer",
        box_weight = Decimal(30),
        box_area = Decimal(1),
        boxes_count = 3,
        main_image = b"MAIN",
        category_name = category_name if category_name else "category",
        manager = manager,
        images = [b"A", b"B"],
        color_feature = "feature",
        surface = "surface",
        file_manager = file_manager,
        images_generator = images_generator,
    )
    if size:
        length, width, height = size.split()
        params["length"], params["width"], params["height"] = Decimal(length), Decimal(width), Decimal(height)
    if test_uow_class: params["uow_class"] = FakeUoW
    if need_params:
        return await add_tile(**params), params
    else:
        return await add_tile(**params)


async def add_tile_helper(manager, file_manager, images_generator, test_uow_class: bool=True, need_params: bool=False):
    # обёртка на сервисным методом add_tile, которая создана для многоразового использования одного и того же вызова функции
    # для уменьшения объёма кода
    # params = dict(
    #     name = "Tile",
    #     length = Decimal(300),
    #     width = Decimal(200),
    #     height = Decimal(10),
    #     color_name = "color",
    #     producer_name = "producer",
    #     box_weight = Decimal(30),
    #     box_area = Decimal(1),
    #     boxes_count = 3,
    #     main_image = b"MAIN",
    #     category_name = "category",
    #     manager = manager,
    #     images = [b"A", b"B"],
    #     color_feature = "feature",
    #     surface = "surface",
    #     file_manager = file_manager,
    #     images_generator = images_generator,
    # )
    # if test_uow_class: params["uow_class"] = FakeUoW
    # if need_params:
    #     return await add_tile(**params), params
    # else:
    #     return await add_tile(**params)
    return await add_tile_helper_with_control_filters(manager, file_manager, images_generator, test_uow_class, need_params)

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


async def add_collection_helper(manager, file_manager, images_generator, collection_name: str | None = None, category_name: str | None = None, test_uow_class: bool=True):
    params = dict(
        name="collection1",
        image=b"MAIN",
        category_name="category1",
        manager=manager,
        images_generator=images_generator,
        file_manager=file_manager,
    )
    if test_uow_class: params["uow_class"] = FakeUoW
    if category_name: params["category_name"] = category_name

    return await add_collection(**params)


def update_filters(length_missing: bool=False, width_missing: bool = False, height_missing: bool = False, weight_missing: bool = False, area_missing: bool = False, color_name_missing: bool = False, feature_name_missing: bool = False):
    # новые данные для обновления tile с возможностью пропускать половины ключей
    new_size = {"length":Decimal(500), "width": Decimal(300), "height": Decimal(20)}
    if length_missing: del new_size["length"]
    if width_missing: del new_size["width"]
    if height_missing: del new_size["height"]
    new_color = {"color_name": "NewColor", "feature_name": "NewFeature"}
    if color_name_missing: del new_color["color_name"]
    if feature_name_missing: del new_color["feature_name"]
    new_box = {"weight": Decimal(50), "area": Decimal(50)}
    if area_missing: del new_box["area"]
    if weight_missing: del new_box["weight"]
    return dict(
        name="NewTile",
        size=new_size,
        color=new_color,
        box=new_box,
        producer_name="NewProducer",
        boxes_count=5,
        category_name="NewCategory",
        surface_name="NewSurface",
    )


