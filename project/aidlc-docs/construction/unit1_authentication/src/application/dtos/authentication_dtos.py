from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class RegisterRequestDTO:
    """회원가입 요청 DTO"""
    email: str
    gender: Optional[str] = None
    birth_year: Optional[int] = None


@dataclass
class VerifyRegistrationRequestDTO:
    """회원가입 인증 요청 DTO"""
    email: str
    verification_code: str


@dataclass
class LoginRequestDTO:
    """로그인 요청 DTO"""
    email: str


@dataclass
class VerifyLoginRequestDTO:
    """로그인 인증 요청 DTO"""
    email: str
    verification_code: str


@dataclass
class AuthResponseDTO:
    """인증 응답 DTO"""
    success: bool
    token: Optional[str] = None
    user: Optional[dict] = None
    message: Optional[str] = None
