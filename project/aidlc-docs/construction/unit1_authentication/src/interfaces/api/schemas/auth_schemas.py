from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any


class RegisterRequest(BaseModel):
    """회원가입 요청 스키마"""
    email: EmailStr
    gender: Optional[str] = None
    birth_year: Optional[int] = None


class VerifyRegistrationRequest(BaseModel):
    """회원가입 인증 요청 스키마"""
    email: EmailStr
    verification_code: str


class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    email: EmailStr


class VerifyLoginRequest(BaseModel):
    """로그인 인증 요청 스키마"""
    email: EmailStr
    verification_code: str


class ProfileUpdateRequest(BaseModel):
    """프로필 수정 요청 스키마"""
    gender: Optional[str] = None
    birth_year: Optional[int] = None
    language: Optional[str] = None


class SuccessResponse(BaseModel):
    """성공 응답 스키마 (공통 형식)"""
    success: bool = True
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


class ErrorDetail(BaseModel):
    """오류 상세 정보"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """오류 응답 스키마 (공통 형식)"""
    success: bool = False
    error: ErrorDetail


# 하위 호환성을 위한 기존 스키마 (deprecated)
class AuthResponse(BaseModel):
    """인증 응답 스키마 (deprecated - 하위 호환성용)"""
    success: bool
    message: Optional[str] = None
    token: Optional[str] = None
    user: Optional[dict] = None
