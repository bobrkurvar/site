import asyncio
import logging

from adapters.crud import get_db_manager
from domain import Collections, CollectionCategory

log = logging.getLogger(__name__)


async def delete_colls():
    manager = get_db_manager()
    manager.connect()
    collections = await manager.read(Collections)
    coll_names = {col["name"] for col in collections}
    coll_category = await manager.read(CollectionCategory)
    for coll in coll_category:
        if coll["collection_name"] not in coll_names:
            await manager.delete(CollectionCategory, **coll)

async def main():
    await delete_colls()


if __name__ == "__main__":
    log.info("Старт")
    asyncio.run(main())
    log.info("Конец")
