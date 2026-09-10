import domain
from db import models
from sqlalchemy import inspect


def map_tile_image_to_domain(o: models.TileImage) -> domain.Image:
    return domain.Image(image_id=o.image_id, master_id=o.tile_id, image_path=o.image_path)

def map_tile_image_to_orm(d: domain.Image) -> models.TileImage:
    return models.TileImage(image_id=d.id, tile_id=d.master_id, image_path=d.image_path)


def map_tile_to_domain(o: models.Tile) -> domain.Tile:
    insp = inspect(o)

    images = None
    if "images" not in insp.unloaded:
        images = [map_tile_image_to_domain(img) for img in o.images]

    size_obj = None
    if "size" not in insp.unloaded:
        size_obj = map_size_to_domain(o.size)

    box_obj = None
    if "box" not in insp.unloaded:
        box_obj = map_box_to_domain(o.box)

    category_obj = None
    if "category" not in insp.unloaded:
        #category_obj = domain.Category(id=o.category.id, name=o.category.name)
        category_obj = map_category_to_domain(o.category)

    color = domain.Color(color_name=o.color_name, feature_name=o.feature_name)

    surface = domain.Surface(name=o.surface_name) if o.surface_name else None
    producer = domain.Producer(name=o.producer_name)

    return domain.Tile(
        article=o.id,
        name=o.name,
        boxes_count=o.boxes_count,
        color=color,
        surface=surface,
        producer=producer,
        category=category_obj,
        category_id=o.category_id,
        size=size_obj,  # Либо готовый объект, либо None
        size_id=o.size_id,  # ID есть всегда, берем прямо из колонки плитки!
        box=box_obj,
        box_id=o.box_id,
        images=images,
    )

def map_tile_to_orm(d: domain.Tile) -> models.Tile:
    #orm_images = [models.TileImage(image_path=img.image_path) for img in d.images]
    orm_images = [map_tile_image_to_orm(image) for image in d.images]
    return models.Tile(
        id=d.id,
        name=d.name,
        color_name=d.color.color_name,
        feature_name=d.color.feature_name,
        size_id=d.size.id,
        box_id=d.box.id,
        surface_name=d.surface.name,
        producer_name=d.producer.name,
        category_id=d.category.id,
        boxes_count=d.boxes_count,
        images=orm_images,
    )


def map_size_to_domain(o: models.TileSize) -> domain.Size:
    return domain.Size(
        size_id=o.id, length=o.length, height=o.height, width=o.width
    )

def map_size_to_orm(d: domain.Size) -> models.TileSize:
    return models.TileSize(id=d.id, length=d.length, height=d.height, width=d.width)


def map_color_to_domain(o: models.TileColor) -> domain.Color:
    return domain.Color(color_name=o.color_name, feature_name=o.feature_name)

def map_color_to_orm(d: domain.Color) -> models.TileColor:
    return models.TileColor(color_name=d.color_name, feature_name=d.feature_name)


def map_surface_to_domain(o: models.TileSurface) -> domain.Surface:
    return domain.Surface(name=o.name)

def map_surface_to_orm(d: domain.Surface) -> models.TileSurface:
    return models.TileSurface(name=d.name)


def map_producer_to_domain(o: models.Producer) -> domain.Producer:
    return domain.Producer(name=o.name)

def map_producer_to_orm(d: domain.Producer) -> models.Producer:
    return models.Producer(name=d.name)


def map_box_to_domain(o: models.Box) -> domain.Box:
    return domain.Box(box_id=o.id, weight=o.weight, area=o.area)

def map_box_to_orm(d: domain.Box) -> models.Box:
    return models.Box(id=d.id, weight=d.weight, area=d.area)


def map_category_to_domain(o: models.Category) -> domain.Category:
    return domain.Category(name=o.name, id=o.id)

def map_category_to_orm(d: domain.Category) -> models.Category:
    return models.Category(name=d.name, id=d.id)





