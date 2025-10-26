import uuid
from abc import ABC, abstractmethod
from typing import Optional
from ..entities.share_link_aggregate import ShareLinkAggregate
from ..value_objects.share_token import ShareToken

class ShareLinkRepository(ABC):
    @abstractmethod
    async def save(self, aggregate: ShareLinkAggregate) -> None:
        pass
    
    @abstractmethod
    async def find_by_token(self, token: ShareToken) -> Optional[ShareLinkAggregate]:
        pass
    
    @abstractmethod
    async def find_by_card_id(self, card_id: uuid.UUID) -> list[ShareLinkAggregate]:
        pass
    
    @abstractmethod
    async def delete_expired_links(self) -> int:
        pass
