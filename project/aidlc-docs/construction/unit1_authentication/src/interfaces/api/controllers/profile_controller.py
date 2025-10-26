from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Dict, Any, Optional
from uuid import UUID

from application.services.profile_app_service import ProfileAppService
from infrastructure.persistence.repositories.postgresql_profile_repository import PostgreSQLProfileRepository
from infrastructure.persistence.repositories.postgresql_user_repository import PostgreSQLUserRepository
from interfaces.api.schemas.auth_schemas import ProfileUpdateRequest
from common.jwt_utils import extract_user_id_from_token
from domain.exceptions.domain_exceptions import DomainException


router = APIRouter(prefix="/api", tags=["profile"])


def get_profile_service() -> ProfileAppService:
    """프로필 서비스 의존성 주입"""
    return ProfileAppService(
        profile_repo=PostgreSQLProfileRepository(),
        user_repo=PostgreSQLUserRepository()
    )


def create_error_response(error_code: str, message: str, details: Dict = None) -> Dict[str, Any]:
    """표준 오류 응답 생성"""
    return {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {}
        }
    }


def create_success_response(data: Dict = None, message: str = None) -> Dict[str, Any]:
    """표준 성공 응답 생성"""
    response = {"success": True}
    if data:
        response["data"] = data
    if message:
        response["message"] = message
    return response


def get_current_user_from_token(authorization: Optional[str] = Header(None)) -> UUID:
    """JWT 토큰에서 사용자 정보 추출"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="AUTH_013: Invalid authorization header")
    
    token = authorization.split(" ")[1]
    try:
        return extract_user_id_from_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="AUTH_002: Token expired")


@router.get("/profile")
async def get_profile(
    user_id: UUID = Depends(get_current_user_from_token),
    profile_service: ProfileAppService = Depends(get_profile_service)
) -> Dict[str, Any]:
    """프로필 정보 조회"""
    try:
        user_profile = await profile_service.get_profile(user_id)
        return create_success_response(
            data={"user": user_profile}
        )
    except DomainException as e:
        return create_error_response(e.error_code or "AUTH_012", e.message)
    except Exception as e:
        return create_error_response("AUTH_012", str(e))


@router.put("/profile")
async def update_profile(
    request: ProfileUpdateRequest,
    user_id: UUID = Depends(get_current_user_from_token),
    profile_service: ProfileAppService = Depends(get_profile_service)
) -> Dict[str, Any]:
    """프로필 정보 수정"""
    try:
        updated_profile = await profile_service.update_profile(
            user_id=user_id,
            gender=request.gender,
            birth_year=request.birth_year,
            language=request.language
        )
        return create_success_response(
            data={"user": updated_profile},
            message="프로필이 수정되었습니다."
        )
    except DomainException as e:
        error_code = e.error_code or "AUTH_012"
        if "gender" in str(e).lower():
            error_code = "AUTH_009"
        elif "birth" in str(e).lower():
            error_code = "AUTH_008"
        elif "language" in str(e).lower():
            error_code = "AUTH_010"
        return create_error_response(error_code, e.message)
    except Exception as e:
        return create_error_response("AUTH_012", str(e))
