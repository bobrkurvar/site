import logging
from pathlib import Path

log = logging.getLogger(__name__)


class FakeStorage:
    def __init__(self, fs=None):
        self.storage = fs if fs is not None else {}

    async def save(self, path, data):
        self.storage[Path(path).as_posix()] = data

    async def delete(self, path):
        log.debug("delete by path: %s", path)
        key = Path(path).as_posix()
        if key in self.storage:
            del self.storage[key]


class FakeImageGenerator:

    async def generate_product_variants(self, img: bytes):
        return {"products": b"aaa", "details": b"bbb"}

    async def generate_collection_variants(self, img: bytes):
        return {"collections": b"aaa"}

    async def generate_slide_variant(self, img: bytes):
        return {"slides": b"aaa"}
