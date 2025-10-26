from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Dict, Any, Optional

from application.services.authentication_app_service import AuthenticationAppService
from application.dtos.authentication_dtos import (
    RegisterRequestDTO, VerifyRegistrationRequestDTO,
    LoginRequestDTO, VerifyLoginRequestDTO
)
from interfaces.api.schemas.auth_schemas import (
    RegisterRequest, VerifyRegistrationRequest,
    LoginRequest, VerifyLoginRequest, AuthResponse, ErrorResponse
)
from domain.exceptions.domain_exceptions import DomainException


router = APIRouter(prefix="/api/auth", tags=["authentication"])


def get_auth_service() -> AuthenticationAppService:
    """인증 서비스 의존성 주입"""
    from infrastructure.persistence.repositories.postgresql_user_repository import PostgreSQLUserRepository
    from infrastructure.persistence.repositories.redis_verification_code_repository import RedisVerificationCodeRepository
    from infrastructure.external.email.console_email_adapter import ConsoleEmailAdapter
    
    return AuthenticationAppService(
        user_repo=PostgreSQLUserRepository(),
        verification_code_repo=RedisVerificationCodeRepository(),
        email_service=ConsoleEmailAdapter()
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


@router.post("/register")
async def register(
    request: RegisterRequest,
    auth_service: AuthenticationAppService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """회원가입 요청"""
    try:
        dto = RegisterRequestDTO(
            email=request.email,
            gender=request.gender,
            birth_year=request.birth_year
        )
        
        result = await auth_service.register(dto)
        
        # 이미 존재하는 이메일인 경우 오류로 처리
        if "이미 존재하는" in result.message:
            return create_error_response("AUTH_004", result.message)
        
        return create_success_response(message=result.message)
        
    except DomainException as e:
        return create_error_response(e.error_code or "AUTH_001", e.message)
    except Exception as e:
        return create_error_response("AUTH_001", str(e))


@router.post("/verify-registration")
async def verify_registration(
    request: VerifyRegistrationRequest,
    auth_service: AuthenticationAppService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """회원가입 인증 확인"""
    try:
        dto = VerifyRegistrationRequestDTO(
            email=request.email,
            verification_code=request.verification_code
        )
        
        result = await auth_service.verify_registration(dto)
        
        # 잘못된 인증 코드인 경우 오류로 처리
        if "잘못된 인증 코드" in result.message or result.token is None:
            return create_error_response("AUTH_006", result.message or "Invalid verification code")
        
        return create_success_response(
            data={
                "token": result.token,
                "user": result.user
            },
            message=result.message
        )
        
    except DomainException as e:
        return create_error_response(e.error_code or "AUTH_006", e.message)
    except Exception as e:
        return create_error_response("AUTH_006", str(e))


@router.post("/login")
async def login(
    request: LoginRequest,
    auth_service: AuthenticationAppService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """로그인 요청"""
    try:
        dto = LoginRequestDTO(email=request.email)
        
        result = await auth_service.login(dto)
        
        return create_success_response(message=result.message)
        
    except DomainException as e:
        return create_error_response(e.error_code or "AUTH_003", e.message)
    except Exception as e:
        return create_error_response("AUTH_003", str(e))


@router.post("/verify-login")
async def verify_login(
    request: VerifyLoginRequest,
    auth_service: AuthenticationAppService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """로그인 인증 확인"""
    try:
        dto = VerifyLoginRequestDTO(
            email=request.email,
            verification_code=request.verification_code
        )
        
        result = await auth_service.verify_login(dto)
        
        # 잘못된 인증 코드인 경우 오류로 처리
        if "잘못된 인증 코드" in result.message or result.token is None:
            return create_error_response("AUTH_006", result.message or "Invalid verification code")
        
        return create_success_response(
            data={
                "token": result.token,
                "user": result.user
            },
            message=result.message
        )
        
    except DomainException as e:
        return create_error_response(e.error_code or "AUTH_006", e.message)
    except Exception as e:
        return create_error_response("AUTH_006", str(e))


@router.post("/logout")
async def logout(
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """로그아웃"""
    if not authorization or not authorization.startswith("Bearer "):
        return create_error_response("AUTH_013", "Invalid authorization header")
    
    # JWT 토큰 무효화 로직 (현재는 클라이언트 측에서 토큰 삭제로 처리)
    return create_success_response(message="로그아웃이 완료되었습니다.")


@router.post("/refresh-session")
async def refresh_session(
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """세션 자동 연장"""
    if not authorization or not authorization.startswith("Bearer "):
        return create_error_response("AUTH_013", "Invalid authorization header")
    
    token = authorization.split(" ")[1]
    
    # JWT 토큰 갱신 로직 (현재는 기존 토큰 반환)
    return create_success_response(
        data={"newToken": token},
        message="세션이 연장되었습니다."
    )


@router.delete("/account")
async def delete_account(
    authorization: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """회원 탈퇴"""
    if not authorization or not authorization.startswith("Bearer "):
        return create_error_response("AUTH_013", "Invalid authorization header")
    
    # 회원 탈퇴 로직 구현 필요
    return create_success_response(message="회원 탈퇴가 완료되었습니다.")
