"""Event Publisher Implementation"""

import json
from typing import Any
import aioredis

from ...domain.events.domain_events import (
    SearchQueryCreated, SearchExecuted, PublicCardSaved, SearchSuggestionRequested
)


class RedisEventPublisher:
    """Redis 기반 이벤트 발행자"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self._redis = redis_client
    
    async def publish(self, event: Any) -> None:
        """도메인 이벤트 발행"""
        try:
            event_data = self._serialize_event(event)
            channel = f"events:{event.__class__.__name__}"
            await self._redis.publish(channel, json.dumps(event_data))
        except Exception as e:
            # 이벤트 발행 실패는 로깅만 하고 서비스는 계속 진행
            print(f"Failed to publish event: {e}")
    
    def _serialize_event(self, event: Any) -> dict:
        """이벤트 직렬화"""
        if isinstance(event, SearchQueryCreated):
            return {
                'event_type': 'SearchQueryCreated',
                'search_query_id': str(event.search_query_id),
                'user_id': str(event.user_id),
                'occurred_at': event.occurred_at.isoformat()
            }
        elif isinstance(event, SearchExecuted):
            return {
                'event_type': 'SearchExecuted',
                'search_query_id': str(event.search_query_id),
                'user_id': str(event.user_id),
                'result_count': event.result_count,
                'processing_time_ms': event.processing_time_ms,
                'occurred_at': event.occurred_at.isoformat()
            }
        elif isinstance(event, PublicCardSaved):
            return {
                'event_type': 'PublicCardSaved',
                'original_card_id': str(event.original_card_id),
                'new_card_id': str(event.new_card_id),
                'user_id': str(event.user_id),
                'category_id': str(event.category_id),
                'saved_at': event.saved_at.isoformat()
            }
        elif isinstance(event, SearchSuggestionRequested):
            return {
                'event_type': 'SearchSuggestionRequested',
                'user_id': str(event.user_id),
                'query': event.query,
                'occurred_at': event.occurred_at.isoformat()
            }
        else:
            return {
                'event_type': event.__class__.__name__,
                'data': str(event)
            }
