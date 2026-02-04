from pathlib import Path
import aiofiles
import logging

log = logging.getLogger(__name__)


class FileManager:
    def __init__(self, upload_dir: str = "static/images", layers: dict | None = None, fs=aiofiles):
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
        upload_dir = image_path.parent
        if upload_dir:
            upload_dir.mkdir(parents=True, exist_ok=True)
            async with self.fs.open(image_path, "xb") as fw:
                await fw.write(img)

    async def save_slide_original(self, file_name, img):
        image_path = self.resolve_path(file_name, "original_slide")
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

    @staticmethod
    def _delete(paths: list[Path]):
        deleted = 0
        for path in paths:
            if isinstance(path, str):
                path = Path(path)
            path.unlink(missing_ok=True)
            deleted += 1
        return deleted

    def base_product_path(self, file_name: str):
        return self.resolve_path(file_name, "original_product")

    def base_collection_path(self, file_name: str):
        return self.resolve_path(file_name, "original_collection")

    @property
    def slides_file_count(self):
        slide_path = self.root / self.layers["original_slide"]
        upload_dir = Path(slide_path)
        return len([f for f in upload_dir.iterdir() if f.is_file()])
