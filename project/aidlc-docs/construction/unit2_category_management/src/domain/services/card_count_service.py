from abc import ABC, abstractmethod
from typing import Dict
from uuid import UUID

class CardCountService(ABC):
    
    @abstractmethod
    async def get_card_count(self, category_id: UUID) -> int:
        pass
    
    @abstractmethod
    async def get_card_counts(self, category_ids: list[UUID]) -> Dict[UUID, int]:
        pass
