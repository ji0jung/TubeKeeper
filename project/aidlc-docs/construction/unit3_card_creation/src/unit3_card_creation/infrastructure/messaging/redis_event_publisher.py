import json
import redis.asyncio as redis
from ...domain.events.domain_events import DomainEvent
from ..config.settings import settings


class RedisEventPublisher:
    def __init__(self):
        self._redis = redis.from_url(settings.redis_url)
    
    async def publish(self, event: DomainEvent) -> None:
        event_data = {
            "event_type": event.__class__.__name__,
            "data": self._serialize_event(event),
            "occurred_at": event.occurred_at.isoformat()
        }
        
        channel = f"events.{event.__class__.__name__}"
        await self._redis.publish(channel, json.dumps(event_data))
    
    def _serialize_event(self, event: DomainEvent) -> dict:
        """Convert event to dictionary"""
        result = {}
        for key, value in event.__dict__.items():
            if hasattr(value, 'isoformat'):  # datetime
                result[key] = value.isoformat()
            elif hasattr(value, '__str__'):  # UUID, etc
                result[key] = str(value)
            else:
                result[key] = value
        return result
    
    async def close(self):
        await self._redis.close()
