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
