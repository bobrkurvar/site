from pathlib import Path
import logging
from domain.tile import Tile
from core import config
import aiofiles

log = logging.getLogger(__name__)

async def add_tile(name: str, height: float, width: float, image: bytes, manager):

    path = config.image_path
    upload_dir = Path(path)
    name = Path(name).name
    image_path = upload_dir / name
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_created = False

    try:
        async with aiofiles.open(image_path, "xb") as fw:
            await fw.write(image)
        file_created = True
    except FileExistsError:
        log.error('не удалось записать файл')

    try:
        return await manager.create(Tile, name=name, size_height=height, size_width=width, image_path=str(image_path))
    except Exception:
        log.error('БД упала, удаляем файл')
        if file_created:
            image_path.unlink(missing_ok=True)
        raise

async def delete_tile(manager, **filters):

    tiles = await manager.read(Tile, **filters)

    files_deleted = 0

    try:
        for tile in tiles:
            image_path = Path(tile['image_path'])
            if image_path.exists():
                image_path.unlink(missing_ok=True)
                files_deleted += 1
                log.info(f"Удален файл: {image_path}")
        log.info("Удалено файлов: %s", files_deleted)

    except Exception as e:
        log.error(f"Ошибка при удалении файлов")
        raise

    await manager.delete(Tile, **filters)

