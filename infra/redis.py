import json


class RedisService:


    def __init__(self, redis, prefix: str = ""):
        self.prefix = prefix
        self.conn = redis


    async def set(
        self,
        key: str,
        value,
        ttl: int | None = None,
    ) -> None:
        key = f"{self.prefix}:{key}"
        await self.conn.set(
            key,
            json.dumps(value),
            ex=ttl,
        )

    async def get(self, key: str):
        key = f"{self.prefix}:{key}"
        value = await self.conn.get(key)
        return json.loads(value) if value else None

    async def delete(self, key: str) -> None:
        key = f"{self.prefix}:{key}"
        await self.conn.delete(key)

    async def pop(self, key: str):
        key = f"{self.prefix}:{key}"
        value = await self.conn.getdel((key))
        return json.loads(value) if value else None

    async def exists(self, key: str) -> bool:
        key = f"{self.prefix}:{key}"
        return bool(await self.conn.exists(key))

    async def incr(self, key: str) -> int:
        key = f"{self.prefix}:{key}"
        return await self.conn.incr(key)

    async def expire(self, key: str, ttl: int):
        key = f"{self.prefix}:{key}"
        await self.conn.expire(key, ttl)
