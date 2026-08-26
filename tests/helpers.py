from domain import (Box, Category, Collection, Image, Producer, Tile,
                    TileColor, TileSize, TileSurface)
from services.collections import add_collection
from services.tile import add_tile
from tests.fakes import FakeUoW


async def add_collection_helper(
    manager,
    file_manager,
    images_generator,
    collection_name=None,
    category_name=None,
    test_uow_class=True,
):
    collection = Collection(
        name=collection_name if collection_name else "collection1",
        categories=Category(name=category_name if category_name else "category1"),
        image=Image(image_bytes=b"COLLECTION"),
    )
    params = {}
    if test_uow_class:
        params["uow_class"] = FakeUoW
    return await add_collection(
        manager=manager,
        file_manager=file_manager,
        images_generator=images_generator,
        collection=collection,
        **params,
    )


async def add_tile_helper(
    manager,
    file_manager,
    images_generator,
    name: str = "Tile",
    test_uow_class: bool = True,
    need_params: bool = False,
    category_name=None,
    size: TileSize = None,
    color: TileColor = None,
    producer_name=None,
):
    # обёртка на сервисным методом add_tile, которая создана для многоразового использования одного и того же вызова функции
    params = dict(
        name=name,
        size=size if size else TileSize(length=300, width=200, height=10),
        color=color if color else TileColor("color", "feature"),
        producer=Producer(producer_name if producer_name else "producer"),
        box=Box(area=1, weight=30),
        boxes_count=3,
        images=[Image(b"MAIN"), Image(b"A"), Image(b"B")],
        surface=TileSurface("surface"),
        category=Category(category_name if category_name else "category"),
    )
    tile = Tile(**params)
    infra_params = dict(
        manager=manager, file_manager=file_manager, images_generator=images_generator
    )
    if test_uow_class:
        infra_params["uow"] = FakeUoW()
    if need_params:
        return await add_tile(tile, **infra_params), params
    else:
        return await add_tile(tile, **infra_params)


def assert_tile_fields(tile, expected):
    for k, v in expected.items():
        actual = getattr(tile, k)
        assert actual == v, f"{k}: expected {v}, got {actual}"


def assert_size(size, expected: dict):
    assert size.length == expected["length"]
    assert size.width == expected["width"]
    assert size.height == expected["height"]


def assert_box(box, expected):
    # функция для вынесения логики проверки размеров данных о коробке
    assert box.weight == expected["weight"]
    assert box.area == expected["area"]


async def assert_handbooks_count(manager, models, expected_count):
    for model in models:
        rows = await manager.read(model)
        assert (
            len(rows) == expected_count
        ), f"model: {model} count != {expected_count} count = {len(rows)}"


def update_filters(
    length_missing: bool = False,
    width_missing: bool = False,
    height_missing: bool = False,
    weight_missing: bool = False,
    area_missing: bool = False,
    color_name_missing: bool = False,
    feature_name_missing: bool = False,
):
    # новые данные для обновления tile с возможностью пропускать половины ключей
    new_size = {"length": 500, "width": 300, "height": 20}
    if length_missing:
        del new_size["length"]
    if width_missing:
        del new_size["width"]
    if height_missing:
        del new_size["height"]
    new_color = {"color_name": "NewColor", "feature_name": "NewFeature"}
    if color_name_missing:
        del new_color["color_name"]
    if feature_name_missing:
        del new_color["feature_name"]
    new_box = {"weight": 50, "area": 50}
    if area_missing:
        del new_box["area"]
    if weight_missing:
        del new_box["weight"]
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
