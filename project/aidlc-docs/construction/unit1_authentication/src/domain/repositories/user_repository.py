from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from domain.entities.user import User
from domain.value_objects.email import Email


class UserRepository(ABC):
    """사용자 리포지토리 인터페이스"""
    
    @abstractmethod
    async def save(self, user: User) -> None:
        """사용자 저장"""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        """ID로 사용자 조회"""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: Email) -> Optional[User]:
        """이메일로 사용자 조회"""
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool:
        """이메일 존재 여부 확인"""
        pass
