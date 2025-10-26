import json
from dataclasses import asdict
import redis.asyncio as redis

from ...domain.services.event_publisher import EventPublisher
from ...domain.events.base import DomainEvent
from ...config.settings import settings

class RedisEventPublisher(EventPublisher):
    
    def __init__(self):
        self._redis = redis.from_url(settings.redis_url)
    
    async def publish(self, event: DomainEvent) -> None:
        channel = f"category.{event.__class__.__name__.lower()}"
        message = json.dumps(asdict(event), default=str)
        await self._redis.publish(channel, message)
