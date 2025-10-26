import uuid
from ..dtos.commands import CreateShareLinkCommand
from ..dtos.response_dtos import CreateShareLinkDto
from ...domain.entities.share_link_aggregate import ShareLinkAggregate
from ...domain.repositories.share_link_repository import ShareLinkRepository
from ...domain.value_objects.share_url import ShareUrl
from ...settings import settings

class CreateShareLinkUseCase:
    def __init__(self, repository: ShareLinkRepository):
        self._repository = repository
    
    async def execute(self, command: CreateShareLinkCommand) -> CreateShareLinkDto:
        # 공유 링크 애그리게이트 생성
        aggregate = ShareLinkAggregate.create(
            card_id=command.card_id,
            user_id=command.user_id
        )
        
        # 저장
        await self._repository.save(aggregate)
        
        # 공유 URL 생성
        share_url = ShareUrl(
            base_url=settings.share_link_base_url,
            token=aggregate.share_link.share_token
        )
        
        return CreateShareLinkDto(
            share_url=str(share_url),
            share_token=aggregate.share_link.share_token.value,
            expires_at=aggregate.share_link.expires_at.to_iso_string()
        )
