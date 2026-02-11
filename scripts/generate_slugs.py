import asyncio
import logging

from adapters.crud import get_db_manager
from domain import Collections, Categories, Slug
from slugify import slugify

log = logging.getLogger(__name__)


async def add_slugs():
    manager = get_db_manager()
    manager.connect()
    collections = await manager.read(Collections)
    categories = await manager.read(Categories)
    full_list = {col["name"] for col in collections} | {category["name"] for category in categories}
    for item in full_list:
        slug = slugify(item)
        await manager.create(Slug, name=item, slug=slug)


async def main():
    await add_slugs()


if __name__ == "__main__":
    log.info("Старт")
    asyncio.run(main())
    log.info("Конец")
