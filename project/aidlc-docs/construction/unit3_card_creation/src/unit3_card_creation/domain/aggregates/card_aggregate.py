from dataclasses import dataclass, field
from typing import List
from uuid import UUID
from ..entities.card import Card
from ..value_objects.content_url import ContentUrl
from ..events.domain_events import DomainEvent, CardCreated, MetadataCollected


@dataclass
class CardAggregate:
    card: Card
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False)
    
    @classmethod
    def create(
        cls,
        user_id: UUID,
        category_id: UUID,
        content_url: ContentUrl,
        memo: str = "",
        tags: list[str] = None
    ) -> 'CardAggregate':
        card = Card.create(user_id, category_id, content_url, memo, tags or [])
        aggregate = cls(card)
        aggregate._add_event(CardCreated(
            card_id=card.card_id,
            user_id=card.user_id,
            category_id=card.category_id,
            content_url=content_url.value
        ))
        return aggregate
    
    def update_metadata(self, metadata) -> None:
        self.card.update_metadata(metadata)
        self._add_event(MetadataCollected(
            card_id=self.card.card_id,
            video_title=metadata.video_title.value if metadata.video_title else ""
        ))
    
    def toggle_favorite(self) -> None:
        self.card.toggle_favorite()
    
    def get_domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        self._domain_events.clear()
    
    def _add_event(self, event: DomainEvent) -> None:
        self._domain_events.append(event)
