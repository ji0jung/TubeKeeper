"""SearchExecutionService"""

from typing import List
from uuid import UUID
from datetime import datetime

from ..entities.search_query import SearchQuery
from ..entities.search_result import SearchResult
from ..entities.card_summary import CardSummary
from ..value_objects.result_metadata import ResultMetadata


class SearchExecutionService:
    """검색 실행 및 결과 생성 서비스"""
    
    def __init__(self, card_search_repository):
        self._card_search_repository = card_search_repository
    
    async def execute_my_card_search(self, query: SearchQuery) -> SearchResult:
        """내 카드 검색 실행"""
        start_time = datetime.utcnow()
        
        # 검색 실행
        cards = await self._card_search_repository.search_my_cards(
            user_id=query.user_id,
            criteria=query.criteria,
            pagination=query.pagination_info
        )
        
        # 처리 시간 계산
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # 다음 커서 및 has_more 계산
        has_more = len(cards) > query.pagination_info.limit
        actual_cards = cards[:query.pagination_info.limit] if has_more else cards
        next_cursor = actual_cards[-1].created_at if actual_cards and has_more else None
        
        # 메타데이터 생성
        metadata = ResultMetadata.cursor_based(
            has_more=has_more,
            next_cursor=next_cursor,
            processing_time_ms=processing_time
        )
        
        return SearchResult.create(
            search_query_id=query.id,
            card_summaries=actual_cards,
            metadata=metadata,
            ttl_minutes=3  # 내 카드는 3분 TTL
        )
    
    async def execute_public_card_search(self, query: SearchQuery) -> SearchResult:
        """공개 카드 검색 실행"""
        start_time = datetime.utcnow()
        
        # 검색 실행
        result = await self._card_search_repository.search_public_cards(
            criteria=query.criteria,
            pagination=query.pagination_info,
            exclude_user_id=query.user_id
        )
        
        # 처리 시간 계산
        processing_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        # 메타데이터 생성
        total_pages = (result.total_count + query.pagination_info.limit - 1) // query.pagination_info.limit
        metadata = ResultMetadata.offset_based(
            total_count=result.total_count,
            current_page=query.pagination_info.page or 1,
            limit=query.pagination_info.limit,
            processing_time_ms=processing_time
        )
        
        return SearchResult.create(
            search_query_id=query.id,
            card_summaries=result.cards,
            metadata=metadata,
            ttl_minutes=5  # 공개 카드는 5분 TTL
        )
    
    def apply_category_filter(self, cards: List[CardSummary], category_id: UUID) -> List[CardSummary]:
        """카테고리 필터 적용"""
        # 실제 구현에서는 데이터베이스 레벨에서 필터링
        return [card for card in cards if card.category_name is not None]
    
    def apply_tag_filter(self, cards: List[CardSummary], tag: str) -> List[CardSummary]:
        """태그 필터 적용"""
        return [card for card in cards if tag in card.tags]
    
    def apply_keyword_filter(self, cards: List[CardSummary], keyword: str) -> List[CardSummary]:
        """키워드 필터 적용"""
        keyword_lower = keyword.lower()
        return [
            card for card in cards 
            if keyword_lower in card.title.lower() or keyword_lower in card.summary.lower()
        ]
