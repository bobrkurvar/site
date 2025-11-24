import logging
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


async def add_tile_size(height:float, width: float, manager, session):
    tile_size = await manager.read(TileSize, height=height, width=width, session=session)
    if not tile_size:
        await manager.create(TileSize, height=height, width=width, session=session)


async def add_tile_color(color_name: str, feature_name: str, manager, session):
    tile_color_feature = await manager.read(TileColorFeature, name=feature_name, session=session)
    log.debug("tile_color_feature: %s", tile_color_feature)
    if not tile_color_feature:
        await manager.create(TileColorFeature, name=feature_name, session=session)

    tile_color = await manager.read(TileColor, name=color_name, session=session)
    log.debug("tile_color: %s", tile_color)
    if not tile_color:
        await manager.create(TileColor, name=color_name, feature_name=feature_name, session=session)


async def add_tile_material(material_name: str, manager, session):
    tile_material = await manager.read(TileMaterial, name=material_name, session=session)
    if not tile_material:
        await manager.create(TileMaterial, name=material_name, session=session)


async def add_producer(producer_name: str, manager, session):
    producer = await manager.read(Producer, name=producer_name, session=session)
    if not producer:
        await manager.create(Producer, name=producer_name, session=session)

async def add_box_weight(box_weight: float, manager, session):
    weight = await manager.read(BoxWeight, weight=box_weight, session=session)
    if not weight:
        await manager.create(BoxWeight, weight=box_weight, session=session)

async def add_pallet_weight(pallet_weight: float, manager, session):
    weight = await manager.read(PalletWeight, weight=pallet_weight, session=session)
    if not weight:
        await manager.create(PalletWeight, weight=pallet_weight, session=session)

async def add_tile(
    name: str,
    height: float,
    width: float,
    color: str,
    color_feature: str,
    surface: str,
    material: str,
    producer: str,
    box_weight: float,
    pallet_weight: float,
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
        await add_box_weight(box_weight, manager, uow.session)
        await add_pallet_weight(pallet_weight, manager, uow.session)

        tile_record = await manager.create(
            Tile,
            name=name,
            size_height=height,
            size_width=width,
            color_name=color,
            surface_name=surface,
            material_name = material,
            producer_name = producer,
            image_path=str(image_path),
            session = uow.session
        )

        upload_dir.mkdir(parents=True, exist_ok=True)
        try:
            async with aiofiles.open(image_path, "xb") as fw:
                await fw.write(image)
        except FileExistsError:
            log.debug('путь %s уже занять', image_path)
            raise

        return tile_record


async def delete_tile(manager, **filters):

    async with UnitOfWork(manager._session_factory) as uow:
        tiles = await manager.read(Tile, session = uow.session, **filters)

        files_deleted = 0

        await manager.delete(Tile, session = uow.session, **filters)

        for tile in tiles:
            image_path = Path(tile["image_path"])
            log.debug('for delete image_path: %s', image_path)
            if image_path.exists():
                image_path.unlink(missing_ok=True)
                files_deleted += 1
                log.info(f"Удален файл: {image_path}")
        log.info("Удалено файлов: %s", files_deleted)


