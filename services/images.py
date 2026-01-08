
import logging
from pathlib import Path
from PIL import Image, ImageOps


log = logging.getLogger(__name__)


IMAGE_PRESETS = {
    "products": {"size": (640, 400), "mode": "cover"},       # каталог товаров
    "collections": {"size": (960, 480), "mode": "cover"},    # карточки коллекций
    "details": {"size": (2400, None), "mode": "contain"}, # детальная картинка
}

BASE_DIR = Path("static/images")
OUTPUT_DIRS = {
    "products": BASE_DIR / "products" / "catalog",
    "collections": BASE_DIR / "collections" / "catalog",
    "details": BASE_DIR / "products" / "details",
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


def generate_image_variant(
    input_path: Path,
    target: str,
    quality: int = 82,
):
    """
    Генерирует вариант изображения для сайта.

    - сохраняет пропорции
    - не апскейлит маленькие изображения
    - идемпотентна
    """

    if target not in IMAGE_PRESETS:
        raise ValueError(f"Unknown image preset: {target}")

    preset = IMAGE_PRESETS[target]
    width, height = preset["size"]
    mode = preset["mode"]
    output_dir = OUTPUT_DIRS[target]
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / input_path.name

    if output_path.exists():
        log.debug("Image already exists: %s", output_path)
        return output_path

    with Image.open(input_path) as img:
        img = img.convert("RGB")

        # 🔒 защита от апскейла
        if img.width < width or img.height < height:
            log.warning(
                "Image smaller than target (%s < %s), saving original size",
                img.size,
                (width, height),
            )
            resized = img
        else:
            resized = resize_image(img, (width, height), mode)

        output_format = output_path.suffix.lstrip(".").upper()
        if not output_format:
            output_format = "JPEG"  # дефолтный формат для файлов без расширения

        resized.save(
            output_path,
            output_format,
            quality=quality,
            optimize=True,
            progressive=True,
        )

    log.info("Generated %s image: %s", target, output_path)
    return output_path



async def get_image_path(my_path: str, *directories, upload_root=None):
    if directories:
        upload_dir = upload_root or Path(__name__).parent.parent
        my_path_name = Path(my_path).name
        path = upload_dir / "static" / "images"
        for directory in directories:
            path /= directory
        path /= my_path_name
        str_path = str(path)
        str_path = '\\'+str_path
        log.debug("Path: %s", str_path)
        if path.exists():
            log.debug("MINI Path: %s", str_path)
            return str_path
    return my_path



def generate_image_variant_bg(input_path: Path, target: str, quality: int = 82):
    task_queue = get_task_queue()
    task = (str(input_path), target, quality, 0)  # (args..., retry_count)
    task_queue.put(task)
    log.info(f"Task queued: {task}")
