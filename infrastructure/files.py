import asyncio
import logging
from pathlib import Path

import aiofiles  # type: ignore

log = logging.getLogger(__name__)


class FileSystemStorage:
    @staticmethod
    async def save(path: Path | str, data: bytes):
        upload_dir = Path(path).parent
        if upload_dir:
            path.parent.mkdir(parents=True, exist_ok=True)
            async with aiofiles.open(path, "xb") as fw:
                await fw.write(data)

    @staticmethod
    async def delete(path: Path | str):
        path = Path(path)
        await asyncio.to_thread(path.unlink, True)


class FileManager:
    def __init__(
        self, root: str = "static/images", layers: dict | None = None, storage = None
    ):
        self._root = Path(root)
        self._storage = storage if storage else FileSystemStorage()
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

    def session(self):
        return FileSession(self)


    def resolve_path(self, file_name: str = "", layer: str | None = None) -> Path:
        if layer not in self._layers:
            raise ValueError(f"Unknown layer: {layer}")
        return self._root / self._layers.get(layer, "") / file_name


    async def save(self, image_path: Path | str, img):
        # upload_dir = Path(image_path).parent
        # if upload_dir:
        #     upload_dir.mkdir(parents=True, exist_ok=True)
        #     async with self._fs.open(image_path, "xb") as fw:
        #         await fw.write(img)
        await self._storage.save(image_path, img)
        return image_path

    async def save_by_layer(self, file_name: str, img: bytes, layer: str):
        path = self.resolve_path(file_name, layer)
        await self.save(path, img)
        return path

    async def save_by_layer_from_path(self, base_path: Path | str, img: bytes, layer: str):
        return await self.save_by_layer(Path(base_path).name, img, layer)

    async def delete_by_layers(self, base_path: str | Path, layers: list[str]) -> int:
        log.debug("deleted by layers: %s", layers)
        file_name = Path(base_path).name
        paths = [self.resolve_path(file_name, layer) for layer in layers]
        paths.append(base_path)  # type: ignore
        #return await self.delete_async(paths)
        return await self.delete(paths)


    async def delete(self, paths: list[Path]) -> int:
        deleted = 0
        for path in paths:
            if isinstance(path, str):
                path = Path(path)
            await self._storage.delete(path)
            deleted += 1
        return deleted


    # async def delete_async(self, paths):
    #     return await asyncio.to_thread(self._delete, paths)

    # @staticmethod
    # def _delete(paths: list[Path]) -> int:
    #     deleted = 0
    #     for path in paths:
    #         if isinstance(path, str):
    #             path = Path(path)
    #         path.unlink(missing_ok=True)
    #         deleted += 1
    #     return deleted

    @staticmethod
    def get_directory(main_path: Path, other_path: str | Path) -> str:
        if main_path.exists():
            return str(main_path)
        return str(other_path)


class FileSession:
    def __init__(self, file_manager: FileManager):
        self._fm = file_manager
        self._saved_files: list[Path] = []

    async def __aenter__(self):
        return self  # ← возвращаем proxy, а не fm

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            await self.rollback()
        else:
            self._saved_files.clear()


    async def save(self, image_path: Path, img: bytes):
        image_path = await self._fm.save(image_path, img)
        self._saved_files.append(image_path)

    async def save_by_layer(self, image_path: Path, img: bytes, layer: str):
        image_path = await self._fm.save_by_layer(image_path, img, layer)
        self._saved_files.append(image_path)

    async def rollback(self):
        log.debug("paths to rollback: %s", self._saved_files)
        await self._fm.delete(self._saved_files)

    def __getattr__(self, name):
        return getattr(self._fm, name)
