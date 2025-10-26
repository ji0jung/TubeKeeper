import json
from typing import Optional, Any
from uuid import UUID
import redis.asyncio as redis

from ...domain.services.cache_service import CacheService
from ...config.settings import settings

class RedisCacheService(CacheService):
    
    def __init__(self):
        self._redis = redis.from_url(settings.redis_url)
    
    async def get(self, key: str) -> Optional[Any]:
        value = await self._redis.get(key)
        return json.loads(value) if value else None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> None:
        ttl = ttl or settings.cache_ttl
        await self._redis.setex(key, ttl, json.dumps(value, default=str))
    
    async def delete(self, key: str) -> None:
        await self._redis.delete(key)
    
    async def invalidate_user_categories(self, user_id: UUID) -> None:
        pattern = f"categories:user:{user_id}:*"
        keys = await self._redis.keys(pattern)
        if keys:
            await self._redis.delete(*keys)
    
    def _get_categories_key(self, user_id: UUID) -> str:
        return f"categories:user:{user_id}:list"
