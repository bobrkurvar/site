import logging

log = logging.getLogger(__name__)


class FakeRepo:
    def __init__(self):
        self.created = []

    async def create(self, obj, *args, **kwargs):
        self.created.append(obj)
        return obj

    async def read(self, *args, **kwargs):
        pass

    async def read_one(self, *args, **kwargs):
        pass

    async def update(self, *args, **kwargs):
        pass

    async def delete(self, *args, **kwargs):
        pass


class FakeUoW:
    def __init__(self, db):
        self.committed = False
        # self.session = self
        self.db = db

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def commit(self):
        self.committed = True
