import logging
from pathlib import Path

import aiofiles

from core import config
from domain.tile import *
from repo.Uow import UnitOfWork
from decimal import Decimal


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
    tile_color = await manager.read(TileColor, color_name=color_name, feature_name=feature_name, session=session)
    log.debug("tile_color: %s", tile_color)
    if not tile_color:
        await manager.create(
            TileColor, color_name=color_name, feature_name=feature_name, session=session
        )


async def add_tile_material(material_name: str, manager, session):
    tile_material = await manager.read(
        TileMaterial, name=material_name, session=session
    )
    if not tile_material:
        await manager.create(TileMaterial, name=material_name, session=session)


async def add_producer(producer_name: str, manager, session):
    producer = await manager.read(Producer, name=producer_name, session=session)
    if not producer:
        await manager.create(Producer, name=producer_name, session=session)


async def add_box(box_weight: Decimal, box_area: Decimal, manager, session):
    box = await manager.read(Box, weight=box_weight, area=box_area, session=session)
    if not box:
        return await manager.create(Box, weight=box_weight, area=box_area, session=session)
    else:
        return box


async def add_pallet(pallet_weight: Decimal, pallet_area: Decimal, manager, session):
    pallet = await manager.read(Pallet, weight=pallet_weight, area=pallet_area, session=session)
    if not pallet:
        return await manager.create(Pallet, weight=pallet_weight, area=pallet_area, session=session)
    else:
        return pallet[0]


async def add_tile(
    name: str,
    height: Decimal,
    width: Decimal,
    color: str,
    color_feature: str,
    surface: str,
    material: str,
    producer: str,
    box_weight: Decimal,
    pallet_weight: Decimal,
    box_area: Decimal,
    pallet_area: Decimal,
    image: bytes,
    manager,
):
    path = config.image_path
    upload_dir = Path(path)
    name = Path(name).name
    image_path = upload_dir / name

    async with UnitOfWork(manager._session_factory) as uow:

        await add_tile_size(height, width, manager, uow.session)
        await add_tile_surface(surface, manager, uow.session)
        await add_tile_color(color, color_feature, manager, uow.session)
        await add_tile_material(material, manager, uow.session)
        await add_producer(producer, manager, uow.session)
        box = await add_box(box_weight, box_area, manager, uow.session)
        pallet = await add_pallet(pallet_weight, pallet_area, manager, uow.session)

        tile_record = await manager.create(
            Tile,
            name=name,
            size_height=height,
            size_width=width,
            color_name=color,
            feature_name=color_feature,
            surface_name=surface,
            material_name=material,
            producer_name=producer,
            box_weight = box.get("weight"),
            box_area = box.get("area"),
            pallet_weight=pallet.get("weight"),
            pallet_area=pallet.get("area"),
            image_path=str(image_path),
            session=uow.session,
        )

        upload_dir.mkdir(parents=True, exist_ok=True)
        try:
            async with aiofiles.open(image_path, "xb") as fw:
                await fw.write(image)
        except FileExistsError:
            log.debug("путь %s уже занять", image_path)
            raise

        #tile_record = [map_to_tile_domain(tile) for tile in tile_record]
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


async def delete_tile_color(tiles: list, color_name: str, manager, session):
    tiles = [tile for tile in tiles if tile.get("color_name") == color_name]
    if not tiles:
        log.debug("%s удаляется из справочника", color_name)
        await manager.delete(TileColor, name=color_name, session=session)


async def delete_tile(manager, **filters):

    async with UnitOfWork(manager._session_factory) as uow:
        tiles = await manager.read(Tile, session=uow.session, **filters)
        files_deleted = 0

        await manager.delete(Tile, session=uow.session, **filters)
        all_tiles = await manager.read(Tile, session=uow.session)

        for tile in tiles:
            await delete_tile_size(
                all_tiles, tile.get("size_height"), tile.get("size_width"), manager, uow.session
            )
            await delete_tile_color(
                all_tiles, tile.get("color_name"), manager, uow.session
            )
            image_path = Path(tile["image_path"])
            log.debug("for delete image_path: %s", image_path)
            if image_path.exists():
                image_path.unlink(missing_ok=True)
                files_deleted += 1
                log.info(f"Удален файл: {image_path}")
        log.info("Удалено файлов: %s", files_deleted)
