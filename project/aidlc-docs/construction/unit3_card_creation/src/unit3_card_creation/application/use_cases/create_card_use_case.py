from uuid import UUID
from ..commands.commands import CreateCardCommand
from ..dtos.card_dtos import CreateCardResult
from ...domain.aggregates.card_aggregate import CardAggregate
from ...domain.value_objects.content_url import ContentUrl
from ...domain.repositories.card_repository import CardRepository
from ...domain.services.domain_services import CardDuplicationChecker


class CreateCardUseCase:
    def __init__(
        self,
        card_repository: CardRepository,
        duplication_checker: CardDuplicationChecker
    ):
        self._card_repository = card_repository
        self._duplication_checker = duplication_checker
    
    async def execute(self, command: CreateCardCommand) -> CreateCardResult:
        try:
            content_url = ContentUrl(command.content_url)
            
            # 중복 검사
            existing_card = await self._duplication_checker.check_duplicate(
                command.user_id, content_url
            )
            if existing_card:
                return CreateCardResult(
                    card_id=existing_card.card_id,
                    status="DUPLICATE",
                    message="이미 동일한 URL의 카드가 존재합니다"
                )
            
            # 카드 생성
            card_aggregate = CardAggregate.create(
                user_id=command.user_id,
                category_id=command.category_id,
                content_url=content_url,
                memo=command.memo,
                tags=command.tags
            )
            
            await self._card_repository.save(card_aggregate)
            
            return CreateCardResult(
                card_id=card_aggregate.card.card_id,
                status="CREATED",
                message="카드가 생성되었습니다"
            )
            
        except ValueError as e:
            return CreateCardResult(
                card_id=UUID('00000000-0000-0000-0000-000000000000'),
                status="ERROR",
                message=str(e)
            )
