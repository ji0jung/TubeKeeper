from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from ..aggregates.card_aggregate import CardAggregate
from ..value_objects.content_url import ContentUrl


class CardRepository(ABC):
    @abstractmethod
    async def save(self, card_aggregate: CardAggregate) -> None:
        pass
    
    @abstractmethod
    async def find_by_id(self, card_id: UUID) -> Optional[CardAggregate]:
        pass
    
    @abstractmethod
    async def find_by_content_url(self, user_id: UUID, content_url: ContentUrl) -> Optional[CardAggregate]:
        pass
    
    @abstractmethod
    async def find_by_user_id(self, user_id: UUID, limit: int = 20, cursor: Optional[str] = None) -> List[CardAggregate]:
        pass
    
    @abstractmethod
    async def delete(self, card_id: UUID) -> None:
        pass
    
    @abstractmethod
    async def exists_by_content_url(self, user_id: UUID, content_url: ContentUrl) -> bool:
        pass
