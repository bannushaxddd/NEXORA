"""Redis cache for Nexora (optional when use_cache=False)."""
import json
from typing import Any, Optional

from src.config import settings
from src.logger import logger

# Use redis.asyncio (built into redis package); avoid deprecated aioredis
try:
    from redis.asyncio import Redis
except ImportError:
    Redis = None  # type: ignore


class Cache:
    """Async Redis cache; no-op when use_cache is False or Redis unavailable."""

    def __init__(self) -> None:
        self._client: Optional[Any] = None

    async def connect(self) -> None:
        if not getattr(settings, "use_cache", True):
            logger.info("cache_disabled")
            return
        url = settings.get_redis_url()
        if not url:
            return
        if Redis is None:
            logger.warning("redis_not_installed_skipping_cache")
            return
        try:
            self._client = Redis.from_url(url, decode_responses=True)
            await self._client.ping()
            logger.info("cache_connected", url=url)
        except Exception as e:
            logger.warning("cache_connect_failed", error=str(e))
            self._client = None

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("cache_disconnected")

    async def get(self, key: str) -> Optional[Any]:
        if not self._client:
            return None
        try:
            val = await self._client.get(key)
            if val is None:
                return None
            return json.loads(val)
        except Exception:
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        if not self._client:
            return
        ex = ttl if ttl is not None else getattr(settings, "cache_ttl", 3600)
        try:
            await self._client.set(key, json.dumps(value), ex=ex)
        except Exception as e:
            logger.warning("cache_set_failed", key=key, error=str(e))

    async def invalidate(self, pattern: str) -> int:
        if not self._client:
            return 0
        count = 0
        try:
            async for key in self._client.scan_iter(match=pattern):
                await self._client.delete(key)
                count += 1
        except Exception as e:
            logger.warning("cache_invalidate_failed", pattern=pattern, error=str(e))
        return count


cache = Cache()
