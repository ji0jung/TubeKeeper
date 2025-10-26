"""SearchMyCardsUseCase"""

from datetime import datetime
from ..dto.commands import SearchMyCardsCommand
from ...domain.entities.search_query import SearchQuery
from ...domain.value_objects.search_criteria import SearchCriteria
from ...domain.value_objects.search_scope import SearchScope
from ...domain.value_objects.pagination_info import PaginationInfo
from ...domain.services.search_query_validation_service import SearchQueryValidationService
from ...domain.services.search_execution_service import SearchExecutionService


class SearchMyCardsUseCase:
    """내 카드 검색 유스케이스"""
    
    def __init__(self, validation_service: SearchQueryValidationService,
                 execution_service: SearchExecutionService):
        self._validation_service = validation_service
        self._execution_service = execution_service
    
    async def execute(self, command: SearchMyCardsCommand):
        """내 카드 검색 실행"""
        # 검색 조건 생성
        criteria = SearchCriteria(
            keyword=command.keyword,
            tag=command.tag,
            category_id=command.category_id
        )
        
        scope = SearchScope.my_cards()
        
        pagination = PaginationInfo.cursor_based(
            cursor=command.cursor,
            limit=command.limit
        )
        
        # 유효성 검증
        validation_result = self._validation_service.validate_search_criteria(criteria, scope)
        if not validation_result.is_valid:
            raise ValueError(validation_result.error_message)
        
        # 검색 쿼리 생성
        search_query = SearchQuery.create(
            user_id=command.user_id,
            criteria=criteria,
            scope=scope,
            pagination_info=pagination
        )
        
        # 검색 실행
        return await self._execution_service.execute_my_card_search(search_query)
