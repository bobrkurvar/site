from typing import Protocol
from pathlib import Path

class FileSessionPort(Protocol):
    async def __aenter__(self) -> "FileSessionPort": pass
    async def __aexit__(self, exc_type, exc, tb) -> None: pass

    async def save(self, image_path: Path | str, img: bytes) -> None: pass
    async def save_by_layer(
        self, image_path: Path | str, img: bytes, layer: str
    ) -> None: pass

    async def rollback(self) -> None: pass


class ProductImagesPort(Protocol):
    def session(self) -> FileSessionPort: pass
    def base_product_path(self, file_name: str) -> Path: pass
    async def delete_product(self, base_path: str | Path) -> int: pass
    def get_product_catalog_image_path(self, base_path: str) -> str: pass


class CollectionImagesPort(Protocol):
    def session(self) -> FileSessionPort: pass
    def base_collection_path(self, file_name: str) -> Path: pass
    async def delete_collection(self, base_path: str | Path) -> int: pass
    def get_collections_image_path(self, base_path: str) -> str: pass


class SlideImagesPort(Protocol):
    def session(self) -> FileSessionPort: pass
    async def delete_all_slides(self) -> int: pass
    @property
    def get_all_slides_paths(self) -> tuple[str, ...]: pass
    def base_slide_path(self, file_name: str) -> Path: pass
    @property
    def slides_file_count(self) -> int: pass