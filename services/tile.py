import logging
from pathlib import Path

import aiofiles

from domain.tile import *
from repo.Uow import UnitOfWork

log = logging.getLogger(__name__)


async def add_items(domain_model, manager, session, **filters):
    item = await manager.read(domain_model, **filters, session=session)
    if not item:
        return await manager.create(domain_model, **filters, session=session)
    return item[0]


async def add_tile(
    tile_name: str,
    length: Decimal,
    width: Decimal,
    height: Decimal,
    color_name: str,
    producer_name: str,
    box_weight: Decimal,
    box_area: Decimal,
    boxes_count: int,
    main_image: bytes,
    tile_type: str,
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
        await add_items(Types, manager, uow.session, name=tile_type)
        box = await add_items(
            Box, manager, uow.session, weight=box_weight, area=box_area
        )

        tile_record = await manager.create(
            Tile,
            name=tile_name,
            tile_size_id=size["id"],
            color_name=color_name,
            type_name=tile_type,
            feature_name=color_feature,
            surface_name=surface,
            producer_name=producer_name,
            box_id=box["id"],
            boxes_count=boxes_count,
            session=uow.session,
        )

        upload_dir = upload_root or Path(__name__).parent.parent
        upload_dir = upload_dir / "static" / "images" / "tiles"
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
            except FileExistsError:
                log.debug("путь %s уже занять", image_path)
                raise

        return tile_record


async def delete_tile(manager, **filters):

    async with UnitOfWork(manager._session_factory) as uow:
        tiles = await manager.read(
            Tile, to_join=["images"], session=uow.session, **filters
        )
        files_deleted = 0
        await manager.delete(Tile, session=uow.session, **filters)

        for tile in tiles:
            images_paths = tile["images_paths"]
            project_root = Path(__file__).resolve().parent.parent
            upload_dir_str = str(project_root).replace(r"\app", "")
            absolute_path = Path(upload_dir_str)
            for image in images_paths:
                image_str = image.lstrip("/")
                image_path = absolute_path / image_str
                log.debug("for delete image_path: %s", str(image_path))
                if image_path.exists():
                    image_path.unlink(missing_ok=True)
                    files_deleted += 1
                    log.info(f"Удален файл: {image_path}")
        log.info("Удалено файлов: %s", files_deleted)


async def map_to_domain_for_filter(
    article: int, manager, session, param: str, value, mapped: dict
):
    mapper_for_domain_model = {
        "name": Tile,
        "boxes_count": Tile,
        "tile_type": Types,
        "size": TileSize,
        "color_name": TileColor,
        "color_feature": TileColor,
        "producer": Producer,
        "box_weight": Box,
        "box_area": Box,
        "surface": TileSurface,
    }

    mapper_for_filters = {
        "name": {"name": value},
        "surface": {"name": value},
        "producer": {"name": value},
        "tile_type": {"name": value},
    }
    if param == "boxes_count":
        mapper_for_filters["boxes_count"] = {"boxes_count": int(value)}

    if param == "size":
        length_str, width_str, height_str = value.split()
        mapper_for_filters[param] = {
            "length": Decimal(length_str),
            "width": Decimal(width_str),
            "height": Decimal(height_str),
        }

    elif param == "color_feature":
        color_name = mapped.setdefault(
            "color_name",
            (await manager.read(Tile, id=article, session=session))[0]["color_name"],
        )
        mapper_for_filters[param] = {"color_name": color_name, "feature_name": value}
        mapped["feature_name"] = value

    elif param == "color_name":
        feature_name = mapped.setdefault(
            "feature_name",
            (await manager.read(Tile, id=article, session=session))[0]["feature_name"],
        )
        mapper_for_filters[param] = {"color_name": value, "feature_name": feature_name}
        mapped["color_name"] = value

    elif param == "box_weight":
        box_area = mapped.setdefault(
            "box_area",
            (await manager.read(Tile, to_join=["box"], id=article, session=session))[0][
                "box_area"
            ],
        )
        mapper_for_filters[param] = {
            "weight": Decimal(value),
            "area": Decimal(box_area),
        }
        mapped["box_weight"] = value

    elif param == "box_area":
        box_weight = mapped.setdefault(
            "box_weight",
            (await manager.read(Tile, to_join=["box"], id=article, session=session))[0][
                "box_area"
            ],
        )
        mapper_for_filters[param] = {
            "weight": Decimal(box_weight),
            "area": Decimal(value),
        }
        mapped["box_area"] = value

    return {
        "param": param,
        "domain_model": mapper_for_domain_model[param],
        "filters": mapper_for_filters.get(param, {param: value}),
    }


async def update_tile(manager, article, **params):

    mapper_for_tiles = {
        "surface": "surface_name",
        "producer": "producer_name",
        "size": "tile_size_id",
        "box_weight": "box_id",
        "box_area": "box_id",
        "tile_type": "type_name",
        "color_feature": "feature_name",
    }

    mapper_for_item = {
        "size": "id",
        "box_weight": "id",
        "box_area": "id",
        "producer": "name",
        "tile_type": "name",
        "color_feature": "feature_name",
        "surface": "name",
    }

    mapper_for_type_tile = {"boxes_count": int}

    mapped = {}

    async with UnitOfWork(manager._session_factory) as uow:
        domain_tile_filters = []
        for_tiles = {}
        log.debug("params %s", params)
        for param in params:
            domain_tile_filters.append(
                await map_to_domain_for_filter(
                    article, manager, uow.session, param, params[param], mapped
                )
            )
        log.debug("mapped: %s", mapped)
        log.debug("domain_tile_filters %s", domain_tile_filters)
        for tile_filter in domain_tile_filters:
            cur = tile_filter["param"]
            if cur != "name" and cur != "boxes_count":
                log.debug("param: %s, model: %s", cur, tile_filter["domain_model"])
                item = await add_items(
                    tile_filter["domain_model"],
                    manager,
                    uow.session,
                    **tile_filter["filters"],
                )
                for_tiles.update(
                    **{
                        mapper_for_tiles.get(cur, cur): item[
                            mapper_for_item.get(cur, cur)
                        ]
                    }
                )
            else:
                for_tiles.update(
                    **{
                        mapper_for_tiles.get(cur, cur): mapper_for_type_tile.get(
                            cur, str
                        )(params[cur])
                    }
                )
        log.debug("for_tiles: %s", for_tiles)

        await manager.update(
            Tile, filters=dict(id=article), session=uow.session, **for_tiles
        )
