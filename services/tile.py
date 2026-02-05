import logging

from domain.tile import *
from services.UoW import UnitOfWork

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
    generate_images,
    file_manager,
    color_feature: str = "",
    surface: str | None = None,
    uow_class=UnitOfWork,
):
    async with uow_class(manager._session_factory) as uow:

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
        #file_manager.set_path("static/images/base/products")
        images = [img for img in images if img]
        images.insert(0, main_image)
        for n, img in enumerate(images):
            str_name = str(tile_record["id"]) + "-" + str(n)
            image_path = file_manager.base_product_path(str_name)
            await manager.create(
                TileImages,
                tile_id=tile_record["id"],
                image_path=str(image_path),
                session=uow.session,
            )
            try:
                await file_manager.save(image_path, img)
                miniatures = await generate_images(img)
                for layer, miniature in miniatures.items():
                    await file_manager.save_by_layer(image_path, miniature, layer)
            except TypeError:
                log.debug("generate_image_variant_callback  или save_files не получили нужную функцию")
                raise
            except FileExistsError:
                log.debug("путь %s уже занять", image_path)
                raise
        return tile_record


async def delete_tile(
        manager,
        file_manager,
        uow_class=UnitOfWork,
        **filters
):

    async with uow_class(manager._session_factory) as uow:
        tiles = await manager.read(
            Tile, to_join=["images"], session=uow.session, **filters
        )
        del_res = await manager.delete(Tile, session=uow.session, **filters)
        for tile in tiles:
            images_paths = tile.get("images_paths", [])
            #file_manager.set_path('static/images/products')
            for image in images_paths:
                file_manager.delete_product(image)
                # product_catalog_path = (
                #     file_manager.upload_dir
                #     / "catalog"
                #     /  file_manager.file_name(image)
                # )
                # product_details_path = (
                #     file_manager.upload_dir
                #     / "details"
                #     / file_manager.file_name(image)
                # )
                # all_paths = [image, product_catalog_path, product_details_path]
                # file_manager.delete(all_paths)
        return del_res

async def map_to_domain_for_filter(article: int, manager, session, **params):
    for_tile = {}
    for_models = {}
    mapped = {}

    for param, value in params.items():
        if param == "name":
            for_tile.update(name=value)

        elif param == "producer_name":
            for_tile.update(producer_name=value)
            for_models[Producer] = {"name": value}

        elif param == "category_name":
            for_tile.update(category_name=value)
            for_models[Categories] = {"name": value}

        elif param == "surface_name":
            for_tile.update(surface_name=value)
            for_models[TileSurface] = {"name": value}

        elif param == "boxes_count":
            for_tile.update(boxes_count=int(value))

        elif param == "size":
            length_str, width_str, height_str = value.split()
            for_models[TileSize] = {
                "length": Decimal(length_str),
                "width": Decimal(width_str),
                "height": Decimal(height_str),
            }

        elif param == "feature_name":
            color_name = mapped.setdefault(
                "color_name",
                (await manager.read(Tile, id=article, session=session))[0][
                    "color_name"
                ],
            )
            for_tile.update(feature_name=value)
            for_models[TileColor] = {"color_name": color_name, "feature_name": value}
            mapped["feature_name"] = value

        elif param == "color_name":
            feature_name = mapped.setdefault(
                "feature_name",
                (await manager.read(Tile, id=article, session=session))[0][
                    "feature_name"
                ],
            )
            for_models[TileColor] = {"color_name": value, "feature_name": feature_name}
            for_tile.update(color_name=value)
            mapped["color_name"] = value

        elif param == "box_weight":
            box_area = mapped.setdefault(
                "box_area",
                (
                    await manager.read(
                        Tile, to_join=["box"], id=article, session=session
                    )
                )[0]["box_area"],
            )
            for_models[Box] = {
                "weight": Decimal(value),
                "area": Decimal(box_area),
            }
            mapped["box_weight"] = value

        elif param == "box_area":
            box_weight = mapped.setdefault(
                "box_weight",
                (
                    await manager.read(
                        Tile, to_join=["box"], id=article, session=session
                    )
                )[0]["box_area"],
            )
            for_models[Box] = {
                "weight": Decimal(box_weight),
                "area": Decimal(value),
            }
            mapped["box_area"] = value

    return for_tile, for_models


async def update_tile(manager, article, uow_class=UnitOfWork, **params):
    log.debug("PARAMS: %s", params)

    async with uow_class(manager._session_factory) as uow:
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

        log.debug("for_tiles: %s", for_tiles)

        await manager.update(
            Tile, filters=dict(id=article), session=uow.session, **for_tiles
        )
