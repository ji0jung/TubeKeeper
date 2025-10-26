import redis.asyncio as redis
from ....settings import settings

redis_client = redis.from_url(settings.redis_url)

async def check_rate_limit(key: str, limit: int, window_seconds: int) -> bool:
    try:
        current = await redis_client.get(key)
        if current is None:
            await redis_client.setex(key, window_seconds, 1)
            return True
        if int(current) >= limit:
            return False
        await redis_client.incr(key)
        return True
    except Exception:
        return True
