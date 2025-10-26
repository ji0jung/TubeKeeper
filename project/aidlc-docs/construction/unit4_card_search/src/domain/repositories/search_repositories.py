"""Repository Interfaces for Unit4 Search"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from ..entities.search_query import SearchQuery
from ..entities.search_result import SearchResult
from ..entities.card_summary import CardSummary
from ..value_objects.search_criteria import SearchCriteria
from ..value_objects.pagination_info import PaginationInfo
from ..value_objects.search_scope import SearchScope
from ..services.search_suggestion_service import TagSuggestion


class ISearchQueryRepository(ABC):
    """검색 쿼리 리포지토리 인터페이스"""
    
    @abstractmethod
    async def save(self, search_query: SearchQuery) -> None:
        pass
    
    @abstractmethod
    async def find_by_id(self, search_query_id: UUID) -> Optional[SearchQuery]:
        pass
    
    @abstractmethod
    async def find_recent_by_user(self, user_id: UUID, limit: int) -> List[SearchQuery]:
        pass
    
    @abstractmethod
    async def delete(self, search_query_id: UUID) -> None:
        pass


class ISearchResultRepository(ABC):
    """검색 결과 리포지토리 인터페이스"""
    
    @abstractmethod
    async def save(self, search_result: SearchResult) -> None:
        pass
    
    @abstractmethod
    async def find_by_query_id(self, search_query_id: UUID) -> Optional[SearchResult]:
        pass
    
    @abstractmethod
    async def find_expired_results(self) -> List[SearchResult]:
        pass
    
    @abstractmethod
    async def delete(self, search_result_id: UUID) -> None:
        pass


class SearchResultData:
    """검색 결과 데이터 클래스"""
    def __init__(self, cards: List[CardSummary], total_count: int = 0):
        self.cards = cards
        self.total_count = total_count


class ICardSearchRepository(ABC):
    """카드 검색 리포지토리 인터페이스"""
    
    @abstractmethod
    async def search_my_cards(self, user_id: UUID, criteria: SearchCriteria, 
                            pagination: PaginationInfo) -> List[CardSummary]:
        pass
    
    @abstractmethod
    async def search_public_cards(self, criteria: SearchCriteria, pagination: PaginationInfo,
                                exclude_user_id: UUID) -> SearchResultData:
        pass
    
    @abstractmethod
    async def get_card_summary(self, card_id: UUID) -> Optional[CardSummary]:
        pass
    
    @abstractmethod
    async def get_public_card(self, card_id: UUID) -> Optional[CardSummary]:
        pass
    
    @abstractmethod
    async def count_my_cards(self, user_id: UUID, criteria: SearchCriteria) -> int:
        pass
    
    @abstractmethod
    async def count_public_cards(self, criteria: SearchCriteria) -> int:
        pass


class ISearchSuggestionRepository(ABC):
    """검색 제안 리포지토리 인터페이스"""
    
    @abstractmethod
    async def get_recent_searches(self, user_id: UUID, limit: int) -> List[str]:
        pass
    
    @abstractmethod
    async def save_recent_search(self, user_id: UUID, query: str) -> None:
        pass
    
    @abstractmethod
    async def get_my_card_tags(self, user_id: UUID) -> List[TagSuggestion]:
        pass
    
    @abstractmethod
    async def get_popular_tags(self, scope: SearchScope, limit: int) -> List[TagSuggestion]:
        pass
