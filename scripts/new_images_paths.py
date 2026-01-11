import asyncio
import logging

from core import logger
from domain.tile import Collections, TileImages
from repo import get_db_manager

log = logging.getLogger(__name__)


async def new_images_paths_for_products():
    manager = get_db_manager()
    images_paths = await manager.read(TileImages)
    for path in images_paths:
        new_path = path["image_path"].split("\\")
        new_path[2] = "base"
        new_path.append(new_path[3])
        new_path[3] = "products"
        new_path = "\\".join(new_path)
        await manager.update(
            TileImages, {"image_id": path["image_id"]}, image_path=new_path
        )


async def new_images_paths_for_colletions():
    manager = get_db_manager()
    collections = await manager.read(Collections)
    for collection in collections:
        new_path = collection["image_path"].split("\\")
        new_path[2] = "base"
        new_path.append(new_path[3])
        new_path[3] = "collections"
        new_path = "\\".join(new_path)
        await manager.update(
            Collections,
            {"name": collection["name"], "category_name": collection["category_name"]},
            image_path=new_path,
        )


async def main():
    await new_images_paths_for_products()
    await new_images_paths_for_colletions()


if __name__ == "__main__":
    log.info("Старт")
    asyncio.run(main())
    log.info("Конец")
