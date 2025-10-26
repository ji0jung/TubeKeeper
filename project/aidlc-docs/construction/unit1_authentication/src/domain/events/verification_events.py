from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from domain.events.base_event import EventMixin
from domain.value_objects.email import Email
from domain.value_objects.code_purpose import CodePurpose


@dataclass
class VerificationCodeGenerated(EventMixin):
    """인증 코드 생성 이벤트"""
    code_id: UUID
    email: Email
    purpose: CodePurpose
    expires_at: datetime


@dataclass
class VerificationCodeUsed(EventMixin):
    """인증 코드 사용 이벤트"""
    code_id: UUID
    email: Email
    purpose: CodePurpose
    used_at: Optional[datetime]
