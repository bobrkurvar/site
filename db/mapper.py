from sqlalchemy import inspect
from db import models
import domain


def map_catalog_to_orm(d: domain.Tile) -> models.Catalog:
    return models.Catalog(
        id=d.id,
        name=d.name,
        color_name=d.color.color_name,
        feature_name=d.color.feature_name,
        size_id=d.size.id,
        box_id=d.box.id,
        surface_name=d.surface.name,
        producer_name=d.producer.name,
        category_name=d.category.name,
        boxes_count=d.boxes_count
    )


def map_category_to_orm(d: domain.Category) -> models.Category:
    return models.Category(name=d.name)


def map_tile_image_to_orm(d: domain.TileImage) -> models.TileImage:
    return models.TileImage(image_id=d.id, tile_id=d.tile_id, image_path=d.image_path)


def map_collection_to_orm(d: domain.Collection) -> models.Collection:
    return models.Collection(id=d.id, name=d.name, image_path=d.image_path)


def map_collection_category_to_orm(d: domain.CollectionCategory) -> models.CollectionCategory:
    return models.CollectionCategory(
        collection_id=d.collection_id,
        category_name=d.category_name
    )

def map_collection_category_to_domain(o: models.CollectionCategory) -> domain.CollectionCategory:
    return domain.CollectionCategory(
        collection_id=o.collection_id,
        category_name=o.category_name
    )

def map_size_to_orm(d: domain.TileSize) -> models.TileSize:
    return models.TileSize(id=d.id, length=d.length, height=d.height, width=d.width)


def map_color_to_orm(d: domain.TileColor) -> models.TileColor:
    return models.TileColor(color_name=d.color_name, feature_name=d.feature_name)


def map_surface_to_orm(d: domain.TileSurface) -> models.TileSurface:
    return models.TileSurface(name=d.name)


def map_producer_to_orm(d: domain.Producer) -> models.Producer:
    return models.Producer(name=d.name)


def map_box_to_orm(d: domain.Box) -> models.Box:
    return models.Box(id=d.id, weight=d.weight, area=d.area)


def map_admin_to_orm(d: domain.Admin) -> models.Admin:
    return models.Admin(username=d.username, password=d.password)


def map_slug_to_orm(d: domain.Slug) -> models.Slug:
    return models.Slug(name=d.name, slug=d.slug)


def map_catalog_to_domain(o: models.Catalog) -> domain.Tile:
    insp = inspect(o)

    size = None
    if "size" not in insp.unloaded and o.size is not None:
        size = domain.TileSize(
            size_id=o.size.id,
            height=o.size.height,
            width=o.size.width,
            length=o.size.length,
        )

    box = None
    if "box" not in insp.unloaded and o.box is not None:
        box = domain.Box(
            box_id=o.box.id,
            weight=o.box.weight,
            area=o.box.area,
        )

    color = domain.TileColor(
        color_name=o.color_name,
        feature_name=o.feature_name
    )

    surface = domain.TileSurface(name=o.surface_name) if o.surface_name else None
    producer = domain.Producer(name=o.producer_name)
    category = domain.Category(name=o.category_name)

    return domain.Tile(
        size=size,
        color=color,
        name=o.name,
        surface=surface,
        box=box,
        boxes_count=o.boxes_count,
        producer=producer,
        category_name=category,
        article=o.id,
    )

def map_category_to_domain(o: models.Category) -> domain.Category:
    return domain.Category(name=o.name)


def map_tile_image_to_domain(o: models.TileImage) -> domain.TileImage:
    return domain.TileImage(image_id=o.image_id, tile_id=o.tile_id, image_path=o.image_path)


def map_collection_to_domain(o: models.Collection) -> domain.Collection:
    return domain.Collection(id=o.id, name=o.name, image_path=o.image_path)


def map_collection_category_to_domain(o: models.CollectionCategory) -> domain.CollectionCategory:
    insp = inspect(o)

    return domain.CollectionCategory(
        collection_id=o.collection_id,
        category_name=o.category_name
    )


def map_size_to_domain(o: models.TileSize) -> domain.TileSize:
    return domain.TileSize(size_id=o.id, length=o.length, height=o.height, width=o.width)


def map_color_to_domain(o: models.TileColor) -> domain.TileColor:
    return domain.TileColor(color_name=o.color_name, feature_name=o.feature_name)


def map_surface_to_domain(o: models.TileSurface) -> domain.TileSurface:
    return domain.TileSurface(name=o.name)


def map_producer_to_domain(o: models.Producer) -> domain.Producer:
    return domain.Producer(name=o.name)


def map_box_to_domain(o: models.Box) -> domain.Box:
    return domain.Box(box_id=o.id, weight=o.weight, area=o.area)


def map_admin_to_domain(o: models.Admin) -> domain.Admin:
    return domain.Admin(username=o.username, password=o.password)


def map_slug_to_domain(o: models.Slug) -> domain.Slug:
    return domain.Slug(name=o.name, slug=o.slug)


class MapperRegistry:
    def __init__(self):
        self._models = {}          # domain_cls -> orm_model
        self._to_orm_funcs = {}    # domain_cls -> func
        self._to_domain_funcs = {} # orm_model -> func (Внимание: ключ - ORM класс!)

    def register(self, domain_cls, orm_model, to_orm, to_domain):
        self._models[domain_cls] = orm_model
        self._to_orm_funcs[domain_cls] = to_orm
        self._to_domain_funcs[orm_model] = to_domain

    def get_model(self, domain_cls):
        return self._models[domain_cls]

    def to_orm(self, domain_obj):
        domain_cls = type(domain_obj)
        func = self._to_orm_funcs.get(domain_cls)
        if not func:
            raise RuntimeError(f"Маппер в ORM не найден для {domain_cls}")
        return func(domain_obj)

    def to_domain(self, orm_obj):
        orm_cls = type(orm_obj)
        func = self._to_domain_funcs.get(orm_cls)
        if not func:
            raise RuntimeError(f"Маппер в Домен не найден для {orm_cls}")
        return func(orm_obj)




registry = MapperRegistry()
registry.register(domain.Tile,models.Catalog,map_catalog_to_orm,map_catalog_to_domain)
registry.register(domain.Category, models.Category, map_category_to_orm, map_category_to_domain)
registry.register(domain.Collection, models.Collection, map_collection_to_orm, map_collection_to_domain)
registry.register(domain.CollectionCategory, models.CollectionCategory, map_collection_category_to_orm, map_collection_category_to_domain)
registry.register(domain.TileSize, models.TileSize, map_size_to_orm, map_size_to_domain)
registry.register(domain.TileColor, models.TileColor, map_color_to_orm, map_color_to_domain)
registry.register(domain.TileSurface, models.TileSurface, map_surface_to_orm, map_surface_to_domain)
registry.register(domain.Producer, models.Producer, map_producer_to_orm, map_producer_to_domain)
registry.register(domain.Box, models.Box, map_box_to_orm, map_box_to_domain)
registry.register(domain.TileImage, models.TileImage, map_tile_image_to_orm, map_tile_image_to_domain)
registry.register(domain.Admin, models.Admin, map_admin_to_orm, map_admin_to_domain)
registry.register(domain.Slug, models.Slug, map_slug_to_orm, map_slug_to_domain)
registry.register(domain.CollectionCategory, models.CollectionCategory, map_collection_category_to_orm, map_collection_category_to_domain)