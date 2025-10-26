from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.category import Category

class CategoryRepository(ABC):
    
    @abstractmethod
    async def save(self, category: Category) -> Category:
        pass
    
    @abstractmethod
    async def find_by_id(self, category_id: UUID) -> Optional[Category]:
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: UUID) -> List[Category]:
        pass
    
    @abstractmethod
    async def delete(self, category_id: UUID) -> None:
        pass
    
    @abstractmethod
    async def exists_by_name_and_parent(self, user_id: UUID, name: str, parent_id: Optional[UUID]) -> bool:
        pass
