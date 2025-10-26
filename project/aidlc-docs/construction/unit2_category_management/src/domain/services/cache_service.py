from abc import ABC, abstractmethod
from typing import Optional, Any
from uuid import UUID

class CacheService(ABC):
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = None) -> None:
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        pass
    
    @abstractmethod
    async def invalidate_user_categories(self, user_id: UUID) -> None:
        pass
