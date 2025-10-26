from typing import Optional
from uuid import UUID
from ...domain.services.domain_services import CardDuplicationChecker
from ...domain.value_objects.content_url import ContentUrl
from ...domain.entities.card import Card
from ...domain.repositories.card_repository import CardRepository


class CardDuplicationService(CardDuplicationChecker):
    def __init__(self, card_repository: CardRepository):
        self._card_repository = card_repository
    
    async def check_duplicate(self, user_id: UUID, content_url: ContentUrl) -> Optional[Card]:
        card_aggregate = await self._card_repository.find_by_content_url(user_id, content_url)
        return card_aggregate.card if card_aggregate else None
