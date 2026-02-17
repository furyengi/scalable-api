import json
from typing import Any, Optional
import redis.asyncio as aioredis
from app.core.config import settings


class RedisClient:
    def __init__(self):
        self._client: Optional[aioredis.Redis] = None

    async def connect(self):
        self._client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )

    async def ping(self) -> bool:
        try:
            if not self._client:
                await self.connect()
            return await self._client.ping()
        except Exception:
            return False

    async def get(self, key: str) -> Optional[Any]:
        if not self._client:
            await self.connect()
        data = await self._client.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        if not self._client:
            await self.connect()
        return await self._client.setex(key, ttl, json.dumps(value, default=str))

    async def delete(self, *keys: str) -> int:
        if not self._client:
            await self.connect()
        return await self._client.delete(*keys)

    async def delete_pattern(self, pattern: str) -> int:
        if not self._client:
            await self.connect()
        keys = await self._client.keys(pattern)
        return await self._client.delete(*keys) if keys else 0

    async def close(self):
        if self._client:
            await self._client.aclose()


redis_client = RedisClient()
