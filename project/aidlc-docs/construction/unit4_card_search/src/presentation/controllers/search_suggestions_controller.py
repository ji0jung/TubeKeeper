"""SearchSuggestionsController"""

from typing import Optional
from fastapi import APIRouter, Depends, Query

from ..models.response_models import StandardResponse, SearchSuggestionsResponse, TagsResponse, SearchSuggestion, TagInfo
from ...application.services.search_application_service import SearchApplicationService
from ...application.dto.commands import GetSearchSuggestionsQuery, GetTagsQuery


router = APIRouter(prefix="/api/search", tags=["Search Suggestions"])


@router.get("/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=1, description="검색 쿼리"),
    scope: str = Query("my", regex="^(my|public)$", description="검색 범위"),
    search_service: SearchApplicationService = Depends(get_search_service),
    current_user = Depends(get_current_user)
) -> StandardResponse:
    """검색 자동완성 제안"""
    
    try:
        if len(query.strip()) < 2:
            return StandardResponse.error_response(
                "SEARCH_002", 
                "Query must be at least 2 characters"
            )
        
        suggestions_query = GetSearchSuggestionsQuery(
            user_id=current_user.id,
            query=query.strip(),
            scope=scope
        )
        
        suggestions = await search_service.get_search_suggestions(suggestions_query)
        
        response_data = SearchSuggestionsResponse(
            suggestions=[
                SearchSuggestion(type=s.type, value=s.value) 
                for s in suggestions
            ]
        )
        
        return StandardResponse.success_response(
            data=response_data,
            message="Success"
        )
        
    except ValueError as e:
        return StandardResponse.error_response("SEARCH_002", str(e))
    except Exception as e:
        return StandardResponse.error_response("SEARCH_009", "Search service unavailable")


@router.get("/tags")
async def get_tags(
    scope: str = Query("my", regex="^(my|public)$", description="검색 범위"),
    search_service: SearchApplicationService = Depends(get_search_service),
    current_user = Depends(get_current_user)
) -> StandardResponse:
    """태그 목록 (내 카드 또는 공개 카드)"""
    
    try:
        tags_query = GetTagsQuery(
            user_id=current_user.id,
            scope=scope
        )
        
        tags = await search_service.get_tags(tags_query)
        
        response_data = TagsResponse(
            tags=[TagInfo(name=tag.name, count=tag.count) for tag in tags]
        )
        
        return StandardResponse.success_response(
            data=response_data,
            message="Success"
        )
        
    except Exception as e:
        return StandardResponse.error_response("SEARCH_009", "Search service unavailable")


async def get_search_service() -> SearchApplicationService:
    """SearchApplicationService 의존성 주입"""
    pass


async def get_current_user():
    """현재 사용자 조회"""
    pass
