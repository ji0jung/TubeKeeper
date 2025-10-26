"""SearchSuggestionService"""

from typing import List
from uuid import UUID
from dataclasses import dataclass

from ..value_objects.search_scope import SearchScope


@dataclass
class SearchSuggestion:
    type: str  # 'recent', 'tag', 'popular'
    value: str
    count: int = 0


@dataclass
class TagSuggestion:
    name: str
    count: int


class SearchSuggestionService:
    """검색 자동완성 제안 생성 서비스"""
    
    def __init__(self, suggestion_repository):
        self._suggestion_repository = suggestion_repository
    
    async def get_suggestions(self, query: str, user_id: UUID, scope: SearchScope) -> List[SearchSuggestion]:
        """검색 제안 생성 (최근 검색어 3개 + 내 카드 태그 4개 + 인기 태그 3개)"""
        suggestions = []
        
        # 1. 최근 검색어 (3개)
        recent_searches = await self._suggestion_repository.get_recent_searches(user_id, limit=3)
        for search in recent_searches:
            if query.lower() in search.lower():
                suggestions.append(SearchSuggestion(type='recent', value=search))
        
        # 2. 내 카드 태그 (4개) - 내 카드 검색 시에만
        if scope.is_my_cards():
            my_tags = await self._suggestion_repository.get_my_card_tags(user_id)
            matching_tags = [tag for tag in my_tags if query.lower() in tag.name.lower()][:4]
            for tag in matching_tags:
                suggestions.append(SearchSuggestion(type='tag', value=tag.name, count=tag.count))
        
        # 3. 인기 태그 (3개)
        popular_tags = await self._suggestion_repository.get_popular_tags(scope, limit=3)
        for tag in popular_tags:
            if query.lower() in tag.name.lower() and not any(s.value == tag.name for s in suggestions):
                suggestions.append(SearchSuggestion(type='popular', value=tag.name, count=tag.count))
        
        # 총 10개로 제한
        return suggestions[:10]
    
    async def get_recent_searches(self, user_id: UUID) -> List[str]:
        """최근 검색어 목록"""
        return await self._suggestion_repository.get_recent_searches(user_id, limit=10)
    
    async def get_my_card_tags(self, user_id: UUID) -> List[TagSuggestion]:
        """내 카드 태그 목록"""
        return await self._suggestion_repository.get_my_card_tags(user_id)
    
    async def get_popular_tags(self, scope: SearchScope) -> List[TagSuggestion]:
        """인기 태그 목록"""
        return await self._suggestion_repository.get_popular_tags(scope, limit=20)
    
    async def save_recent_search(self, user_id: UUID, query: str) -> None:
        """최근 검색어 저장"""
        if len(query.strip()) >= 2:  # 최소 길이 확인
            await self._suggestion_repository.save_recent_search(user_id, query.strip())
