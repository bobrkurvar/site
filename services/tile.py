import logging

from domain import *
from services.UoW import UnitOfWork
from typing import Any

from .exceptions import FileStorageError
from slugify import slugify
from .ports import ProductImagesPort, CrudPort

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
    manager: CrudPort,
    images: list[bytes] | list,
    generate_images,
    file_manager: ProductImagesPort,
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
        await add_items(Categories, manager, uow.session, name=category_name)
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
            str_name = str(tile_record["id"]) + "-" + str(n) # type: ignore
            image_path = file_manager.base_product_path(str_name)
            await manager.create(
                TileImages,
                tile_id=tile_record["id"], #type: ignore
                image_path=str(image_path),
                session=uow.session,
            )
            try:
                async with file_manager.session() as files:
                    await files.save(image_path, img)
                    miniatures = await generate_images(img)
                    for layer, miniature in miniatures.items():
                        await files.save_by_layer(image_path, miniature, layer)
            except FileExistsError as exc:
                log.debug("путь %s уже занять", image_path)
                raise FileStorageError(f"путь {image_path} уже занять") from exc
        return tile_record


async def delete_tile(
        manager: CrudPort,
        file_manager: ProductImagesPort,
        uow_class=UnitOfWork,
        **filters
):
    async with uow_class(manager) as uow:
        tiles = await manager.read(
            Tile, to_join=["images"], session=uow.session, **filters
        )
        del_res = await manager.delete(Tile, session=uow.session, **filters)
        for tile in tiles:
            images_paths = tile.get("images_paths", [])
            for image in images_paths:
                await file_manager.delete_product(image)
        return del_res


async def set_composite_parameter(
    manager: CrudPort,
    session,
    article: int,
    main_value,
    mapped: dict,
    for_models: dict,
    main_name: str,
    other_name: str,
    model,
    for_tile_name: str | None = None,
    to_join: list | None = None
):
    to_join = [] if to_join is None else to_join
    for_tile_name = other_name if for_tile_name is None else for_tile_name
    other_value = mapped.setdefault(
        other_name,
        (await manager.read(Tile, id=article, to_join=to_join, session=session))[0][
            for_tile_name
        ],
    )
    #log.debug("OTHER NAME: %s, OTHER VALUE: %s, FOR TILE NAME: %s", other_name, other_value, for_tile_name)
    for_models[model] = {main_name: main_value, other_name: other_value}
    mapped[main_name] = main_value



async def map_to_domain_for_filter(
        article: int,
        manager: CrudPort,
        session,
        **params
):
    for_tile: dict[Any, Any] = {}
    for_models: dict[Any, Any] = {}
    mapped: dict[Any, Any] = {}

    for param, value in params.items():
        for_tile.update(**{param: value})

        if param == "producer_name":
            for_models[Producer] = {"name": value}
        elif param == "category_name":
            for_models[Categories] = {"name": value}
        elif param == "surface_name":
            for_models[TileSurface] = {"name": value}
        elif param == "size":
            for_tile.pop("size")
            for_models[TileSize] = value

        elif param == "feature_name":
            await set_composite_parameter(
                manager,
                session,
                article,
                value,
                mapped,
                for_models,
                param,
                "color_name",
                TileColor
            )

        elif param == "color_name":
            await set_composite_parameter(
                manager,
                session,
                article,
                value,
                mapped,
                for_models,
                param,
                "feature_name",
                TileColor
            )

        elif param == "box_weight":
            for_tile.pop(param)
            await set_composite_parameter(
                manager=manager,
                session=session,
                article=article,
                main_value=value,
                mapped=mapped,
                for_models=for_models,
                main_name="weight",
                other_name="area",
                model=Box,
                for_tile_name="box_area",
                to_join=["box"]
            )


        elif param == "box_area":
            for_tile.pop(param)
            await set_composite_parameter(
                manager=manager,
                session=session,
                article=article,
                main_value=value,
                mapped=mapped,
                for_models=for_models,
                main_name="area",
                other_name="weight",
                model=Box,
                for_tile_name="box_weight",
                to_join=["box"]
            )

    return for_tile, for_models


async def update_tile(manager: CrudPort, article: int, uow_class=UnitOfWork, **params):
    log.debug("PARAMS: %s", params)

    async with uow_class(manager) as uow:
        for_tiles, for_models = await map_to_domain_for_filter(
            article, manager, uow.session, **params
        )
        log.debug("for_models: %s", for_models)
        for model, values in for_models.items():
            item = await add_items(
                model,
                manager,
                uow.session,
                **values,
            )
            if model is Box:
                for_tiles["box_id"] = item["id"]
            elif model is TileSize:
                for_tiles["size_id"] = item["id"]
        log.debug("For tiles: %s For models: %s", for_tiles, for_models)

        await manager.update(
            Tile, filters=dict(id=article), session=uow.session, **for_tiles
        )
