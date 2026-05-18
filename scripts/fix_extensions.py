import logging
from pathlib import Path
from PIL import Image
from core.logger import setup_logging
import asyncio
from adapters.db import build_crud
from adapters.db_provider import DbProvider
from core import conf
from domain import TileImage, Collection
from infra.security import calculate_file_hash

setup_logging()


log = logging.getLogger(__name__)

# Папка внутри контейнера, куда примонтированы картинки
TARGET_DIR = Path("static/images")


def fix_fs():
    if not TARGET_DIR.exists():
        log.error(f"Директория {TARGET_DIR} не найдена! Проверь volumes в docker-compose.")
        return

    log.info(f"Начало сканирования директории: {TARGET_DIR}")

    fixed_count = 0
    skipped_count = 0

    for file_path in TARGET_DIR.rglob('*'):
        if file_path.is_file() and not file_path.suffix:
            try:
                # Открываем Pillow, чтобы узнать реальный формат файла
                with Image.open(file_path) as img:
                    fmt = img.format.lower()

                    # Маппим форматы в расширения
                    ext = f".{fmt}"
                    if fmt == "jpeg":
                        ext = ".jpg"

                    new_path = file_path.with_suffix(ext)

                    # Физически переименовываем файл на диске
                    file_path.rename(new_path)
                    log.info(f"Успешно переименован: {file_path.name} -> {new_path.name}")
                    fixed_count += 1

            except IOError:
                # Если это не картинка или файл поврежден
                log.warning(f"Файл {file_path.name} не является валидным изображением. Пропуск.")
                skipped_count += 1
            except Exception as e:
                log.error(f"Ошибка при обработке {file_path.name}: {e}")
                skipped_count += 1

    log.info(f"Сканирование завершено. Переименовано: {fixed_count}, пропущено: {skipped_count}")


async def main():
    fix_fs()
    db_provider = DbProvider(url=conf.db_url)
    manager = build_crud(db_provider.session_factory)
    models = TileImage, Collection
    for model in models:
        items = await manager.read(model)
        for item in items:
            image_path = item.image_path
            path_obj = Path(image_path)
            parent_dir = path_obj.parent
            stem = path_obj.stem
            matching_files = list(parent_dir.glob(f"{stem}.*"))
            if matching_files:
                real_file = matching_files[0]
                extension = real_file.suffix
                if model is TileImage:
                    file_bytes = await asyncio.to_thread(real_file.read_bytes)
                    file_hash = await asyncio.to_thread(calculate_file_hash, file_bytes)
                    new_filename = f"{file_hash}{extension}"
                else:
                    new_filename = f"{stem}{extension}"

                new_file_path = real_file.with_name(new_filename)
                if real_file != new_file_path:
                    real_file.rename(new_file_path)
                    log.info(f"Переименован на диске: {real_file.name} -> {new_filename}")
                new_db_path = (path_obj.parent / new_filename).as_posix()
                log.info(f"Переименован: {real_file.name} -> {new_filename}")
                await manager.update(model, {"image_path": image_path}, image_path=new_db_path)

            else:
                log.warning(f"Файл для записи {image_path} не найден ни с одним расширением")




if __name__ == "__main__":
    asyncio.run(main())