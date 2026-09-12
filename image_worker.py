# import asyncio
# import base64
# import logging
# from concurrent.futures import ProcessPoolExecutor
# from io import BytesIO
#
# from fastapi import FastAPI
# from PIL import Image, ImageOps
# from pydantic import BaseModel
#
# from core.logger import setup_logging
# from shared import COLLECTIONS, DETAILS, PRODUCTS, SLIDES
#
# setup_logging()
#
# app = FastAPI()
# log = logging.getLogger(__name__)
#
#
# NUM_WORKERS = 4  # процессов для CPU
# MAX_RETRIES = 3
#
# executor = ProcessPoolExecutor(max_workers=NUM_WORKERS)
#
# IMAGE_PRESETS = {
#     PRODUCTS: {"size": (640, 400), "mode": "cover"},  # каталог товаров
#     COLLECTIONS: {"size": (960, 480), "mode": "cover"},  # карточки коллекций
#     DETAILS: {"size": (2400, None), "mode": "fit"},  # детальная картинка
#     SLIDES: {"size": (1100, 825), "mode": "cover"},
# }
#
#
# def resize_image(
#     img: Image.Image,
#     target_size: tuple[int, int],
#     mode: str,
# ) -> Image.Image:
#     if mode == "fit":
#         img.thumbnail(target_size, Image.LANCZOS)  # type: ignore
#         return img
#
#     if mode == "cover":
#         return ImageOps.fit(
#             img,
#             target_size,
#             method=Image.LANCZOS,  # type ignore
#             centering=(0.5, 0.5),
#         )
#
#     raise ValueError(f"Unknown resize mode: {mode}")
#
#
# def image_to_bytes(
#     img: Image.Image,
#     img_format: str = "JPEG",
#     quality: int = 82,
# ) -> bytes:
#     buf = BytesIO()
#     img.save(
#         buf,
#         format=img_format,
#         quality=quality,
#         optimize=True,
#         progressive=True,
#     )
#     return buf.getvalue()
#
#
# def generate_image_variant(image_bytes: bytes, target: str):
#     """
#     Генерирует вариант изображения для сайта.
#     - сохраняет пропорции
#     - не апскейлит маленькие изображения
#     - идемпотентна
#     """
#
#     if target not in IMAGE_PRESETS:
#         raise ValueError(f"Unknown image preset: {target}")
#
#     preset = IMAGE_PRESETS[target]
#     width, height = preset["size"]
#     mode = preset["mode"]
#     with Image.open(BytesIO(image_bytes)) as img:
#         img = img.convert("RGB")
#         smaller_width = width is not None and img.width < width
#         smaller_height = height is not None and img.height < height
#         # защита от апскейла
#         if smaller_width or smaller_height:
#             log.warning(
#                 "Image smaller than target (%s < %s), saving original size",
#                 img.size,
#                 (width, height),
#             )
#             resized = img
#         else:
#             target_size = (
#                 width if width is not None else img.width,
#                 height if height is not None else img.height,
#             )
#             resized = resize_image(img, target_size, mode)
#         bytes_img = image_to_bytes(resized)
#
#         return bytes_img
#
#
# class ImageWithTarget(BaseModel):
#     data: str
#     targets: tuple
#
#
# @app.get("/health")
# def health():
#     return {"status": "ok"}
#
#
# @app.post("/generate-images")
# async def generate_image(image_data: ImageWithTarget):
#     data = base64.b64decode(image_data.data)
#     loop = asyncio.get_running_loop()
#     images = {}
#     for target in image_data.targets:
#         image = await loop.run_in_executor(
#             executor,
#             generate_image_variant,
#             data,
#             target,
#         )
#         images[target] = base64.b64encode(image).decode("utf-8")
#     return images
import asyncio
import base64
import logging
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO

from fastapi import FastAPI
from PIL import Image, ImageOps
from pydantic import BaseModel

from core.logger import setup_logging
from contracts.layers import COLLECTIONS, SLIDES, DETAILS, PRODUCTS, LAYERS_IMAGE_FORMAT
from contracts.images import ImageVariant, GenerateImagesRequest

setup_logging()

app = FastAPI()
log = logging.getLogger(__name__)


NUM_WORKERS = 4  # процессов для CPU
MAX_RETRIES = 3

executor = ProcessPoolExecutor(max_workers=NUM_WORKERS)


IMAGE_PRESETS = {
    PRODUCTS: {"size": (640, 400), "mode": "cover"},  # каталог товаров
    COLLECTIONS: {"size": (960, 480), "mode": "cover"},  # карточки коллекций
    DETAILS: {"size": (2400, None), "mode": "fit"},  # детальная картинка
    SLIDES: {"size": (1100, 825), "mode": "cover"},
}


def resize_image(
    img: Image.Image,
    target_size: tuple[int, int],
    mode: str,
) -> Image.Image:
    if mode == "fit":
        img.thumbnail(target_size, Image.LANCZOS)  # type: ignore
        return img

    if mode == "cover":
        return ImageOps.fit(
            img,
            target_size,
            method=Image.LANCZOS,  # type ignore
            centering=(0.5, 0.5),
        )

    raise ValueError(f"Unknown resize mode: {mode}")


def image_to_bytes(
    img: Image.Image,
    #img_format: str = LAYERS_IMAGE_FORMAT,
    quality: int = 82,
) -> bytes:
    buf = BytesIO()
    img.save(
        buf,
        format=LAYERS_IMAGE_FORMAT,
        method=4,
        quality=quality,
    )
    return buf.getvalue()


def generate_image_variant(image_bytes: bytes, target: str) -> tuple[bytes, str]:
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
        if img.mode in ("RGBA", "LA") or (
            img.mode == "P" and "transparency" in img.info
        ):
            img = img.convert("RGBA")
        else:
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

        return image_to_bytes(resized), f".{LAYERS_IMAGE_FORMAT.lower()}"


# class ImageWithTarget(BaseModel):
#     data: str
#     targets: tuple


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate-images")
async def generate_image(image_data: GenerateImagesRequest):
    loop = asyncio.get_running_loop()

    result = []

    for target in image_data.targets:
        data, extension = await loop.run_in_executor(
            executor,
            generate_image_variant,
            image_data.data,
            target,
        )

        result.append(
            ImageVariant(
                target=target,
                data=data,
                extension=extension,
            )
        )

    return result

