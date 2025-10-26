from fastapi import APIRouter, Depends
from uuid import UUID
from typing import List, Dict
from ....application.services.card_application_service import CardApplicationService
from ....application.queries.get_user_tags_query import GetUserTagsQuery
from ..middleware.auth_middleware import get_current_user_id
from ..dependencies import get_card_application_service

router = APIRouter(prefix="/api/tags", tags=["tags"])

@router.get("/")
async def get_user_tags(
    user_id: UUID = Depends(get_current_user_id),
    card_service: CardApplicationService = Depends(get_card_application_service)
) -> dict:
    """사용자의 태그 목록 조회 (사용 빈도순)"""
    try:
        query = GetUserTagsQuery(user_id=user_id)
        tags = await card_service.get_user_tags(query)
        
        return {
            "success": True,
            "data": {"tags": tags},
            "message": "태그 목록 조회 완료"
        }
    except Exception as e:
        print(f"태그 API 오류: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "message": "태그 목록 조회 실패"
        }
