from pathlib import Path
import logging
from domain.tile import Tile

log = logging.getLogger(__name__)

async def add_tile(name: str, price: float, image, manager):
    upload_dir = Path("static/images").absolute()
    upload_dir.mkdir(parents=True, exist_ok=True)
    image_path = upload_dir / name

    file_exists = image_path.exists()
    file_created = False
    try:
        if not file_exists:
            with open(image_path, "wb") as fw:
                fw.write(await image.read())
            file_created = True
    except Exception:
        log.error('не удалось записать файл')
        raise

    try:
        return await manager.create(Tile, name=name, price=price, image_path=str(image_path))
    except Exception:
        log.error('БД упала, удаляем файл')
        if file_created:
            image_path.unlink(missing_ok=True)
        raise

async def delete_tile(manager, tile_id: int | None = None, name: str | None = None):
    image_path = None
    upload_dir = Path("static/images").absolute()
    if name:
        image_path = upload_dir / name
    else:
        if tile_id is not None:
            tile = await manager.read(Tile, ident_val=tile_id)
            image_path = Path(tile[0].get("image_path"))
    try:
        if image_path:
            image_path.unlink(missing_ok=True)
            files_deleted = 1
        else:
            files_deleted = 0
            for file_path in upload_dir.iterdir():
                if file_path.is_file():
                    file_path.unlink(missing_ok=True)
                    files_deleted += 1
                    log.info(f"Удален файл: {file_path}")
        log.info("Удалено файлов: %s", files_deleted)

    except Exception as e:
        log.error(f"Ошибка при удалении файлов из {upload_dir}: {e}")
        raise

    if tile_id is not None:
        log.debug("удаление по tile_id: %s", tile_id)
        return await manager.delete(Tile, ident_val=tile_id)
    if name is not None:
        log.debug("удаление по name: %s", name)
        return await manager.delete(Tile, ident='name', ident_val=name)
    await manager.delete(Tile)

