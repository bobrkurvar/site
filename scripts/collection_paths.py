import asyncio
import logging
from pathlib import Path

from adapters.db import build_crud
from adapters.db_provider import DbProvider
from core import conf
from domain import Collection, Slug

log = logging.getLogger(__name__)


async def main():
    db_provider = DbProvider(url=conf.db_url)
    manager = build_crud(db_provider.session_factory)

    collections = await manager.read(Collection)
    collection_names = [collection.name for collection in collections]

    slugs = await manager.read(Slug, name=collection_names)
    collection_slug = {slug.name: slug.slug for slug in slugs}

    # Используем Path для базовых директорий
    base_dir = Path("static/images/base/collections")
    catalog_dir = Path("static/images/collections/catalog")

    for col in collections:
        # 1. Безопасно получаем slug (защита от KeyError)
        col_slug = collection_slug.get(col.name)
        if not col_slug:
            log.warning(f"Пропуск: Для коллекции '{col.name}' не найден Slug.")
            continue

        # 2. Обязательно приводим col.id к строке!
        old_id_str = str(col.id)

        old_paths = [
            base_dir / old_id_str,
            catalog_dir / old_id_str,
        ]
        new_paths = [
            base_dir / col_slug,
            catalog_dir / col_slug,
        ]

        # Флаг успешного переноса файлов
        files_moved_successfully = True

        # 3. Сначала переименовываем файлы
        for old_p, new_p in zip(old_paths, new_paths):
            try:
                if not old_p.exists() and new_p.exists():
                    log.info(f"Уже переименовано: {new_p}")
                    continue

                old_p.rename(new_p)
                log.info(f"Переименовано: {old_p.name} -> {new_p.name}")
            except FileNotFoundError:
                log.warning(f"Файл не найден, пропуск: {old_p}")
                # Решай сам: считать ли это ошибкой. Скорее всего, путь в БД всё равно надо обновить
            except Exception as e:
                log.error(f"Ошибка при переименовании {old_p}: {e}")
                files_moved_successfully = False
                break  # Прерываем переименование для этой коллекции

        # 4. И ТОЛЬКО ПОТОМ обновляем базу данных
        if files_moved_successfully:
            new_db_path = str(base_dir / col_slug)

            await manager.update(Collection, {"name": col.name}, image_path=new_db_path)
            log.info(f"База обновлена для коллекции '{col.name}'")


if __name__ == "__main__":
    asyncio.run(main())
