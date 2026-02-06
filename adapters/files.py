from pathlib import Path
import aiofiles
import logging
import asyncio

log = logging.getLogger(__name__)


class FileManager:
    def __init__(self, root: str = "static/images", layers: dict | None = None, fs=aiofiles):
        self._root = Path(root)
        self._fs = fs
        self._layers = layers if layers else {
            "original_product": "base/products",
            "original_collection": "base/collections",
            "original_slide": "base/slides",
            "products": "products/catalog",
            "details": "products/details",
            "collections": "collections/catalog",
            "slides": "slides"
        }

    def resolve_path(self, file_name: str | None = "", layer: str = None):
        if layer not in self._layers:
            raise ValueError(f"Unknown layer: {layer}")
        return self._root / self._layers.get(layer, "") / file_name


    async def save(self, image_path, img):
        upload_dir = image_path.parent
        if upload_dir:
            upload_dir.mkdir(parents=True, exist_ok=True)
            async with self._fs.open(image_path, "xb") as fw:
                await fw.write(img)


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

    @staticmethod
    def _delete(paths: list[Path]):
        deleted = 0
        for path in paths:
            if isinstance(path, str):
                path = Path(path)
            path.unlink(missing_ok=True)
            deleted += 1
        return deleted


    @staticmethod
    def get_directory(main_path: Path, other_path: str | Path):
        if main_path.exists():
            return str(main_path)
        return str(other_path)
