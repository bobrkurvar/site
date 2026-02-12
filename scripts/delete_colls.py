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
        coll_names = {col["name"] for col in collections}
        coll_category = await manager.read(CollectionCategory)
        for coll in coll_category:
            if coll["collection_name"] not in coll_names:
                await manager.delete(CollectionCategory, session=uow.session, **coll)
                slug = await manager.read(Slug, name=coll["collection_name"])
                if slug:
                    await manager.delete(Slug, name=coll["collection_name"])

async def main():
    await delete_colls()


if __name__ == "__main__":
    log.info("Старт")
    asyncio.run(main())
    log.info("Конец")
