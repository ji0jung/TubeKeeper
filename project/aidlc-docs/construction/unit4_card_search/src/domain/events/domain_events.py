"""Domain Events for Unit4 Card Search"""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional

from ..value_objects.search_criteria import SearchCriteria
from ..value_objects.search_scope import SearchScope


@dataclass(frozen=True)
class SearchQueryCreated:
    """검색 쿼리 생성 이벤트"""
    search_query_id: UUID
    user_id: UUID
    criteria: SearchCriteria
    scope: SearchScope
    occurred_at: datetime


@dataclass(frozen=True)
class SearchExecuted:
    """검색 실행 완료 이벤트"""
    search_query_id: UUID
    user_id: UUID
    result_count: int
    processing_time_ms: int
    occurred_at: datetime


@dataclass(frozen=True)
class PublicCardSaved:
    """공개 카드 저장 이벤트"""
    original_card_id: UUID
    new_card_id: UUID
    user_id: UUID
    category_id: UUID
    saved_at: datetime


@dataclass(frozen=True)
class SearchSuggestionRequested:
    """검색 제안 요청 이벤트"""
    user_id: UUID
    query: str
    search_scope: SearchScope
    occurred_at: datetime
