import asyncio
import logging

from core import conf
from domain.user import Admin
from adapters.repo import get_db_manager
from core.auth import get_password_hash

log = logging.getLogger(__name__)


async def add_admins():
    initial_admins = conf.initial_admins_list
    log.debug("ADMINS: %s", initial_admins)
    manager = get_db_manager()
    for admin in initial_admins:
        log.debug("ADMIN: %s", admin)
        password = get_password_hash(admin["password"])
        log.debug("HASH PASWORD: %s,", password)
        await manager.create(Admin, username=admin["username"], password=password)


async def main():
    await add_admins()


if __name__ == "__main__":
    log.info("Старт")
    asyncio.run(main())
    log.info("Конец")
