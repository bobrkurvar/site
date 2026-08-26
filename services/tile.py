import asyncio
import logging

from domain import *
from infra.security import calculate_file_hash
from adapters.uow import UnitOfWork

log = logging.getLogger(__name__)


async def add_items(domain_obj, manager, session, **filters):
    item = await manager.read_one(type(domain_obj), **filters, session=session)
    if not item:
        item = await manager.create(domain_obj, session=session)
    return item


async def add_tile(
    tile: Tile,
    manager,
    images_generator,
    file_manager,
    uow_class=UnitOfWork,
):
    async with uow_class(manager) as uow:
        tile.size = await add_items(
            tile.size,
            manager,
            uow.session,
            height=tile.size.height,
            width=tile.size.width,
            length=tile.size.length,
        )
        if tile.surface:
            await add_items(tile.surface, manager, uow.session, name=tile.surface.name)
        await add_items(
            tile.color,
            manager,
            uow.session,
            color_name=tile.color.color_name,
            feature_name=tile.color.feature_name,
        )
        await add_items(tile.producer, manager, uow.session, name=tile.producer.name)
        await add_items(tile.category, manager, uow.session, name=tile.category.name)
        slug = Slug(name=tile.category.name)
        await add_items(slug, manager, uow.session, name=tile.category.name)
        tile.box = await add_items(
            tile.box, manager, uow.session, weight=tile.box.weight, area=tile.box.area
        )
        async with file_manager.session() as files:
            for img in tile.images:
                img_bytes = img.consume_bytes()
                file_name = await asyncio.to_thread(calculate_file_hash, img_bytes)
                image_path = file_manager.base_product_path(file_name)
                img.image_path = str(image_path)
                try:
                    await files.save(image_path, img_bytes)
                    miniatures = await images_generator.generate_product_variants(
                        img_bytes
                    )
                    for layer, miniature in miniatures.items():
                        await files.save_by_layer(file_name, miniature, layer)
                except FileExistsError:
                    log.debug("путь %s уже занять", image_path)
                    pass
        return await manager.create(tile, session=uow.session)


async def delete_tile(manager, file_manager, uow_class=UnitOfWork, **filters):
    async with uow_class(manager) as uow:
        tiles_to_delete = await manager.read(
            Tile, loaded=["images"], session=uow.session, **filters
        )
        if not tiles_to_delete:
            return []

        del_res = await manager.delete(Tile, session=uow.session, **filters)
        for tile in tiles_to_delete:
            images_paths = [image.image_path for image in tile.images]
            for image in images_paths:
                await file_manager.delete_product(image)
        return del_res


def dict_for_update_model(tile_field: str, value):
    if tile_field in ("size", "box", "color"):
        res = value
    elif tile_field.endswith("name"):
        res = {"name": value}
    else:
        res = {tile_field: value}
    return res


def model_to_update_values(model, domain_obj, **values):
    if model is TileSize:
        res = {"size_id": domain_obj.id}
    elif model is Box:
        res = {"box_id": domain_obj.id}
    elif model is TileSurface:
        res = {"surface_name": domain_obj.name}
    elif model is Producer:
        res = {"producer_name": domain_obj.name}
    elif model is Category:
        res = {"category_name": domain_obj.name}
    else:
        res = values
    return res


def set_values_from_db(values: dict, key: str, value_from_db):
    if key not in values:
        values[key] = value_from_db


def extract_composite_fields(tile: Tile) -> dict:
    return {
        "id": tile.article,
        "name": tile.name,
        "boxes_count": tile.boxes_count,
        "category_name": tile.category_name,
        "producer_name": tile.producer_name,
        "surface_name": tile.surface_name,
        "size_length": tile.size.length if tile.size else None,
        "size_width": tile.size.width if tile.size else None,
        "size_height": tile.size.height if tile.size else None,
        "size_id": tile.size_id,
        "box_area": tile.box.area if tile.box else None,
        "box_weight": tile.box.weight if tile.box else None,
        "box_id": tile.box_id,
        "color_name": tile.color_name,
        "feature_name": tile.feature_name,
    }


async def create_composite(
    manager, article: int, values: dict, columns: tuple, *to_join
):
    tile = await manager.read_one(Tile, loaded=list(to_join), id=article)
    if not tile:
        return

    for k, v in extract_composite_fields(tile).items():
        if k in columns:
            k = map_tile_param_to_model_param(k)
            set_values_from_db(values, k, v)


def map_tile_param_to_model_param(tile_param: str):
    if tile_param in (
        "size_length",
        "size_width",
        "size_height",
        "box_area",
        "box_weight",
    ):
        return tile_param.split("_")[1]
    else:
        return tile_param


async def create_new_model(manager, article: int, model, session, **values):
    if model is TileSize:
        await create_composite(
            manager,
            article,
            values,
            ("size_length", "size_width", "size_height"),
            "size",
        )
    elif model is Box:
        await create_composite(
            manager, article, values, ("box_area", "box_weight"), "box"
        )
    elif model is TileColor:
        await create_composite(
            manager, article, values, ("color_name", "feature_name"), "color"
        )
    log.debug("model: %s values: %s", model, values)
    new_instance = model(**values)
    domain_obj = await add_items(new_instance, manager, session, **values)
    return model_to_update_values(model, domain_obj, **values)


def map_param_to_domain_model(param_name: str):
    mapper = {
        "name": Tile,
        "boxes_count": Tile,
        "size": TileSize,
        "color": TileColor,
        "producer_name": Producer,
        "box": Box,
        "category_name": Category,
        "surface_name": TileSurface,
    }
    return mapper[param_name]


async def update_tile(
    manager,
    article: int,
    uow_class=UnitOfWork,
    name: str | None = None,
    size: dict | None = None,
    color: dict | None = None,
    producer_name: str | None = None,
    box: dict | None = None,
    boxes_count: int | None = None,
    category_name: str | None = None,
    surface_name: str | None = None,
):
    params = {
        k: v
        for k, v in locals().items()
        if v is not None and k not in {"manager", "article", "uow_class"}
    }
    to_update = {}
    async with uow_class(manager) as uow:
        for k, v in params.items():
            domain_model = map_param_to_domain_model(k)
            if domain_model is Tile:
                to_update.update({k: v})
                continue
            updated_in_model = dict_for_update_model(k, v)
            updated_fields_in_tile = await create_new_model(
                manager, article, domain_model, uow.session, **updated_in_model
            )
            to_update.update(updated_fields_in_tile)
        await manager.update(
            Tile, session=uow.session, filters=dict(id=article), **to_update
        )


