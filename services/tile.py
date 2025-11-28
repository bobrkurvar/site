import logging
from decimal import Decimal
from pathlib import Path

import aiofiles

from core import config
from domain.tile import *
from repo.Uow import UnitOfWork

log = logging.getLogger(__name__)


async def add_tile_surface(name: str, manager, session):
    tile_surface = await manager.read(TileSurface, name=name, session=session)
    if not tile_surface:
        await manager.create(TileSurface, name=name, session=session)


async def add_tile_size(height: Decimal, width: Decimal, manager, session):
    tile_size = await manager.read(
        TileSize, height=height, width=width, session=session
    )
    if not tile_size:
        await manager.create(TileSize, height=height, width=width, session=session)


async def add_tile_color(color_name: str, feature_name: str, manager, session):
    tile_color = await manager.read(
        TileColor, color_name=color_name, feature_name=feature_name, session=session
    )
    if not tile_color:
        await manager.create(
            TileColor, color_name=color_name, feature_name=feature_name, session=session
        )


async def add_producer(producer_name: str, manager, session):
    producer = await manager.read(Producer, name=producer_name, session=session)
    if not producer:
        await manager.create(Producer, name=producer_name, session=session)


async def add_box(box_weight: Decimal, box_area: Decimal, manager, session):
    box = await manager.read(Box, weight=box_weight, area=box_area, session=session)
    if not box:
        return await manager.create(
            Box, weight=box_weight, area=box_area, session=session
        )
    else:
        return box[0]


async def add_tile(
    tile_name: str,
    height: Decimal,
    width: Decimal,
    color: str,
    producer: str,
    box_weight: Decimal,
    box_area: Decimal,
    boxes_count: int,
    main_image: bytes,
    manager,
    images: list[bytes] | list,
    color_feature: str = "",
    surface: str | None = None,
):

    async with UnitOfWork(manager._session_factory) as uow:

        await add_tile_size(height, width, manager, uow.session)
        if surface:
            await add_tile_surface(surface, manager, uow.session)
        await add_tile_color(color, color_feature, manager, uow.session)
        await add_producer(producer, manager, uow.session)
        box = await add_box(box_weight, box_area, manager, uow.session)

        tile_record = await manager.create(
            Tile,
            name=tile_name,
            size_height=height,
            size_width=width,
            color_name=color,
            feature_name=color_feature,
            surface_name=surface,
            producer_name=producer,
            box_weight=box.get("weight"),
            box_area=box.get("area"),
            boxes_count = boxes_count,
            session=uow.session,
        )

        path = config.image_path
        upload_dir = Path(path)
        upload_dir.mkdir(parents=True, exist_ok=True)
        images.insert(0, main_image)
        for n, img in enumerate(images):
            name = Path(str(tile_record['id']) + '-' + str(n)).name
            image_path = upload_dir / name
            await manager.create(TileImages, tile_id=tile_record['id'], image_path=str(image_path), session=uow.session)

            try:
                async with aiofiles.open(image_path, "xb") as fw:
                    await fw.write(img)
            except FileExistsError:
                log.debug("путь %s уже занять", image_path)
                raise

        return tile_record


async def delete_tile_size(tiles: list, height: float, width: float, manager, session):
    tiles = [
        tile
        for tile in tiles
        if tile.get("size_height") == height and tile.get("size_width") == width
    ]
    if not tiles:
        log.debug("%s, %s удаляется из справочника", height, width)
        await manager.delete(TileSize, height=height, width=width, session=session)


async def delete_tile_color(tiles: list, color_name: str, feature_name: str, manager, session):
    tiles = [tile for tile in tiles if tile.get("color_name") == color_name and tile.get("feature_name") == feature_name]
    if not tiles:
        log.debug("%s удаляется из справочника", color_name)
        await manager.delete(TileColor, color_name=color_name, feature_name=feature_name, session=session)


async def delete_tile(manager, **filters):

    async with UnitOfWork(manager._session_factory) as uow:
        tiles = await manager.read(Tile, to_join=['images'], session=uow.session, **filters)
        files_deleted = 0

        await manager.delete(Tile, session=uow.session, **filters)
        all_tiles = await manager.read(Tile, session=uow.session)

        for tile in tiles:
            await delete_tile_size(
                all_tiles,
                tile.get("size_height"),
                tile.get("size_width"),
                manager,
                uow.session,
            )
            await delete_tile_color(
                all_tiles, tile.get("color_name"), tile.get("feature_name"), manager, uow.session
            )
            images_paths = tile["images_paths"]
            absolute_path = (Path(__file__).resolve().parent.parent / "static").parent
            for image in images_paths:
                image_str = image.lstrip('/')
                image_path = absolute_path / image_str
                log.debug("for delete image_path: %s", image_path)
                if image_path.exists():
                    image_path.unlink(missing_ok=True)
                    files_deleted += 1
                    log.info(f"Удален файл: {image_path}")
        log.info("Удалено файлов: %s", files_deleted)
