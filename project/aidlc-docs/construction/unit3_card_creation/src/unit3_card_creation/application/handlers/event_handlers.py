from ...domain.events.domain_events import CardCreated
from ...domain.services.domain_services import ContentMetadataExtractor
from ...domain.repositories.card_repository import CardRepository
from ...domain.value_objects.content_url import ContentUrl


class MetadataCollectionHandler:
    def __init__(
        self,
        card_repository: CardRepository,
        metadata_extractor: ContentMetadataExtractor
    ):
        self._card_repository = card_repository
        self._metadata_extractor = metadata_extractor
    
    async def handle(self, event: CardCreated) -> None:
        try:
            content_url = ContentUrl(event.content_url)
            metadata = await self._metadata_extractor.extract_metadata(content_url)
            
            card_aggregate = await self._card_repository.find_by_id(event.card_id)
            if card_aggregate:
                # 메타데이터 업데이트 후 바로 완료 상태로 변경
                card_aggregate.card.update_metadata(metadata)
                await self._card_repository.save(card_aggregate)
                
        except Exception as e:
            # 로깅 및 실패 처리
            print(f"Metadata collection failed: {e}")
            
            card_aggregate = await self._card_repository.find_by_id(event.card_id)
            if card_aggregate:
                card_aggregate.card.status = CardStatus(CardStatusType.FAILED)
                await self._card_repository.save(card_aggregate)
