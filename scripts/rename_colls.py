import asyncio
import logging
from pathlib import Path

import core.logger
from adapters.crud import get_db_manager
from domain.tile import Collections

log = logging.getLogger(__name__)


async def new_images_paths_for_collections():
    manager = get_db_manager()
    manager.connect()
    collections = await manager.read(Collections)
    for collection in collections:
        old_path = Path(collection["image_path"])
        path_parts = list(Path(old_path).parts)
        path_parts[-1] = f"{collection['name']}"
        new_path = Path(*path_parts)
        log.debug("old path: %s, new path: %s", old_path, new_path)
        old_paths = [
            old_path,
            Path("static/images/collections/catalog") / old_path.name,
        ]
        new_paths = [
            new_path,
            Path("static/images/collections/catalog") / new_path.name,
        ]
        for old, new in zip(old_paths, new_paths):
            try:
                old.rename(new)
            except FileExistsError:
                log.debug("Файл %s уже существует. Пропускаем.", new)
            except FileNotFoundError:
                log.debug("Файл %s не найден.", old)
            await manager.update(
                Collections,
                {
                    "name": collection["name"],
                    "category_name": collection["category_name"],
                },
                image_path=str(new_path),
            )

async def main():
    await new_images_paths_for_collections()


if __name__ == "__main__":
    log.info("Старт")
    asyncio.run(main())
    log.info("Конец")
