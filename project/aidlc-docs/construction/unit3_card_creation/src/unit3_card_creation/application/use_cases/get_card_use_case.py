from typing import Optional
from ..queries.queries import GetCardQuery
from ..dtos.card_dtos import CardDetailDto
from ...domain.repositories.card_repository import CardRepository


class GetCardUseCase:
    def __init__(self, card_repository: CardRepository):
        self._card_repository = card_repository
    
    async def execute(self, query: GetCardQuery) -> Optional[CardDetailDto]:
        card_aggregate = await self._card_repository.find_by_id(query.card_id)
        
        if not card_aggregate or card_aggregate.card.user_id != query.user_id:
            return None
        
        card = card_aggregate.card
        metadata = card.video_metadata
        
        return CardDetailDto(
            card_id=card.card_id,
            content_url=card.content_url.value if card.content_url else "",
            video_title=metadata.video_title.value if metadata.video_title else "",
            thumbnail_url=metadata.thumbnail.get_display_url() if metadata.thumbnail else "",
            memo=card.memo.content,
            tags=card.tags.items,
            is_favorite=card.is_favorite,
            is_public=card.is_public,
            status=card.status.value.value,
            created_at=card.created_at,
            updated_at=card.updated_at
        )
