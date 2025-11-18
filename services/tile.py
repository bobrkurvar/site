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
    tile_color_feature = await manager.read(TileColorFeature, name=feature_name)
    if not tile_color_feature:
        await manager.create(TileColorFeature, name=feature_name, session=session)

    tile_color = await manager.read(TileColor, name=color_name, session=session)
    if not tile_color:
        await manager.create(TileColor, name=color_name, session=session)

async def add_tile(
    name: str,
    height: float,
    width: float,
    color: str,
    color_feature: str,
    surface: str,
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

        tile_record = await manager.create(
            Tile,
            name=name,
            size_height=height,
            size_width=width,
            color_name=color,
            surface_name=surface,
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

    tiles = await manager.read(Tile, **filters)

    files_deleted = 0

    await manager.delete(Tile, **filters)

    try:
        for tile in tiles:
            image_path = Path(tile["image_path"])
            if image_path.exists():
                image_path.unlink(missing_ok=True)
                files_deleted += 1
                log.info(f"Удален файл: {image_path}")
        log.info("Удалено файлов: %s", files_deleted)

    except Exception as e:
        log.error(f"Ошибка при удалении файлов")
        raise

