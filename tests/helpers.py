from domain import (
    Category,
    Collection,
    Image,
)
from services.collections import add_collection


async def add_collection_helper(
    uow, file_manager, images_generator, category: Category, collection_name=None
):
    collection = Collection(
        name=collection_name if collection_name else "collection1",
        categories=category,
        image=Image(image_bytes=b"COLLECTION"),
    )
    return await add_collection(
        uow=uow,
        file_manager=file_manager,
        images_generator=images_generator,
        collection=collection,
    )


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


async def assert_handbooks_count(db, models, expected_count):
    for model in models:
        rows = await db.read(model)
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
