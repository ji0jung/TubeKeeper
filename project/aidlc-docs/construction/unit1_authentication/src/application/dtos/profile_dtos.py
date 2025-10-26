from dataclasses import dataclass
from typing import Optional


@dataclass
class ProfileResponseDTO:
    """프로필 응답 DTO"""
    email: str
    gender: Optional[str]
    birth_year: Optional[int]
    language: str


@dataclass
class UpdateProfileRequestDTO:
    """프로필 업데이트 요청 DTO"""
    gender: Optional[str] = None
    birth_year: Optional[int] = None
    language: Optional[str] = None
