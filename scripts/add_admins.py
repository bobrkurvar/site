import asyncio
import logging

from adapters.db import build_crud
from adapters.db_provider import DbProvider
from core import conf
from domain import Admin, AlreadyExistsError, NotFoundError
from infra.security import get_hash

log = logging.getLogger(__name__)


async def add_admins():
    db_provider = DbProvider(conf.db_url)
    try:
        initial_admins = conf.initial_admins_list
        log.debug("ADMINS: %s", initial_admins)
        manager = build_crud(db_provider.session_factory)
        try:
            await manager.delete(Admin)
        except NotFoundError:
            pass
        for admin in initial_admins:
            log.debug("ADMIN: %s", admin)
            password = get_hash(admin["password"])
            log.debug("HASH PASWORD: %s,", password)
            try:
                await manager.create(
                    Admin(username=admin["username"], password=password)
                )
            except AlreadyExistsError:
                log.warning("user already exists")
    finally:
        await db_provider.close()


async def main():
    await add_admins()


if __name__ == "__main__":
    log.info("Старт")
    asyncio.run(main())
    log.info("Конец")
