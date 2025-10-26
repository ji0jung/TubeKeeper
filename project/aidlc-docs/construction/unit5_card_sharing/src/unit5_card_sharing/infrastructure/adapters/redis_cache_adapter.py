import json
import redis.asyncio as redis
from typing import Optional, Dict, Any
from datetime import timedelta

class RedisCacheAdapter:
    def __init__(self, redis_client: redis.Redis):
        self._client = redis_client
    
    async def get_share_link_cache(self, share_token: str) -> Optional[Dict[str, Any]]:
        key = f"share_link:{share_token}"
        cached_data = await self._client.get(key)
        
        if cached_data:
            return json.loads(cached_data)
        return None
    
    async def set_share_link_cache(
        self, 
        share_token: str, 
        card_data: Dict[str, Any], 
        ttl_days: int = 7
    ) -> None:
        key = f"share_link:{share_token}"
        ttl = timedelta(days=ttl_days)
        
        await self._client.setex(
            key, 
            ttl, 
            json.dumps(card_data, default=str)
        )
    
    async def delete_share_link_cache(self, share_token: str) -> None:
        key = f"share_link:{share_token}"
        await self._client.delete(key)
    
    async def check_rate_limit(self, key: str, limit: int, window_seconds: int) -> bool:
        current = await self._client.get(key)
        
        if current is None:
            await self._client.setex(key, window_seconds, 1)
            return True
        
        if int(current) >= limit:
            return False
        
        await self._client.incr(key)
        return True
