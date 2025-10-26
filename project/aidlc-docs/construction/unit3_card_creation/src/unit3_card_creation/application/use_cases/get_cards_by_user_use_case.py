from ..queries.queries import GetCardsByUserQuery
from ..dtos.card_dtos import CardListResult, CardSummaryDto
from ...domain.repositories.card_repository import CardRepository


class GetCardsByUserUseCase:
    def __init__(self, card_repository: CardRepository):
        self._card_repository = card_repository
    
    async def execute(self, query: GetCardsByUserQuery) -> CardListResult:
        # limit + 1로 조회하여 다음 페이지 존재 여부 확인
        card_aggregates = await self._card_repository.find_by_user_id(
            user_id=query.user_id,
            limit=query.limit + 1,
            cursor=query.cursor
        )
        
        has_more = len(card_aggregates) > query.limit
        if has_more:
            card_aggregates = card_aggregates[:-1]  # 마지막 항목 제거
        
        cards = []
        for aggregate in card_aggregates:
            card = aggregate.card
            metadata = card.video_metadata
            
            # 즐겨찾기 필터링
            if query.favorites_only and not card.is_favorite:
                continue
            
            cards.append(CardSummaryDto(
                card_id=card.card_id,
                content_url=card.content_url.value if card.content_url else "",
                video_title=metadata.video_title.value if metadata.video_title else "",
                thumbnail_url=metadata.thumbnail.get_display_url() if metadata.thumbnail else "",
                is_favorite=card.is_favorite,
                tags=card.tags.items if card.tags else [],
                created_at=card.created_at
            ))
        
        # 다음 커서 생성
        next_cursor = None
        if has_more and cards:
            next_cursor = cards[-1].created_at.isoformat()
        
        return CardListResult(
            cards=cards,
            next_cursor=next_cursor,
            has_more=has_more
        )
