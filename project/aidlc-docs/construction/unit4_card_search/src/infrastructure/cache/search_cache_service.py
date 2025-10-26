"""Redis Cache Service for Search"""

import json
import hashlib
from typing import Optional, Any
from datetime import datetime, timedelta
import aioredis

from ...domain.entities.search_result import SearchResult
from ...domain.entities.card_summary import CardSummary
from ...domain.value_objects.result_metadata import ResultMetadata


class SearchCacheService:
    """검색 결과 캐싱 서비스"""
    
    def __init__(self, redis_client: aioredis.Redis):
        self._redis = redis_client
    
    async def get_search_result(self, cache_key: str) -> Optional[SearchResult]:
        """캐시된 검색 결과 조회"""
        try:
            cached_data = await self._redis.get(cache_key)
            if not cached_data:
                return None
            
            data = json.loads(cached_data)
            return self._deserialize_search_result(data)
        except Exception:
            return None
    
    async def set_search_result(self, cache_key: str, result: SearchResult, ttl_seconds: int) -> None:
        """검색 결과 캐싱"""
        try:
            serialized_data = self._serialize_search_result(result)
            await self._redis.setex(cache_key, ttl_seconds, json.dumps(serialized_data))
        except Exception:
            pass  # 캐싱 실패해도 서비스는 계속 동작
    
    async def invalidate_user_cache(self, user_id: str) -> None:
        """사용자별 캐시 무효화"""
        pattern = f"search:my:{user_id}:*"
        try:
            keys = await self._redis.keys(pattern)
            if keys:
                await self._redis.delete(*keys)
        except Exception:
            pass
    
    async def invalidate_public_cache(self) -> None:
        """공개 카드 캐시 무효화"""
        pattern = "search:public:*"
        try:
            keys = await self._redis.keys(pattern)
            if keys:
                await self._redis.delete(*keys)
        except Exception:
            pass
    
    def generate_cache_key(self, prefix: str, user_id: str, **kwargs) -> str:
        """캐시 키 생성"""
        key_data = f"{prefix}:{user_id}:{json.dumps(kwargs, sort_keys=True)}"
        return f"{prefix}:{user_id}:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def _serialize_search_result(self, result: SearchResult) -> dict:
        """SearchResult 직렬화"""
        return {
            'id': str(result.id),
            'search_query_id': str(result.search_query_id),
            'cards': [self._serialize_card_summary(card) for card in result.card_summaries],
            'metadata': self._serialize_metadata(result.metadata),
            'generated_at': result.generated_at.isoformat(),
            'expires_at': result.expires_at.isoformat()
        }
    
    def _serialize_card_summary(self, card: CardSummary) -> dict:
        """CardSummary 직렬화"""
        return {
            'card_id': str(card.card_id),
            'title': card.title,
            'thumbnail': card.thumbnail,
            'summary': card.summary,
            'tags': card.tags,
            'category_name': card.category_name,
            'owner_name': card.owner_name,
            'is_favorite': card.is_favorite,
            'is_public': card.is_public,
            'created_at': card.created_at.isoformat() if card.created_at else None
        }
    
    def _serialize_metadata(self, metadata: ResultMetadata) -> dict:
        """ResultMetadata 직렬화"""
        return {
            'total_count': metadata.total_count,
            'has_more': metadata.has_more,
            'next_cursor': metadata.next_cursor.isoformat() if metadata.next_cursor else None,
            'next_page': metadata.next_page,
            'processing_time_ms': metadata.processing_time_ms
        }
    
    def _deserialize_search_result(self, data: dict) -> SearchResult:
        """SearchResult 역직렬화"""
        from uuid import UUID
        
        cards = [self._deserialize_card_summary(card_data) for card_data in data['cards']]
        metadata = self._deserialize_metadata(data['metadata'])
        
        return SearchResult(
            id=UUID(data['id']),
            search_query_id=UUID(data['search_query_id']),
            card_summaries=cards,
            metadata=metadata,
            generated_at=datetime.fromisoformat(data['generated_at']),
            expires_at=datetime.fromisoformat(data['expires_at'])
        )
    
    def _deserialize_card_summary(self, data: dict) -> CardSummary:
        """CardSummary 역직렬화"""
        from uuid import UUID
        
        return CardSummary(
            card_id=UUID(data['card_id']),
            title=data['title'],
            thumbnail=data['thumbnail'],
            summary=data['summary'],
            tags=data['tags'],
            category_name=data['category_name'],
            owner_name=data['owner_name'],
            is_favorite=data['is_favorite'],
            is_public=data['is_public'],
            created_at=datetime.fromisoformat(data['created_at']) if data['created_at'] else None
        )
    
    def _deserialize_metadata(self, data: dict) -> ResultMetadata:
        """ResultMetadata 역직렬화"""
        return ResultMetadata(
            total_count=data['total_count'],
            has_more=data['has_more'],
            next_cursor=datetime.fromisoformat(data['next_cursor']) if data['next_cursor'] else None,
            next_page=data['next_page'],
            processing_time_ms=data['processing_time_ms']
        )
