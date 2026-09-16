import logging
from pathlib import Path

from contracts.layers import (
    COLLECTIONS,
    DETAILS,
    LAYERS_IMAGE_FORMAT,
    PRODUCTS,
    SLIDES,
)
from image_worker import IMAGE_PRESETS, generate_image_variant as generate_variant_bytes

log = logging.getLogger(__name__)

BASE_PATH = Path("static/images/base")
BASE_DIR = Path("static/images")

PROCESS_MAP = {
    PRODUCTS: [PRODUCTS, DETAILS],
    COLLECTIONS: [COLLECTIONS],
    SLIDES: [SLIDES],
}

OUTPUT_DIRS = {
    PRODUCTS: BASE_DIR / "products" / "catalog",
    COLLECTIONS: BASE_DIR / "collections" / "catalog",
    DETAILS: BASE_DIR / "products" / "details",
    SLIDES: BASE_DIR / "slides",
}


def generate_image_variant(
    input_path: Path | str,
    target: str,
    output_dir: Path | None = None,
) -> Path | None:
    if target not in IMAGE_PRESETS:
        raise ValueError(f"Unknown image preset: {target}")

    input_path = Path(input_path)
    if not input_path.exists():
        log.warning("Исходный файл не найден: %s", input_path)
        return None

    output_dir = output_dir or OUTPUT_DIRS[target]
    output_dir.mkdir(parents=True, exist_ok=True)

    extension = f".{LAYERS_IMAGE_FORMAT.lower()}"
    output_path = output_dir / input_path.with_suffix(extension).name

    # Уже сгенерированный слой не пересчитываем.
    if output_path.exists():
        log.debug("Image already exists: %s", output_path)
        return output_path

    image_bytes = input_path.read_bytes()
    variant_bytes, generated_extension = generate_variant_bytes(image_bytes, target)

    # Защита от рассинхронизации контракта и имени выходного файла.
    if generated_extension != extension:
        output_path = output_dir / input_path.with_suffix(generated_extension).name

    output_path.write_bytes(variant_bytes)

    log.info("Generated %s image: %s", target, output_path)
    return output_path


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

                log.debug("Запуск генерации слоя %s", preset)
                generate_image_variant(image_file, preset)


if __name__ == "__main__":
    log.info("Старт генерации изображений")
    process_all_folders()
    log.info("Генерация изображений завершена")
