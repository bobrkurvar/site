import logging
from pathlib import Path

from PIL import Image, ImageOps

from core import logger
from image_worker import IMAGE_PRESETS  # твоя функция и пресеты

log = logging.getLogger(__name__)

BASE_PATH = Path("static/images/base")

PROCESS_MAP = {
    "products": ["products", "details"],  # исходные товары
    "collections": ["collections"],  # исходные коллекции
    "slides": ["slides"],
}

BASE_DIR = Path("static/images")
OUTPUT_DIRS = {
    "products": BASE_DIR / "products" / "catalog",
    "collections": BASE_DIR / "collections" / "catalog",
    "details": BASE_DIR / "products" / "details",
    "slides": BASE_DIR / "slides",
}


def resize_image(
    img: Image.Image,
    target_size: tuple[int, int],
    mode: str,
) -> Image.Image:
    if mode == "fit":
        img.thumbnail(target_size, Image.LANCZOS)
        return img

    if mode == "cover":
        return ImageOps.fit(
            img,
            target_size,
            method=Image.LANCZOS,
            centering=(0.5, 0.5),
        )

    raise ValueError(f"Unknown resize mode: {mode}")


def save_image(image: Image.Image, path: Path, form: str, quality: int):
    image.save(
        path,
        form,
        quality=quality,
        optimize=True,
        progressive=True,
    )


def generate_image_variant(
    input_path: Path | str, target: str, quality: int = 82, output_dir=None
):
    """
    Генерирует вариант изображения для сайта.

    - сохраняет пропорции
    - не апскейлит маленькие изображения
    - идемпотентна
    """

    if target not in IMAGE_PRESETS:
        raise ValueError(f"Unknown image preset: {target}")

    input_path = Path(input_path)

    preset = IMAGE_PRESETS[target]
    width, height = preset["size"]
    mode = preset["mode"]
    output_dir = output_dir or OUTPUT_DIRS[target]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / input_path.name

    if output_path.exists():
        log.debug("Image already exists: %s", output_path)
        return output_path

    if not input_path.exists():
        return

    with Image.open(input_path) as img:
        img = img.convert("RGB")
        smaller_width = width is not None and img.width < width
        smaller_height = height is not None and img.height < height
        # защита от апскейла
        if smaller_width or smaller_height:
            log.warning(
                "Image smaller than target (%s < %s), saving original size",
                img.size,
                (width, height),
            )
            resized = img
        else:
            target_size = (
                width if width is not None else img.width,
                height if height is not None else img.height,
            )
            resized = resize_image(img, target_size, mode)

        output_format = output_path.suffix.lstrip(".").upper()
        if not output_format:
            output_format = "JPEG"  # дефолтный формат для файлов без расширения
        if not input_path.exists():
            return

        save_image(
            resized,
            output_path,
            output_format,
            quality=quality,
        )

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
                log.debug("Запуск функции resize")
                generate_image_variant(image_file, preset)


if __name__ == "__main__":
    log.info("Старт генерации изображений")
    process_all_folders()
    log.info("Генерация изображений завершена")
