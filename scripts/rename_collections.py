import asyncio
import logging

from adapters.uow import UnitOfWork
from db.mapper import registry
from adapters.db_provider import DbProvider
from adapters.images import CollectionImagesManager
from domain import Collection
from infra.security import calculate_file_hash
from core import conf
from pathlib import Path

log = logging.getLogger(__name__)


async def rename_collections():
    db_provider = DbProvider(conf.db_url)
    file_manager = CollectionImagesManager()

    try:
        async with UnitOfWork(provider=db_provider, registry=registry) as uow:
            collections = await uow.db.read(Collection)

            for collection in collections:
                old_path = Path(collection.image_path)

                image_bytes = old_path.read_bytes()
                file_hash = calculate_file_hash(image_bytes)

                new_file_name = file_hash + old_path.suffix.lower()
                new_path = file_manager.base_collection_path(new_file_name)

                if old_path != new_path:
                    if new_path.exists():
                        old_path.unlink()
                    else:
                        old_path.rename(new_path)

                    await uow.db.update(
                        Collection,
                        {"id": collection.id},
                        image_path=str(new_path),
                    )

    finally:
        await db_provider.close()


async def main():
    await rename_collections()


if __name__ == "__main__":
    log.info("Старт")
    asyncio.run(main())
    log.info("Конец")
