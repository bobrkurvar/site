import domain
from domain import (Admin, Box, Category, Collection, CollectionCategory,
                    Image, Producer, Slug, Tile, TileColor, TileSize,
                    TileSurface)

#
#
# class DomainToOrmMapper:
#     domain_model_to_orm_fields_mapper = {
#         Tile: (
#             "id",
#             "name",
#             "box_id",
#             "color_name",
#             "feature_name",
#             "surface_name",
#             "producer_name",
#             "boxes_count",
#             "category_name",
#             "size_id",
#         ),
#         Category: ("name",),
#         TileImage: ("image_id", "tile_id", "image_path"),
#         Collection: ("id", "name", "image_path"),
#         CollectionCategory: (
#             "collection_id",
#             "collection_name",
#             "category_name",
#             "image_path",
#         ),
#         TileSize: ("id", "length", "width", "height"),
#         TileColor: ("color_name", "feature_name"),
#         TileSurface: ("name",),
#         Producer: ("name",),
#         Box: ("id", "weight", "area"),
#         Admin: ("username", "password"),
#         Slug: ("name", "slug"),
#     }
#
#     def to_orm_dict(self, d_obj):
#         return
#
#     @classmethod
#     def fields(cls, domain_model):
#         return cls.domain_model_to_orm_fields_mapper[domain_model]




def map_catalog_to_orm(d: domain.Tile) -> dict:
    return dict(
        id=d.id,
        name=d.name,
        color_name=d.color.color_name,
        feature_name=d.color.feature_name,
        size_id=d.size.id,
        box_id=d.box.id,
        surface_name=d.surface.name,
        producer_name=d.producer.name,
        category_name=d.category.name,
        boxes_count=d.boxes_count,
    )


def map_category_to_orm(d: domain.Category) -> dict:
    return dict(name=d.name)


def map_tile_image_to_orm(d: domain.Image) -> dict:
    return dict(image_id=d.id, tile_id=d.tile_id, image_path=d.image_path)


def map_collection_to_orm(d: domain.Collection) -> dict:
    return dict(id=d.id, name=d.name, image_path=d.image_path)


def map_collection_category_to_orm(d: domain.CollectionCategory) -> dict:
    return dict(collection_id=d.collection_id, category_name=d.category_name)


def map_collection_category_to_domain(o: dict) -> domain.CollectionCategory:
    return domain.CollectionCategory(
        collection_id=o["collection_id"], category_name=o["category_name"]
    )


def map_size_to_orm(d: domain.TileSize) -> dict:
    return dict(id=d.id, length=d.length, height=d.height, width=d.width)


def map_color_to_orm(d: domain.TileColor) -> dict:
    return dict(color_name=d.color_name, feature_name=d.feature_name)


def map_surface_to_orm(d: domain.TileSurface) -> dict:
    return dict(name=d.name)


def map_producer_to_orm(d: domain.Producer) -> dict:
    return dict(name=d.name)


def map_box_to_orm(d: domain.Box) -> dict:
    return dict(id=d.id, weight=d.weight, area=d.area)


def map_admin_to_orm(d: domain.Admin) -> dict:
    return dict(username=d.username, password=d.password)


def map_slug_to_orm(d: domain.Slug) -> dict:
    return dict(name=d.name, slug=d.slug)


def map_catalog_to_domain(o: dict) -> domain.Tile:
    color = domain.TileColor(
        color_name=o.get("color_name"), feature_name=o.get("feature_name")
    )
    category = domain.Category(name=o.get("category_name"))
    producer = domain.Producer(name=o.get("producer_name"))
    surface = None
    if o.get("surface_name"):
        surface = domain.TileSurface(name=o["surface_name"])
    # объекты заглушки, но с правильным id
    size = None
    if o.get("size_id") is not None:
        size = domain.TileSize(1, 1, 1, size_id=o.get("size_id"))

    box = None
    if o.get("box_id") is not None:
        box = domain.Box(1, 1, box_id=o.get("box_id"))

    return domain.Tile(
        article=o.get("id"),
        name=o.get("name"),
        size=size,
        color=color,
        surface=surface,
        box=box,
        boxes_count=o.get("boxes_count", 0),
        producer=producer,
        category=category,
    )


def map_category_to_domain(o: dict) -> domain.Category:
    return domain.Category(name=o["name"])


def map_tile_image_to_domain(o: dict) -> domain.Image:
    return domain.Image(
        image_id=o["image_id"], tile_id=o["tile_id"], image_path=o["image_path"]
    )


def map_collection_to_domain(o: dict) -> domain.Collection:
    return domain.Collection(
        collection_id=o["id"], name=o["name"], image_path=o["image_path"]
    )


def map_size_to_domain(o: dict) -> domain.TileSize:
    return domain.TileSize(
        size_id=o["id"], length=o["length"], height=o["height"], width=o["width"]
    )


def map_color_to_domain(o: dict) -> domain.TileColor:
    return domain.TileColor(color_name=o["color_name"], feature_name=o["feature_name"])


def map_surface_to_domain(o: dict) -> domain.TileSurface:
    return domain.TileSurface(name=o["name"])


def map_producer_to_domain(o: dict) -> domain.Producer:
    return domain.Producer(name=o["name"])


def map_box_to_domain(o: dict) -> domain.Box:
    return domain.Box(box_id=o["id"], weight=o["weight"], area=o["area"])


def map_admin_to_domain(o: dict) -> domain.Admin:
    return domain.Admin(username=o["username"], password=o["password"])


def map_slug_to_domain(o: dict) -> domain.Slug:
    return domain.Slug(name=o["name"], slug=o["slug"])


class MapperRegistry:
    def __init__(self):
        self._to_orm_funcs = {}  # domain_cls -> func
        self._to_domain_funcs = {}  # orm_model -> func (Внимание: ключ - ORM класс!)

    def register(self, domain_cls, to_orm, to_domain):
        self._to_orm_funcs[domain_cls] = to_orm
        self._to_domain_funcs[domain_cls] = to_domain

    def to_orm(self, domain_obj):
        domain_cls = type(domain_obj)
        func = self._to_orm_funcs.get(domain_cls)
        if not func:
            raise RuntimeError(f"Маппер в ORM не найден для {domain_cls}")
        return func(domain_obj)

    def to_domain(self, domain_cls: type, orm_dict: dict):
        func = self._to_domain_funcs.get(domain_cls)
        if not func:
            raise RuntimeError(f"Маппер в Домен не найден для {domain_cls}")

        return func(orm_dict)


registry = MapperRegistry()
registry.register(domain.Tile, map_catalog_to_orm, map_catalog_to_domain)
registry.register(domain.Category, map_category_to_orm, map_category_to_domain)
registry.register(domain.Collection, map_collection_to_orm, map_collection_to_domain)
registry.register(
    domain.CollectionCategory,
    map_collection_category_to_orm,
    map_collection_category_to_domain,
)
registry.register(domain.TileSize, map_size_to_orm, map_size_to_domain)
registry.register(domain.TileColor, map_color_to_orm, map_color_to_domain)
registry.register(domain.TileSurface, map_surface_to_orm, map_surface_to_domain)
registry.register(domain.Producer, map_producer_to_orm, map_producer_to_domain)
registry.register(domain.Box, map_box_to_orm, map_box_to_domain)
registry.register(domain.Image, map_tile_image_to_orm, map_tile_image_to_domain)
registry.register(domain.Admin, map_admin_to_orm, map_admin_to_domain)
registry.register(domain.Slug, map_slug_to_orm, map_slug_to_domain)
registry.register(
    domain.CollectionCategory,
    map_collection_category_to_orm,
    map_collection_category_to_domain,
)
