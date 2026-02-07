import asyncio
import logging
from pathlib import Path

from core import logger

log = logging.getLogger(__name__)


class FakeFileManager:
    def __init__(
        self, upload_dir: str = "test/images", layers: dict | None = None, fs=None
    ):
        self._root = Path(upload_dir)
        self._fs = fs if fs is not None else {}
        self._layers = (
            layers
            if layers
            else {
                "original_product": "base/products",
                "original_collection": "base/collections",
                "original_slide": "base/slides",
                "products": "products/catalog",
                "details": "products/details",
                "collections": "collections/catalog",
                "slides": "slides",
            }
        )

    def resolve_path(self, file_name: str | None = "", layer: str = None):
        if layer not in self._layers:
            raise ValueError(f"Unknown layer: {layer}")
        return self._root / self._layers.get(layer, "") / file_name

    async def save(self, image_path, img):
        log.debug("IN SAVE IMAGE_PATH: %s", image_path)
        self._fs[str(image_path)] = img

    async def save_by_layer(self, image_path, img, layer: str):
        file_name = Path(image_path).name
        image_path = self.resolve_path(file_name, layer)
        await self.save(image_path, img)

    async def delete_by_layers(self, base_path: str | Path, layers: list[str]):
        base_path = Path(base_path) if isinstance(base_path, str) else base_path
        file_name = base_path.name
        paths = [self.resolve_path(file_name, layer) for layer in layers]
        paths.append(base_path)
        return await self.delete_async(paths)

    async def delete_async(self, paths):
        return await asyncio.to_thread(self._delete, paths)

    def _delete(self, paths):
        fake_deleted = 0
        for path in paths:
            if isinstance(path, str):
                path = Path(path)
            del self._fs[str(path)]
            fake_deleted += 1
        return fake_deleted

    @staticmethod
    def get_directory(main_path: Path, other_path: str | Path):
        if main_path.exists():
            return str(main_path)
        return str(other_path)


async def generate_products_images(*args, **kwargs) -> dict:
    return {"products": b"aaa", "details": b"bbb"}


async def generate_collections_images(*args, **kwargs) -> dict:
    return {"collections": b"aaa"}


async def noop_generate(*args, **kwargs) -> dict:
    return {}
