from pathlib import Path

from .fs_fakes import FakeFileManager


class FakeProductImagesManager(FakeFileManager):
    def __init__(self, root: str = "tests/images", layers: dict | None = None, fs=None):
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


class FakeCollectionImagesManager(FakeFileManager):
    def __init__(self, root: str = "tests/images", layers: dict | None = None, fs=None):
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


class FakeSlideImagesManager(FakeFileManager):
    def __init__(self, root: str = "tests/images", layers: dict | None = None, fs=None):
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
