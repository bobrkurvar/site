import asyncio
import logging
from pathlib import Path

from adapters.repo import get_db_manager
from domain.tile import Collections, TileImages

log = logging.getLogger(__name__)


async def new_images_paths_for_products():
    manager = get_db_manager()
    images_paths = await manager.read(TileImages)
    for path in images_paths:
        path_parts = list(Path(path).parts)
        path_parts[2] = "base"
        path_parts.append(path_parts[3])
        path_parts[3] = "products"
        new_path = Path(*path_parts)
        await manager.update(
            TileImages, {"image_id": path["image_id"]}, image_path=str(new_path)
        )


async def new_images_paths_for_collcetions():
    manager = get_db_manager()
    collections = await manager.read(Collections)
    for collection in collections:
        path_parts = list(Path(collection["image_path"]).parts)
        path_parts[2] = "base"
        path_parts.append(path_parts[3])
        path_parts[3] = "collections"
        new_path = Path(*path_parts)
        await manager.update(
            Collections,
            {"name": collection["name"], "category_name": collection["category_name"]},
            image_path=str(new_path),
        )


async def main():
    await new_images_paths_for_products()
    await new_images_paths_for_collcetions()


if __name__ == "__main__":
    log.info("Старт")
    asyncio.run(main())
    log.info("Конец")
