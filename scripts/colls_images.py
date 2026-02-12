import asyncio
import logging
from pathlib import Path

import core.logger
from adapters.crud import get_db_manager
from domain import Collections, CollectionCategory

log = logging.getLogger(__name__)


async def new_images_paths_for_collections():
    manager = get_db_manager()
    manager.connect()
    collections = await manager.read(CollectionCategory, distinct="collection_name")
    for collection in collections:
        collection_name = collection["collection_name"]
        category_name = collection["category_name"]
        old_paths = (
            Path("static/images/base/collections") / (collection_name + '-' + category_name),
            Path("static/images/collections/catalog") / (collection_name + '-' + category_name),
        )
        new_paths = [
            Path("static/images/base/collections") / collection_name,
            Path("static/images/collections/catalog") / collection_name,
        ]
        for old, new in zip(old_paths, new_paths):
            try:
                old.rename(new)
            except FileExistsError:
                print(f"Папка {new} уже существует. Пропускаем.")
            except FileNotFoundError:
                print(f"Папка {old} не найдена.")
            await manager.update(Collections, filters={"name": collection["collection_name"]}, image_path=str(new))


async def main():
    await new_images_paths_for_collections()


if __name__ == "__main__":
    log.info("Старт")
    asyncio.run(main())
    log.info("Конец")
