
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



