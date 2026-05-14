class FakeRedisStorage:
    def __init__(self, storage: dict | None = None):
        self.storage = storage if storage else {}

    async def set(self, key, value, *args, **kwargs):
        self.storage[key] = value

    async def get(self, key):
        return self.storage.get(key, None)

    async def delete(self, key):
        del self.storage[key]

    async def getdel(self, key):
        return self.storage.pop(key)

    async def exists(self, key):
        return key in self.storage

    async def incr(self, key):
        self.storage[key] += 1
        return self.storage[key]

    async def expire(self, *args):
        pass


class FakeRedisService:

    def __init__(self, prefix: str = ""):
        self.prefix = prefix
        self.conn = FakeRedisStorage()

    async def set(
        self,
        key: str,
        value,
        ttl: int | None = None,
    ) -> None:
        key = f"{self.prefix}:{key}"
        await self.conn.set(
            key,
            value,
            ex=ttl,
        )

    async def get(self, key: str):
        key = f"{self.prefix}:{key}"
        value = await self.conn.get(key)
        return value

    async def delete(self, key: str) -> None:
        key = f"{self.prefix}:{key}"
        await self.conn.delete(key)

    async def pop(self, key: str):
        key = f"{self.prefix}:{key}"
        value = await self.conn.getdel(key)
        return value if value else None

    async def exists(self, key: str) -> bool:
        key = f"{self.prefix}:{key}"
        return bool(await self.conn.exists(key))

    async def incr(self, key: str) -> int:
        key = f"{self.prefix}:{key}"
        return await self.conn.incr(key)

    async def expire(self, key: str, ttl: int):
        key = f"{self.prefix}:{key}"
        await self.conn.expire(key, ttl)
