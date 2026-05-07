import base64
import logging
from binascii import Error
from functools import wraps
from pathlib import Path

from adapters.files import FileManager
from services.exceptions import ImageProcessingError
from adapters.file_layers import (
    PRODUCT_IMAGE_LAYERS,
    COLLECTION_IMAGE_LAYERS,
    SLIDE_IMAGE_LAYERS,
    ORIGINAL_PRODUCT,
    ORIGINAL_COLLECTION,
    ORIGINAL_SLIDE,
)
from shared import PRODUCTS, DETAILS, SLIDES, COLLECTIONS

# import aiofiles # type: ignore


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


class ImageGenerator:
    def __init__(self, api_client):
        self._api_client = api_client

    @generate_image_with_exc
    async def generate_product_variants(self, img: bytes):
        img = base64.b64encode(img).decode("utf-8")
        response = await self._api_client.generate_images(
            data=img, targets=(PRODUCTS, DETAILS)
        )
        response[PRODUCTS] = base64.b64decode(response[PRODUCTS])
        response[DETAILS] = base64.b64decode(response[DETAILS])
        return response

    @generate_image_with_exc
    async def generate_collection_variants(self, img: bytes):
        img = base64.b64encode(img).decode("utf-8")
        response = await self._api_client.generate_images(
            data=img, targets=(COLLECTIONS,)
        )
        response[COLLECTIONS] = base64.b64decode(response[COLLECTIONS])
        return response

    @generate_image_with_exc
    async def generate_slide_variant(self, img: bytes):
        img = base64.b64encode(img).decode("utf-8")
        response = await self._api_client.generate_images(data=img, targets=(SLIDES,))
        response[SLIDES] = base64.b64decode(response[SLIDES])
        return response


class ProductImagesManager(FileManager):

    def __init__(self, root: str = "static/images", storage=None):
        super().__init__(root, PRODUCT_IMAGE_LAYERS, storage)

    async def delete_product(self, base_path: str | Path) -> int:
        return await self.delete_by_layers(base_path, [PRODUCTS, DETAILS])

    def base_product_path(self, file_name: str) -> Path:
        return self.resolve_path(file_name, ORIGINAL_PRODUCT)

    def get_product_catalog_image_path(self, base_path: str) -> str:
        base_path = Path(base_path)
        name = base_path.name
        path_catalog = self.resolve_path(name, PRODUCTS)
        return self.get_directory(path_catalog, base_path)

    def get_product_details_image_path(self, base_path: str) -> str:
        base_path = Path(base_path)
        name = base_path.name
        path_details = self.resolve_path(name, DETAILS)
        return self.get_directory(path_details, base_path)


class CollectionImagesManager(FileManager):
    def __init__(self, root: str = "static/images", storage=None):
        super().__init__(root, COLLECTION_IMAGE_LAYERS, storage)

    async def delete_collection(self, base_path: str | Path) -> int:
        return await self.delete_by_layers(base_path, [COLLECTIONS])

    def base_collection_path(self, file_name: str) -> Path:
        return self.resolve_path(file_name, ORIGINAL_COLLECTION)

    def get_collections_image_path(self, base_path: str) -> str:
        name = Path(base_path).name
        path_collections = self.resolve_path(name, COLLECTIONS)
        return self.get_directory(path_collections, base_path)


class SlideImagesManager(FileManager):
    def __init__(self, root: str = "static/images", storage=None):
        super().__init__(root, SLIDE_IMAGE_LAYERS, storage)

    async def delete_all_slides(self) -> int:
        paths = [
            self.resolve_path(layer=ORIGINAL_SLIDE),
            self.resolve_path(layer=SLIDES),
        ]
        return await self.delete(paths)

    def base_slide_path(self, file_name: str) -> Path:
        return self.resolve_path(file_name, ORIGINAL_SLIDE)

    def get_slides_image_path(self, base_path: str | Path) -> str:
        name = Path(base_path).name
        path_slides = self.resolve_path(name, SLIDES)
        return self.get_directory(path_slides, base_path)

    @property
    def get_all_slides_paths(self) -> tuple[str, ...]:
        path = self.resolve_path(layer=ORIGINAL_SLIDE)
        return tuple(
            self.get_slides_image_path(file)
            for file in path.iterdir()
            if file.is_file()
        )

    @property
    def slides_file_count(self) -> int:
        path = self.resolve_path(layer=ORIGINAL_SLIDE)
        return sum(1 for f in path.iterdir() if f.is_file())
