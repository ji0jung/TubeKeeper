"""SearchApplicationService"""

from ..use_cases.search_my_cards_use_case import SearchMyCardsUseCase
from ..use_cases.search_public_cards_use_case import SearchPublicCardsUseCase
from ..use_cases.save_public_card_use_case import SavePublicCardUseCase
from ..use_cases.get_search_suggestions_use_case import GetSearchSuggestionsUseCase
from ..dto.commands import (
    SearchMyCardsCommand, 
    SearchPublicCardsCommand, 
    SavePublicCardCommand,
    GetSearchSuggestionsQuery,
    GetTagsQuery
)


class SearchApplicationService:
    """검색 애플리케이션 서비스"""
    
    def __init__(self, 
                 search_my_cards_use_case: SearchMyCardsUseCase,
                 search_public_cards_use_case: SearchPublicCardsUseCase,
                 save_public_card_use_case: SavePublicCardUseCase,
                 get_suggestions_use_case: GetSearchSuggestionsUseCase,
                 suggestion_service):
        self._search_my_cards_use_case = search_my_cards_use_case
        self._search_public_cards_use_case = search_public_cards_use_case
        self._save_public_card_use_case = save_public_card_use_case
        self._get_suggestions_use_case = get_suggestions_use_case
        self._suggestion_service = suggestion_service
    
    async def search_my_cards(self, command: SearchMyCardsCommand):
        """내 카드 검색"""
        return await self._search_my_cards_use_case.execute(command)
    
    async def search_public_cards(self, command: SearchPublicCardsCommand):
        """공개 카드 검색"""
        return await self._search_public_cards_use_case.execute(command)
    
    async def save_public_card(self, command: SavePublicCardCommand):
        """공개 카드 저장"""
        return await self._save_public_card_use_case.execute(command)
    
    async def get_search_suggestions(self, query: GetSearchSuggestionsQuery):
        """검색 제안 조회"""
        return await self._get_suggestions_use_case.execute(query)
    
    async def get_tags(self, query: GetTagsQuery):
        """태그 목록 조회"""
        from ...domain.value_objects.search_scope import SearchScope, SearchScopeType
        
        scope_type = SearchScopeType.MY_CARDS if query.scope == "my" else SearchScopeType.PUBLIC_CARDS
        scope = SearchScope(scope_type)
        
        if scope.is_my_cards():
            return await self._suggestion_service.get_my_card_tags(query.user_id)
        else:
            return await self._suggestion_service.get_popular_tags(scope)
