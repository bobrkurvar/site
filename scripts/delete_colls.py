import asyncio
import logging

from adapters.crud import get_db_manager
from domain import Collections, CollectionCategory, Slug
from services.UoW import UnitOfWork

log = logging.getLogger(__name__)


async def delete_colls():
    manager = get_db_manager()
    manager.connect()
    async with UnitOfWork(manager._session_factory) as uow:
        collections = await manager.read(Collections, session=uow.session)
        coll_names = {coll["name"] for coll in collections}
        coll_ids = {coll["id"] for coll in collections}
        coll_category = await manager.read(CollectionCategory)
        slugs = await manager.read(Slug)
        for coll in coll_category:
            collection_id = coll["collection_id"]
            if collection_id not in coll_ids:
                await manager.delete(CollectionCategory, session=uow.session, collection_id=collection_id)
        for slug in slugs:
            slug_name = slug["name"]
            if slug_name not in coll_names:
                await manager.delete(Slug, session=uow.session, name=slug_name)

async def main():
    await delete_colls()


if __name__ == "__main__":
    log.info("Старт")
    asyncio.run(main())
    log.info("Конец")
