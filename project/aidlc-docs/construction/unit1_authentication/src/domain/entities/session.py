from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from common.utils import generate_uuid, utc_now, add_days
from domain.value_objects.device_info import DeviceInfo


@dataclass
class Session:
    """세션 엔티티"""
    session_id: UUID
    user_id: UUID
    device_info: DeviceInfo
    created_at: datetime
    expires_at: datetime
    last_accessed_at: datetime
    is_active: bool = True
    
    @classmethod
    def create(cls, user_id: UUID, device_info: DeviceInfo, expire_days: int = 7) -> 'Session':
        """새 세션 생성"""
        now = utc_now()
        return cls(
            session_id=generate_uuid(),
            user_id=user_id,
            device_info=device_info,
            created_at=now,
            expires_at=add_days(now, expire_days),
            last_accessed_at=now,
            is_active=True
        )
    
    def extend(self, expire_days: int = 7) -> None:
        """세션 연장"""
        now = utc_now()
        self.expires_at = add_days(now, expire_days)
        self.last_accessed_at = now
    
    def expire(self) -> None:
        """세션 만료"""
        self.is_active = False
    
    def is_expired(self) -> bool:
        """세션 만료 여부 확인"""
        return not self.is_active or utc_now() > self.expires_at
    
    def is_same_device(self, device_info: DeviceInfo) -> bool:
        """동일 디바이스 여부 확인"""
        return self.device_info.is_same_device(device_info)
