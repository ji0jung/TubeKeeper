from typing import Optional, Dict
from uuid import UUID

from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from domain.value_objects.email import Email


class MemoryUserRepository(UserRepository):
    """메모리 기반 사용자 리포지토리 (테스트용)"""
    
    def __init__(self):
        self._users: Dict[UUID, User] = {}
        self._email_index: Dict[str, UUID] = {}
    
    async def save(self, user: User) -> None:
        """사용자 저장"""
        self._users[user.user_id] = user
        self._email_index[user.email.value] = user.user_id
    
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        """ID로 사용자 조회"""
        return self._users.get(user_id)
    
    async def find_by_email(self, email: Email) -> Optional[User]:
        """이메일로 사용자 조회"""
        user_id = self._email_index.get(email.value)
        if user_id:
            return self._users.get(user_id)
        return None
    
    async def exists_by_email(self, email: Email) -> bool:
        """이메일 존재 여부 확인"""
        return email.value in self._email_index
