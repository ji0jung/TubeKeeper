from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from common.utils import generate_uuid, utc_now
from domain.value_objects.email import Email
from domain.value_objects.user_status import UserStatus


@dataclass
class User:
    """사용자 엔티티"""
    user_id: UUID
    email: Email
    status: UserStatus
    created_at: datetime
    last_active_at: datetime
    deactivated_at: Optional[datetime] = None
    
    @classmethod
    def create(cls, email: Email) -> 'User':
        """새 사용자 생성"""
        now = utc_now()
        return cls(
            user_id=generate_uuid(),
            email=email,
            status=UserStatus.ACTIVE,
            created_at=now,
            last_active_at=now
        )
    
    def activate(self) -> None:
        """사용자 활성화"""
        self.status = UserStatus.ACTIVE
        self.deactivated_at = None
    
    def deactivate(self) -> None:
        """사용자 비활성화"""
        self.status = UserStatus.DEACTIVATED
        self.deactivated_at = utc_now()
    
    def update_last_activity(self) -> None:
        """마지막 활동 시간 업데이트"""
        self.last_active_at = utc_now()
    
    def can_login(self) -> bool:
        """로그인 가능 여부 확인"""
        return self.status == UserStatus.ACTIVE
