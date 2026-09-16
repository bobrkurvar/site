from domain import (
    Category,
    Collection,
    Image,
    Tile,
    Size,
    Surface,
    Producer,
    Box,
    Color
)
from services.collections import add_collection


def make_default_tile():
    return Tile(
        name="Tile",
        size=Size(length=300, width=200, height=10),
        color=Color("color", "feature"),
        producer=Producer("producer"),
        box=Box(area=1, weight=30),
        boxes_count=3,
        images=[Image(b"MAIN"), Image(b"A"), Image(b"B")],
        surface=Surface("surface"),
        category=Category("category"),
    )


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


# def assert_size(size, expected: dict):
#     assert size.length == expected["length"]
#     assert size.width == expected["width"]
#     assert size.height == expected["height"]
#
#
# def assert_box(box, expected):
#     # функция для вынесения логики проверки размеров данных о коробке
#     assert box.weight == expected["weight"]
#     assert box.area == expected["area"]


async def assert_handbooks_count(db, models, expected_count):
    for model in models:
        rows = await db.read(model)
        assert (
            len(rows) == expected_count
        ), f"model: {model} count != {expected_count} count = {len(rows)}"


def update_filters(
    tile: Tile,
    length_missing: bool = False,
    width_missing: bool = False,
    height_missing: bool = False,
    weight_missing: bool = False,
    area_missing: bool = False,
    color_name_missing: bool = False,
    feature_name_missing: bool = False,
):
    # новые данные для обновления tile с возможностью пропускать половины ключей
    size = {"length": 500, "width": 300, "height": 20}
    box = {"weight": 50, "area": 50}
    color = {"color_name": "NewColor", "feature_name": "NewFeature"}

    if length_missing:
        del size["length"]
    if width_missing:
        del size["width"]
    if height_missing:
        del size["height"]

    if weight_missing:
        del box["weight"]
    if area_missing:
        del box["area"]

    if color_name_missing:
        del color["color_name"]
    if feature_name_missing:
        del color["feature_name"]

    service_values = {
        "name": "NewTile",
        "size": size,
        "color": color,
        "box": box,
        "producer_name": "NewProducer",
        "boxes_count": 5,
        "category_name": "NewCategory",
        "surface_name": "NewSurface",
    }

    expected = {
        "name": "NewTile",
        "boxes_count": 5,

        "producer": Producer("NewProducer"),
        "category": Category("NewCategory"),
        "surface": Surface("NewSurface"),

        "size": Size(
            length=size.get("length", tile.size.length),
            width=size.get("width", tile.size.width),
            height=size.get("height", tile.size.height),
        ),
        "box": Box(
            weight=box.get("weight", tile.box.weight),
            area=box.get("area", tile.box.area),
        ),
        "color": Color(
            name=color.get("color_name", tile.color.name),
            feature=color.get("feature_name", tile.color.feature),
        ),
    }

    return service_values, expected


async def create_tiles(uow, category_id: int | None = None, collection_name: str | None = None, count: int = 1, handbooks = None):
    async with uow:
        if handbooks is None:
            size = await uow.db.create(Size(length=300, width=200, height=10))
            box = await uow.db.create(Box(area=1, weight=30))
            producer = await uow.db.create(Producer(f"producer"))
            color = await uow.db.create(Color(f"color", f"feature"))
            handbooks = size, box, producer, color
        else:
            size, box, producer, color = handbooks
        about_category = {}
        if category_id is None:
            category = await uow.db.create(Category("category"))
            about_category["category"] = category
        else:
            about_category["category_id"] = category_id

        tiles = []
        for i in range(count):
            name = f"Tile{i}" if collection_name is None else f"Tile{i} \"{collection_name}\""
            tile = Tile(
                name=name,
                size=size,
                color=color,
                producer=producer,
                box=box,
                boxes_count=3,
                images=[Image(b"MAIN"), Image(b"A"), Image(b"B")],
                **about_category
            )
            tile = await uow.db.create(tile)
            tiles.append(tile)
        return tiles, handbooks