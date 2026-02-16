import base64
import logging
from pathlib import Path

import aiofiles

from adapters.files import FileManager

from .http_client import get_http_client
from services.exceptions import ImageProcessingError
from functools import wraps
from binascii import Error

log = logging.getLogger(__name__)

def generate_image_with_exc(generate):
    @wraps(generate)
    async def wrapper(*args, **kwargs):
        try:
            result = await generate(*args, **kwargs)
        except (ValueError, Error) as exc:
            raise ImageProcessingError("Ошибка декодирования") from exc
        if result is None:
            raise ImageProcessingError("Ошибка генерации")
        return result
    return wrapper


@generate_image_with_exc
async def generate_image_products_catalog_and_details(img: bytes):
    img = base64.b64encode(img).decode("utf-8")
    http_client = get_http_client()
    response = await http_client.generate_images(
        data=img, targets=("products", "details")
    )
    response["products"] = base64.b64decode(response["products"])
    response["details"] = base64.b64decode(response["details"])
    return response


@generate_image_with_exc
async def generate_image_collections_catalog(img: bytes):
    img = base64.b64encode(img).decode("utf-8")
    http_client = get_http_client()
    response = await http_client.generate_images(data=img, targets=("collections",))
    response["collections"] = base64.b64decode(response["collections"])
    return response


@generate_image_with_exc
async def generate_slides(img: bytes):
    img = base64.b64encode(img).decode("utf-8")
    http_client = get_http_client()
    response = await http_client.generate_images(data=img, targets=("slides",))
    response["slides"] = base64.b64decode(response["slides"])
    return response


class ProductImagesManager(FileManager):
    def __init__(
        self, root: str = "static/images", layers: dict | None = None, fs=aiofiles
    ):
        super().__init__(root, layers, fs)

    async def delete_product(self, base_path: str | Path) -> int:
        return await self.delete_by_layers(base_path, ["products", "details"])

    def base_product_path(self, file_name: str) -> Path:
        return self.resolve_path(file_name, "original_product")

    def get_product_catalog_image_path(self, base_path: str) -> str:
        base_path = Path(base_path)
        name = base_path.name
        path_catalog = self.resolve_path(name, "products")
        return self.get_directory(path_catalog, base_path)

    def get_product_details_image_path(self, base_path: str) -> str:
        base_path = Path(base_path)
        name = base_path.name
        path_details = self.resolve_path(name, "details")
        return self.get_directory(path_details, base_path)


class CollectionImagesManager(FileManager):
    def __init__(
        self, root: str = "static/images", layers: dict | None = None, fs=aiofiles
    ):
        super().__init__(root, layers, fs)

    async def delete_collection(self, base_path: str | Path) -> int:
        return await self.delete_by_layers(base_path, ["collections"])

    def base_collection_path(self, file_name: str) -> Path:
        return self.resolve_path(file_name, "original_collection")

    def get_collections_image_path(self, base_path: str) -> str:
        name = Path(base_path).name
        path_collections = self.resolve_path(name, "collections")
        return self.get_directory(path_collections, base_path)


class SlideImagesManager(FileManager):
    def __init__(
        self, root: str = "static/images", layers: dict | None = None, fs=aiofiles
    ):
        super().__init__(root, layers, fs)


    async def delete_all_slides(self) -> int:
        paths = [
            self.resolve_path(layer="original_slide"),
            self.resolve_path(layer="slides"),
        ]
        return await self.delete_async(paths)

    def base_slide_path(self, file_name: str) -> Path:
        return self.resolve_path(file_name, "original_slide")

    def get_slides_image_path(self, base_path: str) -> str:
        name = Path(base_path).name
        path_slides = self.resolve_path(name, "slides")
        return self.get_directory(path_slides, base_path)

    @property
    def get_all_slides_paths(self) -> list[str]:
        path = self.resolve_path(layer="original_slide")
        return [
            self.get_slides_image_path(file)
            for file in path.iterdir()
            if file.is_file()
        ]

    @property
    def slides_files_count(self) -> int:
        path = self.resolve_path(layer="original_slide")
        return sum(1 for f in path.iterdir() if f.is_file())
