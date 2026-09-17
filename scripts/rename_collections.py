# import asyncio
# import logging
#
# from adapters.uow import UnitOfWork
# from db.mapper import registry
# from adapters.db_provider import DbProvider
# from adapters.images import CollectionImagesManager
# from domain import Collection
# from infra.security import calculate_file_hash
# from core import conf
# from pathlib import Path
#
# log = logging.getLogger(__name__)
#
#
# async def rename_collections():
#     db_provider = DbProvider(conf.db_url)
#     file_manager = CollectionImagesManager()
#
#     try:
#         async with UnitOfWork(provider=db_provider, registry=registry) as uow:
#             collections = await uow.db.read(Collection)
#
#             for collection in collections:
#                 old_path = Path(collection.image_path)
#
#                 image_bytes = old_path.read_bytes()
#                 file_hash = calculate_file_hash(image_bytes)
#
#                 new_file_name = file_hash + old_path.suffix.lower()
#                 new_path = file_manager.base_collection_path(new_file_name)
#
#                 if old_path != new_path:
#                     if new_path.exists():
#                         old_path.unlink()
#                     else:
#                         old_path.rename(new_path)
#
#                     await uow.db.update(
#                         Collection,
#                         {"id": collection.id},
#                         image_path=str(new_path),
#                     )
#
#     finally:
#         await db_provider.close()
#
#
# async def main():
#     await rename_collections()
#
#
# if __name__ == "__main__":
#     log.info("Старт")
#     asyncio.run(main())
#     log.info("Конец")
import asyncio
import logging
import shutil
from pathlib import Path

from adapters.uow import UnitOfWork
from db.mapper import registry
from adapters.db_provider import DbProvider
from adapters.images import CollectionImagesManager
from domain import Collection
from infra.security import calculate_file_hash
from core import conf


log = logging.getLogger(__name__)


async def rename_collections():
    db_provider = DbProvider(conf.db_url)
    file_manager = CollectionImagesManager()

    # mapping:
    # старый путь -> канонический путь с hash-именем
    paths_map: dict[str, str] = {}

    # Старые файлы удаляем только после успешного изменения БД.
    files_to_delete: list[Path] = []

    try:
        collection_dir = Path("static/images/base/collections")

        #
        # 1. Сначала приводим файловую систему к новому состоянию.
        #
        for old_path in collection_dir.iterdir():
            if not old_path.is_file():
                continue

            image_bytes = old_path.read_bytes()
            file_hash = calculate_file_hash(image_bytes)

            new_file_name = file_hash + old_path.suffix.lower()
            new_path = file_manager.base_collection_path(new_file_name)

            paths_map[str(old_path)] = str(new_path)

            # Файл уже имеет правильное имя.
            if old_path == new_path:
                continue

            # Новый файл мог быть создан предыдущим запуском.
            if not new_path.exists():
                shutil.copy2(old_path, new_path)

            files_to_delete.append(old_path)

        #
        # 2. Теперь синхронизируем БД с реально найденными файлами.
        #
        async with UnitOfWork(
            provider=db_provider,
            registry=registry,
        ) as uow:
            collections = await uow.db.read(Collection)

            for collection in collections:
                old_path = str(Path(collection.image_path))

                new_path = paths_map.get(old_path)

                # Файла с таким старым путём мы не нашли.
                # Значит ничего с этой записью не делаем.
                if new_path is None:
                    continue

                # Уже правильное значение.
                if old_path == new_path:
                    continue

                await uow.db.update(
                    Collection,
                    {"id": collection.id},
                    image_path=new_path,
                )

        #
        # 3. До этой точки мы дошли только после успешного выхода
        #    из UoW. Теперь старые копии можно удалить.
        #
        for old_path in files_to_delete:
            if old_path.exists():
                old_path.unlink()

    finally:
        await db_provider.close()


async def main():
    await rename_collections()


if __name__ == "__main__":
    log.info("Старт")
    asyncio.run(main())
    log.info("Конец")