from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.verification_code import VerificationCode
from domain.value_objects.email import Email
from domain.value_objects.code_purpose import CodePurpose


class VerificationCodeRepository(ABC):
    """인증 코드 리포지토리 인터페이스"""
    
    @abstractmethod
    async def save(self, verification_code: VerificationCode) -> None:
        """인증 코드 저장"""
        pass
    
    @abstractmethod
    async def find_latest_by_email_and_purpose(
        self, email: Email, purpose: CodePurpose
    ) -> Optional[VerificationCode]:
        """이메일과 목적으로 최신 인증 코드 조회"""
        pass
