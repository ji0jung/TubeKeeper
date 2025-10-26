from fastapi import APIRouter, Depends, HTTPException, status, Query
from uuid import UUID
from typing import Optional
from ..dtos.request_dtos import CreateCardRequest, UpdateCardRequest
from ..dtos.response_dtos import (
    CreateCardResponse, CardDetailResponse, CardListResponse, 
    ToggleFavoriteResponse, CardSummaryResponse
)
from ..middleware.auth_middleware import get_current_user_id
from ..dependencies import get_card_application_service
from ....application.services.card_application_service import CardApplicationService
from ....application.commands.commands import CreateCardCommand, ToggleFavoriteCommand
from ....application.queries.queries import GetCardQuery, GetCardsByUserQuery

router = APIRouter(prefix="/api/cards", tags=["cards"])


@router.post("/", response_model=CreateCardResponse)
async def create_card(
    request: CreateCardRequest,
    user_id: UUID = Depends(get_current_user_id),
    card_service: CardApplicationService = Depends(get_card_application_service)
):
    try:
        command = CreateCardCommand(
            user_id=user_id,
            category_id=request.category_id,
            content_url=request.content_url,
            memo=request.memo,
            tags=request.tags or []
        )
        
        result = await card_service.create_card(command)
        
        return CreateCardResponse(
            success=True,
            data={
                "card_id": result.card_id,
                "status": result.status
            },
            message=result.message
        )
    except ValueError as e:
        return CreateCardResponse(
            success=False,
            data={},
            message=str(e)
        )
    except Exception as e:
        return CreateCardResponse(
            success=False,
            data={},
            message="카드 생성 중 오류가 발생했습니다"
        )


@router.get("/", response_model=dict)
async def get_cards(
    limit: int = Query(20, le=100),
    cursor: Optional[str] = Query(None),
    favorites_only: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    card_service: CardApplicationService = Depends(get_card_application_service)
):
    query = GetCardsByUserQuery(
        user_id=user_id,
        limit=limit,
        cursor=cursor,
        favorites_only=favorites_only
    )
    
    result = await card_service.get_cards_by_user(query)
    
    return {
        "success": True,
        "data": {
            "cards": [
                {
                    "card_id": card.card_id,
                    "content_url": card.content_url,
                    "video_title": card.video_title,
                    "thumbnail_url": card.thumbnail_url,
                    "is_favorite": card.is_favorite,
                    "created_at": card.created_at
                } for card in result.cards
            ],
            "next_cursor": result.next_cursor,
            "has_more": result.has_more
        },
        "message": "카드 목록 조회 완료"
    }


@router.get("/{card_id}", response_model=dict)
async def get_card(
    card_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    card_service: CardApplicationService = Depends(get_card_application_service)
):
    query = GetCardQuery(card_id=card_id, user_id=user_id)
    result = await card_service.get_card(query)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    return {
        "success": True,
        "data": {"card": result.__dict__},
        "message": "카드 조회 완료"
    }


@router.post("/{card_id}/favorite", response_model=ToggleFavoriteResponse)
async def toggle_favorite(
    card_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    card_service: CardApplicationService = Depends(get_card_application_service)
):
    command = ToggleFavoriteCommand(card_id=card_id, user_id=user_id)
    is_favorite = await card_service.toggle_favorite(command)
    
    return ToggleFavoriteResponse(
        success=True,
        data={"is_favorite": is_favorite},
        message="즐겨찾기가 변경되었습니다"
    )


@router.put("/{card_id}", response_model=dict)
async def update_card(
    card_id: UUID,
    request: UpdateCardRequest,
    user_id: UUID = Depends(get_current_user_id),
    card_service: CardApplicationService = Depends(get_card_application_service)
):
    # 카드 존재 및 권한 확인
    existing_card = await card_service.get_card(GetCardQuery(card_id=card_id, user_id=user_id))
    if not existing_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # 수정 로직 (현재는 메모와 태그만 수정 가능)
    success = await card_service.update_card_metadata(card_id, user_id, request.memo, request.tags)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update card"
        )
    
    # 수정된 카드 반환
    updated_card = await card_service.get_card(GetCardQuery(card_id=card_id, user_id=user_id))
    return {
        "success": True,
        "data": {"card": updated_card.__dict__},
        "message": "카드 수정 완료"
    }


@router.delete("/{card_id}")
async def delete_card(
    card_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    card_service: CardApplicationService = Depends(get_card_application_service)
):
    # 카드 존재 및 권한 확인
    existing_card = await card_service.get_card(GetCardQuery(card_id=card_id, user_id=user_id))
    if not existing_card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # 삭제 실행
    success = await card_service.delete_card(card_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete card"
        )
    
    return {
        "success": True,
        "data": {},
        "message": "카드가 삭제되었습니다"
    }
