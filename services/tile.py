import logging

from domain import *
from infra.UoW import UnitOfWork

from .exceptions import FileStorageError

log = logging.getLogger(__name__)


async def add_items(domain_model, manager, session, **filters):
    item = await manager.read(domain_model, **filters, session=session)
    if not item:
        return await manager.create(domain_model, **filters, session=session)
    return item[0]


async def add_tile(
    name: str,
    length: Decimal,
    width: Decimal,
    height: Decimal,
    color_name: str,
    producer_name: str,
    box_weight: Decimal,
    box_area: Decimal,
    boxes_count: int,
    main_image: bytes,
    category_name: str,
    manager,
    images: list[bytes] | list,
    images_generator,
    file_manager,
    color_feature: str = "",
    surface: str | None = None,
    uow_class=UnitOfWork,
):
    async with uow_class(manager) as uow:

        size = await add_items(
            TileSize, manager, uow.session, height=height, width=width, length=length
        )
        if surface:
            await add_items(TileSurface, manager, uow.session, name=surface)
        await add_items(
            TileColor,
            manager,
            uow.session,
            color_name=color_name,
            feature_name=color_feature,
        )
        await add_items(Producer, manager, uow.session, name=producer_name)
        await add_items(Category, manager, uow.session, name=category_name)
        await add_items(
            Slug, manager, uow.session, name=category_name, slug=slugify(category_name)
        )
        box = await add_items(
            Box, manager, uow.session, weight=box_weight, area=box_area
        )
        tile_record = await manager.create(
            Tile,
            name=name,
            size_id=size["id"],
            color_name=color_name,
            category_name=category_name,
            feature_name=color_feature,
            surface_name=surface,
            producer_name=producer_name,
            box_id=box["id"],
            boxes_count=boxes_count,
            session=uow.session,
        )
        images = [img for img in images if img]
        images.insert(0, main_image)
        for n, img in enumerate(images):
            file_name = str(tile_record["id"]) + "-" + str(n)  # type: ignore
            image_path = file_manager.base_product_path(file_name)
            await manager.create(
                TileImage,
                tile_id=tile_record["id"],  # type: ignore
                image_path=str(image_path),
                session=uow.session,
            )
            try:
                async with file_manager.session() as files:
                    await files.save(image_path, img)
                    miniatures = await images_generator.generate_product_variants(img)
                    for layer, miniature in miniatures.items():
                        await files.save_by_layer(file_name, miniature, layer)
            except FileExistsError as exc:
                log.debug("путь %s уже занять", image_path)
                raise FileStorageError(f"путь {image_path} уже занять") from exc
        return tile_record


async def delete_tile(manager, file_manager, uow_class=UnitOfWork, **filters):
    async with uow_class(manager) as uow:
        tiles_to_delete = await manager.read(
            Tile, loaded=["images"], session=uow.session, **filters
        )
        if not tiles_to_delete:
            return []

        del_res = await manager.delete(Tile, session=uow.session, **filters)
        for tile in tiles_to_delete:
            images_paths = tile.images_paths
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


def model_to_update_values(model, **values):
    if model is TileSize:
        res = {"size_id": values["id"]}
    elif model is Box:
        res = {"box_id": values["id"]}
    elif model is TileSurface:
        res = {"surface_name": values["name"]}
    elif model is Producer:
        res = {"producer_name": values["name"]}
    elif model is Category:
        res = {"category_name": values["name"]}
    else:
        res = values
    return res


def set_values_from_db(values: dict, key: str, value_from_db):
    if key not in values:
        values[key] = value_from_db


# async def create_composite(manager, article: int, values, columns, *to_join):
#     model = await manager.read_one(Tile, loaded=list(to_join), id=article)
#     if not model:
#         return
#     for k, v in model.items():
#         if k in columns:
#             k = map_tile_param_to_model_param(k)
#             set_values_from_db(values, k, v)
async def create_composite(manager, article: int, values: dict, columns: tuple, *to_join):
    tile = await manager.read_one(Tile, loaded=list(to_join), id=article)
    if not tile:
        return

    for k, v in tile.to_dict().items():
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
    model_values = await add_items(model, manager, session, **values)
    return model_to_update_values(model, **model_values)


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


# async def update_tile(
#     manager,
#     article: int,
#     uow_class=UnitOfWork,
#     name: str | None = None,
#     size: dict | None = None,
#     color: dict | None = None,
#     producer_name: str | None = None,
#     box: dict | None = None,
#     boxes_count: int | None = None,
#     category_name: str | None = None,
#     surface_name: str | None = None,
# ):
#     params = {
#         k: v
#         for k, v in locals().items()
#         if v is not None and k not in {"manager", "article", "uow_class"}
#     }
#     to_update = {}
#     async with uow_class(manager) as uow:
#         for k, v in params.items():
#             domain_model = map_param_to_domain_model(k)
#             if domain_model is Tile:
#                 to_update.update({k: v})
#                 continue
#             updated_in_model = dict_for_update_model(k, v)
#             updated_fields_in_tile = await create_new_model(
#                 manager, article, domain_model, uow.session, **updated_in_model
#             )
#             to_update.update(updated_fields_in_tile)
#         await manager.update(
#             Tile, session=uow.session, filters=dict(id=article), **to_update
#         )


async def update_tile(
    manager,
    article: int,
    size: SizeUpdate,
    color: ColorUpdate,
    producer_name: ProducerUpdate,
    box: BoxUpdate,
    category_name: CategoryUpdate,
    surface_name: SurfaceUpdate,
    uow_class=UnitOfWork,
    name: str | None = None,
    boxes_count: int | None = None,
):
    params = {
        k: v for k, v in locals().items()
        if v is not None and k not in {"manager", "article", "uow_class", "name", "boxes_count"}
    }

    to_update = {}
    if name is not None: to_update["name"] = name
    if boxes_count is not None: to_update["boxes_count"] = boxes_count

    async with uow_class(manager) as uow:
        commands_needing_read = [cmd for cmd in params.values() if cmd.need_read()]

        if commands_needing_read:
            needed_relations = [cmd.relation_name for cmd in commands_needing_read]
            record = await manager.read_one(Tile, id=article, loaded=needed_relations, session=uow.session)
            tile_flat_dict = record.to_dict() if record else {}

            for cmd in commands_needing_read:
                cmd.set_fields(tile_flat_dict)

        for param in params.values():
            if not param.need_update():
                continue
            new_value = await manager.create(param.domain_model(), session=uow.session)
            for target_field, source_attr in param.output_map.items():
                to_update[target_field] = getattr(new_value, source_attr)

        await manager.update(
            Tile, session=uow.session, filters=dict(id=article), **to_update
        )