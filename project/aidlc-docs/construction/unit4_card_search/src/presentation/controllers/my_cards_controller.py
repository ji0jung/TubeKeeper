"""MyCardsController"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException

from ..models.response_models import StandardResponse, MyCardsResponse, CardSummaryResponse
from ...application.services.search_application_service import SearchApplicationService
from ...application.dto.commands import SearchMyCardsCommand
from ...domain.services.search_query_validation_service import ValidationResult


router = APIRouter(prefix="/api/my-cards", tags=["My Cards"])


async def get_search_service() -> SearchApplicationService:
    """SearchApplicationService 의존성 주입"""
    # 실제 구현에서는 DI 컨테이너에서 주입
    pass


@router.get("")
async def search_my_cards(
    cursor: Optional[str] = Query(None, description="커서 (ISO datetime)"),
    limit: int = Query(20, ge=1, le=100, description="페이지 크기"),
    category_id: Optional[UUID] = Query(None, description="카테고리 ID"),
    search: Optional[str] = Query(None, description="검색 키워드"),
    tag: Optional[str] = Query(None, description="태그"),
    search_service: SearchApplicationService = Depends(get_search_service),
    current_user = Depends(get_current_user)  # Unit1에서 제공
) -> StandardResponse:
    """내 카드 목록 조회 (커서 기반 페이징)"""
    
    try:
        # 커서 파싱
        cursor_dt = None
        if cursor:
            try:
                cursor_dt = datetime.fromisoformat(cursor.replace('Z', '+00:00'))
            except ValueError:
                return StandardResponse.error_response(
                    "SEARCH_010", 
                    "Invalid cursor format"
                )
        
        # 검색 실행
        command = SearchMyCardsCommand(
            user_id=current_user.id,
            cursor=cursor_dt,
            limit=limit,
            category_id=category_id,
            keyword=search,
            tag=tag
        )
        
        result = await search_service.search_my_cards(command)
        
        # 응답 생성
        response_data = MyCardsResponse(
            cards=[CardSummaryResponse.from_domain_summary(card) for card in result.card_summaries],
            nextCursor=result.metadata.next_cursor.isoformat() if result.metadata.next_cursor else None,
            hasMore=result.metadata.has_more
        )
        
        return StandardResponse.success_response(
            data=response_data,
            message="Success"
        )
        
    except ValueError as e:
        return StandardResponse.error_response("SEARCH_001", str(e))
    except Exception as e:
        return StandardResponse.error_response("SEARCH_009", "Search service unavailable")


@router.get("/favorites")
async def get_favorite_cards(
    cursor: Optional[str] = Query(None, description="커서 (ISO datetime)"),
    limit: int = Query(20, ge=1, le=100, description="페이지 크기"),
    search_service: SearchApplicationService = Depends(get_search_service),
    current_user = Depends(get_current_user)
) -> StandardResponse:
    """내 즐겨찾기 카드 목록 조회"""
    
    try:
        cursor_dt = None
        if cursor:
            cursor_dt = datetime.fromisoformat(cursor.replace('Z', '+00:00'))
        
        # 즐겨찾기 필터로 검색
        command = SearchMyCardsCommand(
            user_id=current_user.id,
            cursor=cursor_dt,
            limit=limit,
            # 즐겨찾기 필터는 리포지토리에서 처리
        )
        
        result = await search_service.search_my_cards(command)
        
        response_data = MyCardsResponse(
            cards=[CardSummaryResponse.from_domain_summary(card) for card in result.card_summaries],
            nextCursor=result.metadata.next_cursor.isoformat() if result.metadata.next_cursor else None,
            hasMore=result.metadata.has_more
        )
        
        return StandardResponse.success_response(data=response_data)
        
    except Exception as e:
        return StandardResponse.error_response("SEARCH_009", "Search service unavailable")


async def get_current_user():
    """현재 사용자 조회 (Unit1에서 제공되는 의존성)"""
    # 실제 구현에서는 JWT 토큰에서 사용자 정보 추출
    pass
