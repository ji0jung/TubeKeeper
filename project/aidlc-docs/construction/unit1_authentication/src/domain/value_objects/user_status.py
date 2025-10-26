from enum import Enum


class UserStatus(Enum):
    """사용자 상태 값 객체"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DEACTIVATED = "DEACTIVATED"
    
    def __str__(self) -> str:
        return self.value
