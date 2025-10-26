"""PublicCardsController"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from pydantic import BaseModel

from ..models.response_models import StandardResponse, PublicCardsResponse, SavePublicCardResponse, CardSummaryResponse
from ...application.services.search_application_service import SearchApplicationService
from ...application.dto.commands import SearchPublicCardsCommand, SavePublicCardCommand
from ...domain.services.public_card_saving_service import PublicCardNotFoundError, DuplicateCardError


router = APIRouter(prefix="/api/public-cards", tags=["Public Cards"])


class SavePublicCardRequest(BaseModel):
    """공개 카드 저장 요청"""
    categoryId: Optional[UUID] = None


@router.get("")
async def search_public_cards(
    page: int = Query(1, ge=1, description="페이지 번호"),
    limit: int = Query(20, ge=1, le=100, description="페이지 크기"),
    search: Optional[str] = Query(None, description="검색 키워드"),
    tag: Optional[str] = Query(None, description="태그"),
    search_service: SearchApplicationService = Depends(get_search_service),
    current_user = Depends(get_current_user)
) -> StandardResponse:
    """공개 카드 검색 (오프셋 기반 페이징)"""
    
    try:
        # 검색 조건 검증 (키워드와 태그 동시 사용 불가)
        if search and tag:
            return StandardResponse.error_response(
                "SEARCH_001", 
                "Cannot use both search keyword and tag simultaneously"
            )
        
        if not search and not tag:
            return StandardResponse.error_response(
                "SEARCH_001", 
                "Either search keyword or tag is required"
            )
        
        # 검색 실행
        command = SearchPublicCardsCommand(
            user_id=current_user.id,
            page=page,
            limit=limit,
            keyword=search,
            tag=tag
        )
        
        result = await search_service.search_public_cards(command)
        
        # 총 페이지 수 계산
        total_pages = (result.metadata.total_count + limit - 1) // limit if result.metadata.total_count else 0
        
        response_data = PublicCardsResponse(
            cards=[CardSummaryResponse.from_domain_summary(card) for card in result.card_summaries],
            totalCount=result.metadata.total_count or 0,
            currentPage=page,
            totalPages=total_pages
        )
        
        return StandardResponse.success_response(
            data=response_data,
            message="Success"
        )
        
    except ValueError as e:
        return StandardResponse.error_response("SEARCH_001", str(e))
    except Exception as e:
        return StandardResponse.error_response("SEARCH_009", "Search service unavailable")


@router.post("/{card_id}/save")
async def save_public_card(
    card_id: UUID = Path(..., description="저장할 공개 카드 ID"),
    request: SavePublicCardRequest = Body(...),
    search_service: SearchApplicationService = Depends(get_search_service),
    current_user = Depends(get_current_user)
) -> StandardResponse:
    """공개 카드를 내 계정에 독립적으로 복사 저장"""
    
    try:
        command = SavePublicCardCommand(
            card_id=card_id,
            user_id=current_user.id,
            category_id=request.categoryId
        )
        
        result = await search_service.save_public_card(command)
        
        if result.already_exists:
            response_data = SavePublicCardResponse(alreadyExists=True)
            return StandardResponse.success_response(
                data=response_data,
                message="Card already exists in your collection"
            )
        
        response_data = SavePublicCardResponse(
            newCard=CardSummaryResponse.from_domain_summary(result.new_card) if result.new_card else None,
            alreadyExists=False
        )
        
        return StandardResponse.success_response(
            data=response_data,
            message="Card saved successfully"
        )
        
    except PublicCardNotFoundError:
        return StandardResponse.error_response("SEARCH_006", "Public card not found")
    except DuplicateCardError:
        return StandardResponse.error_response("SEARCH_007", "Card already saved")
    except Exception as e:
        return StandardResponse.error_response("SEARCH_008", "Save permission denied")


async def get_search_service() -> SearchApplicationService:
    """SearchApplicationService 의존성 주입"""
    pass


async def get_current_user():
    """현재 사용자 조회"""
    pass
