import logging

log = logging.getLogger(__name__)


class FakeStorage:
    def __init__(self, fs=None):
        self.storage = fs if fs is not None else {}

    async def save(self, path, data):
        #log.debug("save by path: %s", path)
        self.storage[str(path)] = data

    async def delete(self, path):
        log.debug("delete by path: %s", path)
        del self.storage[str(path)]


# async def generate_products_images(*args, **kwargs) -> dict:
#     return {"products": b"aaa", "details": b"bbb"}
#
#
# async def generate_collections_images(*args, **kwargs) -> dict:
#     return {"collections": b"aaa"}
#
#
# async def noop_generate(*args, **kwargs) -> dict:
#     return {}


class FakeImageGenerator:

    async def products_catalog_and_details(self, img: bytes):
        return {"products": b"aaa", "details": b"bbb"}


    async def collections_catalog(self, img: bytes):
        return {"collections": b"aaa"}


    async def slides(self, img: bytes):
        return {"slides": b"aaa"}

