from pathlib import Path
import logging
from core import logger

log = logging.getLogger(__name__)

# BASE_DIR = Path("static/images")
# OUTPUT_DIRS = {
#     "products": BASE_DIR / "products" / "catalog",
#     "collections": BASE_DIR / "collections" / "catalog",
#     "details": BASE_DIR / "products" / "details",
#     "slides": BASE_DIR / 'slides'
# }
#
# class FakeFileManager:
#     # def __init__(self, upload_dir: str | None = None, fs = None):
#     #     self.upload_dir = Path(upload_dir) if upload_dir else None
#     #     self.fs = fs
#     def __init__(self, fs = None):
#         self.upload_dir = Path("test/images")
#         self._fs = fs
#
#     def set_path(self, upload_dir: str):
#         if self.upload_dir is None:
#             self.upload_dir = Path(upload_dir)
#
#     async def save(self, image_path, img):
#         if self._fs is not None:
#             self._fs[str(image_path)] = img
#
#     def delete(self, paths):
#         fake_deleted = 0
#         for path in paths:
#             if isinstance(path, str):
#                 path = Path(path)
#             del self._fs[str(path)]
#             fake_deleted += 1
#         return fake_deleted
#
#     def path(self, str_name):
#         name = Path(str_name).name
#         return self.upload_dir / name
#
#     @staticmethod
#     def file_name(str_path):
#         return Path(str_path).name

# def get_fake_save_bg_products_and_details_with_fs(fs: dict):
#     async def fake_save_bg(image_path):
#         for target in ("products", "details"):
#             input_path = Path(image_path)
#             output_dir = OUTPUT_DIRS[target]
#             output_path = output_dir / input_path.name
#             fs[str(output_path)] = ""
#     return fake_save_bg
#
# def get_fake_save_bg_collections_with_fs(fs: dict):
#     async def fake_save_bg(image_path):
#         target = "collections"
#         input_path = Path(image_path)
#         output_dir = OUTPUT_DIRS[target]
#         output_path = output_dir / input_path.name
#         fs[str(output_path)] = ""
#     return fake_save_bg

class FakeFileManager:
    def __init__(self, upload_dir: str = "test/images", layers: dict | None = None, fs=None):
        self.root = Path(upload_dir)
        self.fs = fs
        self.layers = layers if layers else {
            "original_product": "base/products",
            "original_collection": "base/collections",
            "original_slide": "base/slides",
            "products": "products/catalog",
            "details": "products/details",
            "collections": "collections/catalog",
            "slides": "slides"
        }

    def resolve_path(self, file_name: str | None = "", layer: str = None):
        return self.root / self.layers.get(layer, "") / file_name

    async def save(self, image_path, img):
        if self.fs is not None:
            log.debug("IN SAVE IMAGE_PATH: %s", image_path)
            self.fs[str(image_path)] = img

    async def save_slide_original(self, file_name, img):
        image_path = self.resolve_path(file_name , "original_slide")
        await self.save(image_path, img)

    async def save_by_layer(self, image_path, img, layer: str):
        file_name = Path(image_path).name
        image_path = self.resolve_path(file_name, layer)
        await self.save(image_path, img)

    def delete_product(self, base_path: str | Path):
        base_path = Path(base_path)
        file_name = base_path.name

        paths = [
            base_path,  # оригинал
            self.resolve_path(file_name, "products"),  # каталог
            self.resolve_path(file_name, "details"),  # детальная картинка
        ]
        return self._delete(paths)

    def delete_collection(self, base_path: str | Path):
        base_path = Path(base_path)
        file_name = base_path.name

        paths = [
            base_path,
            self.resolve_path(file_name, "collections"),
        ]
        return self._delete(paths)

    def delete_all_slides(self):
        upload_dirs = [
            self.resolve_path(layer="original_slide"),
            self.resolve_path(layer="slides"),
        ]
        deleted = 0
        for upload_dir in upload_dirs:
            for f in upload_dir.iterdir():
                if f.is_file() and f.exists():
                    f.unlink()
                    deleted += 1
        return deleted

    def _delete(self, paths):
        fake_deleted = 0
        if self.fs is not None:
            for path in paths:
                if isinstance(path, str):
                    path = Path(path)
                del self.fs[str(path)]
                fake_deleted += 1
        return fake_deleted

    def base_product_path(self, file_name: str):
        return self.resolve_path(file_name, "original_product")

    def product_catalog_path(self, file_name: str):
        return self.resolve_path(file_name, "products")

    def product_details_path(self, file_name: str):
        return self.resolve_path(file_name, "details")

    def base_collection_path(self, file_name: str):
        return self.resolve_path(file_name, "original_collection")

    def collection_catalog_path(self, file_name: str):
        return self.resolve_path(file_name, "collections")


    @property
    def slides_file_count(self):
        slide_path = self.root / self.layers["original_slide"]
        upload_dir = Path(slide_path)
        return len([f for f in upload_dir.iterdir() if f.is_file()])

async def generate_products_images(*args, **kwargs) -> dict:
    return {"products": b"aaa", "details": b"bbb"}

async def generate_collections_images(*args, **kwargs) -> dict:
    return {"collections": b"aaa"}

async def noop_generate(*args, **kwargs) -> dict:
    return {}