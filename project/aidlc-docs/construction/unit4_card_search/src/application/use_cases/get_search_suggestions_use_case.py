"""GetSearchSuggestionsUseCase"""

from ..dto.commands import GetSearchSuggestionsQuery
from ...domain.value_objects.search_scope import SearchScope, SearchScopeType
from ...domain.services.search_suggestion_service import SearchSuggestionService
from ...domain.events.domain_events import SearchSuggestionRequested
from datetime import datetime


class GetSearchSuggestionsUseCase:
    """검색 제안 조회 유스케이스"""
    
    def __init__(self, suggestion_service: SearchSuggestionService, event_publisher):
        self._suggestion_service = suggestion_service
        self._event_publisher = event_publisher
    
    async def execute(self, query: GetSearchSuggestionsQuery):
        """검색 자동완성 제안 조회"""
        
        # 검색 범위 결정
        scope_type = SearchScopeType.MY_CARDS if query.scope == "my" else SearchScopeType.PUBLIC_CARDS
        scope = SearchScope(scope_type)
        
        # 검색 제안 조회
        suggestions = await self._suggestion_service.get_suggestions(
            query=query.query,
            user_id=query.user_id,
            scope=scope
        )
        
        # 이벤트 발행
        event = SearchSuggestionRequested(
            user_id=query.user_id,
            query=query.query,
            search_scope=scope,
            occurred_at=datetime.utcnow()
        )
        await self._event_publisher.publish(event)
        
        return suggestions
