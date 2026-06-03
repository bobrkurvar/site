import json
import logging

from redis.asyncio import ConnectionError, Redis

log = logging.getLogger(__name__)


class RedisProvider:
    def __init__(self, redis: Redis):
        self._redis = redis

    @classmethod
    async def create(cls, host: str) -> "RedisProvider":
        redis = Redis(host=host)
        try:
            await redis.ping()
        except ConnectionError:
            try:
                await redis.aclose()
                await redis.connection_pool.disconnect()
            except Exception:
                pass
            raise RuntimeError("Redis connection is not initialized")
        return cls(redis)

    @property
    def client(self) -> Redis:
        return self._redis

    async def close(self) -> None:
        await self._redis.aclose()
        await self._redis.connection_pool.disconnect()


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
