from fastapi import FastAPI
from pydantic import BaseModel
import logging
#from pathlib import Path
from PIL import Image, ImageOps
from core import logger
import asyncio
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO


app = FastAPI()
log = logging.getLogger(__name__)



NUM_WORKERS = 4  # процессов для CPU
MAX_RETRIES = 3

executor = ProcessPoolExecutor(max_workers=NUM_WORKERS)

IMAGE_PRESETS = {
    "products": {"size": (640, 400), "mode": "cover"},  # каталог товаров
    "collections": {"size": (960, 480), "mode": "cover"},  # карточки коллекций
    "details": {"size": (2400, None), "mode": "fit"},  # детальная картинка
    "slides": {"size": (1100, 825), "mode": "cover"}
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



def image_to_bytes(
    img: Image.Image,
    format: str = "JPEG",
    quality: int = 82,
) -> bytes:
    buf = BytesIO()
    img.save(
        buf,
        format=format,
        quality=quality,
        optimize=True,
        progressive=True,
    )
    return buf.getvalue()

def generate_image_variant(image_bytes: bytes, target: str):
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
    with Image.open(BytesIO(image_bytes)) as img:
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
        bytes_img = image_to_bytes(resized)

        return bytes_img

class ImageWithTarget(BaseModel):
    input_path: str
    targets: tuple


@app.post("/generate-images")
async def generate_image(image_data: ImageWithTarget):
    loop = asyncio.get_running_loop()
    images = {}
    for target in image_data.targets:
        image = await loop.run_in_executor(
            executor,
            generate_image_variant,
            image_data.input_path,
            target,
        )
        images[target] = image
    return images
