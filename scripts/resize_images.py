import logging
from pathlib import Path

from core import logger
from services.images import IMAGE_PRESETS, generate_image_variant  # твоя функция и пресеты

log = logging.getLogger(__name__)

BASE_PATH = Path("static/images/base")

PROCESS_MAP = {
    "products": ["products", "details"],  # исходные товары
    "collections": ["collections"],  # исходные коллекции
    "slides": ["slides"]
}


def process_all_folders():
    for src_dir, presets in PROCESS_MAP.items():
        folder_path = BASE_PATH / src_dir
        if not folder_path.exists() or not folder_path.is_dir():
            log.warning("Исходная папка не найдена: %s", folder_path)
            continue

        log.info("Обрабатываем папку: %s", folder_path)

        for image_file in folder_path.iterdir():
            log.debug("images_file: %s", image_file)
            if not image_file.is_file():
                log.debug("not is file")
                continue
            for preset in presets:
                if preset not in IMAGE_PRESETS:
                    log.warning("Preset не найден: %s", preset)
                    continue
                log.debug("Запуск функции resize")
                generate_image_variant(image_file, preset)


if __name__ == "__main__":
    log.info("Старт генерации изображений")
    process_all_folders()
    log.info("Генерация изображений завершена")
