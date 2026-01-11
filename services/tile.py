import logging
from pathlib import Path

import aiofiles

from domain.tile import *
from repo.Uow import UnitOfWork
from services.images import generate_image_variant_bg

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
    color_feature: str = "",
    surface: str | None = None,
    fs=aiofiles,
    uow_class=UnitOfWork,
    upload_root=None,
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
        upload_dir = upload_root or Path(__name__).parent.parent
        upload_dir = upload_dir / "static" / "images" / "base" / "products"
        upload_dir.mkdir(parents=True, exist_ok=True)
        images = [img for img in images if img]
        images.insert(0, main_image)
        for n, img in enumerate(images):
            name = Path(str(tile_record["id"]) + "-" + str(n)).name
            image_path = upload_dir / name
            log.debug("image_path: %s", image_path)
            await manager.create(
                TileImages,
                tile_id=tile_record["id"],
                image_path=str(image_path),
                session=uow.session,
            )

            try:
                async with fs.open(image_path, "xb") as fw:
                    await fw.write(img)
                generate_image_variant_bg(image_path, "products")
                generate_image_variant_bg(image_path, "details")
            except FileExistsError:
                log.debug("путь %s уже занять", image_path)
                raise
        return tile_record


async def delete_tile(manager, uow_class=UnitOfWork, upload_root=None, **filters):

    async with uow_class(manager._session_factory) as uow:
        tiles = await manager.read(
            Tile, to_join=["images"], session=uow.session, **filters
        )
        files_deleted = 0
        await manager.delete(Tile, session=uow.session, **filters)

        for tile in tiles:
            images_paths = tile["images_paths"]
            upload_dir = upload_root or Path(__file__).parent.parent
            for image in images_paths:
                log.debug("image from db: %s", image)
                image_str = image.lstrip("/").lstrip("\\")
                image_path = upload_dir / Path(image_str)
                log.debug("for delete image_path: %s", str(image_path))
                if image_path.exists():
                    image_path.unlink(missing_ok=True)
                    files_deleted += 1
                    log.info(f"Удален файл: {image_path}")
                product_catalog_path = (
                    upload_dir
                    / "static"
                    / "images"
                    / "products"
                    / "catalog"
                    / Path(image).name
                )
                product_details_path = (
                    upload_dir
                    / "static"
                    / "images"
                    / "products"
                    / "details"
                    / Path(image).name
                )
                other_paths = [product_catalog_path, product_details_path]
                for i in other_paths:
                    if i.exists():
                        i.unlink(missing_ok=True)
                        files_deleted += 1
                        log.info(f"Удален файл: {i}")

        log.info("Удалено файлов: %s", files_deleted)


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
