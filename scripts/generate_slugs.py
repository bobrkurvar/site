# import asyncio
# import logging
#
# from slugify import slugify
#
# from adapters.db import build_crud
# from domain import Category, Collection, Slug
#
# log = logging.getLogger(__name__)
#
#
# async def add_slugs():
#     manager = get_db_manager()
#     manager.connect()
#     collections = await manager.read(Collection)
#     categories = await manager.read(Category)
#     full_list = {col["name"] for col in collections} | {
#         category["name"] for category in categories
#     }
#     for item in full_list:
#         slug = slugify(item)
#         await manager.create(Slug, name=item, slug=slug)
#
#
# async def main():
#     await add_slugs()
#
#
# if __name__ == "__main__":
#     log.info("Старт")
#     asyncio.run(main())
#     log.info("Конец")
