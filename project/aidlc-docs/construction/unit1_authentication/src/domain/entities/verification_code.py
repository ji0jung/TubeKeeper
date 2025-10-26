from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from common.utils import generate_uuid, utc_now, add_minutes
from domain.value_objects.email import Email
from domain.value_objects.verification_code_value import VerificationCodeValue
from domain.value_objects.code_purpose import CodePurpose


@dataclass
class VerificationCode:
    """인증 코드 엔티티"""
    code_id: UUID
    email: Email
    code: VerificationCodeValue
    purpose: CodePurpose
    created_at: datetime
    expires_at: datetime
    is_used: bool = False
    used_at: Optional[datetime] = None
    
    @classmethod
    def create(cls, email: Email, purpose: CodePurpose, expire_minutes: int = 15) -> 'VerificationCode':
        """새 인증 코드 생성"""
        now = utc_now()
        return cls(
            code_id=generate_uuid(),
            email=email,
            code=VerificationCodeValue.generate(),
            purpose=purpose,
            created_at=now,
            expires_at=add_minutes(now, expire_minutes),
            is_used=False
        )
    
    def verify(self, input_code: str) -> bool:
        """인증 코드 검증"""
        if self.is_used or self.is_expired():
            return False
        return self.code.value == input_code
    
    def mark_as_used(self) -> None:
        """사용됨으로 표시"""
        self.is_used = True
        self.used_at = utc_now()
    
    def is_expired(self) -> bool:
        """만료 여부 확인"""
        return utc_now() > self.expires_at
