import logging
from pathlib import Path

import aiofiles

from adapters.files import FileManager

from .http_client import http_client

log = logging.getLogger(__name__)


# def get_image_path(my_path: str, *directories):
#     if directories:
#         root = Path("static/images")
#         my_path_name = Path(my_path).name
#         for directory in directories:
#             root /= directory
#         root /= my_path_name
#         str_path = str(root)
#         if root.exists():
#             log.debug("Path: %s", str_path)
#             return str_path
#     return my_path


async def generate_image_products_catalog_and_details(input_path):
    input_path = str(input_path) if not isinstance(input_path, str) else input_path
    return await http_client.generate_products_images(
        input_path=input_path, targets=("products", "details")
    )


async def generate_image_collections_catalog(input_path):
    input_path = str(input_path) if not isinstance(input_path, str) else input_path
    return await http_client.generate_products_images(
        input_path=input_path, targets=("collections",)
    )


async def generate_slides(input_path):
    input_path = str(input_path) if not isinstance(input_path, str) else input_path
    return await http_client.generate_products_images(
        input_path=input_path, targets=("slides",)
    )


class ProductImagesManager(FileManager):
    def __init__(
        self, root: str = "static/images", layers: dict | None = None, fs=aiofiles
    ):
        super().__init__(root, layers, fs)

    async def delete_product(self, base_path: str | Path):
        return await self.delete_by_layers(base_path, ["products", "details"])

    def base_product_path(self, file_name: str):
        return self.resolve_path(file_name, "original_product")

    def get_product_catalog_image_path(self, base_path: str):
        base_path = Path(base_path)
        name = base_path.name
        path_catalog = self.resolve_path(name, "products")
        return self.get_directory(path_catalog, base_path)

    def get_product_details_image_path(self, base_path: str):
        base_path = Path(base_path)
        name = base_path.name
        path_details = self.resolve_path(name, "details")
        return self.get_directory(path_details, base_path)


class CollectionImagesManager(FileManager):
    def __init__(
        self, root: str = "static/images", layers: dict | None = None, fs=aiofiles
    ):
        super().__init__(root, layers, fs)

    async def delete_collection(self, base_path: str | Path):
        return await self.delete_by_layers(base_path, ["collections"])

    def base_collection_path(self, file_name: str):
        return self.resolve_path(file_name, "original_collection")

    def get_collections_image_path(self, base_path: str):
        base_path = Path(base_path)
        name = base_path.name
        path_collections = self.resolve_path(name, "collections")
        return self.get_directory(path_collections, base_path)


class SlideImagesManager(FileManager):
    def __init__(
        self, root: str = "static/images", layers: dict | None = None, fs=aiofiles
    ):
        super().__init__(root, layers, fs)

    async def save_slide_original(self, file_name, img):
        image_path = self.resolve_path(file_name, "original_slide")
        await self.save(image_path, img)

    async def delete_all_slides(self):
        paths = [
            self.resolve_path(layer="original_slide"),
            self.resolve_path(layer="slides"),
        ]
        return await self.delete_async(paths)

    def base_slide_path(self, file_name: str):
        return self.resolve_path(file_name, "original_slide")

    def get_slides_image_path(self, base_path: str):
        base_path = Path(base_path)
        name = base_path.name
        path_slides = self.resolve_path(name, "slides")
        return self.get_directory(path_slides, base_path)

    @property
    def get_all_slides_paths(self):
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
