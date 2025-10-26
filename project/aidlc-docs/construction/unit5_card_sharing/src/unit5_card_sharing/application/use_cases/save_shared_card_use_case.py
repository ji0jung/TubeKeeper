import uuid
from ..dtos.commands import SaveSharedCardCommand
from ..dtos.response_dtos import SaveSharedCardDto, SavedCardDto
from ...domain.repositories.share_link_repository import ShareLinkRepository
from ...domain.value_objects.share_token import ShareToken

class SaveSharedCardUseCase:
    def __init__(self, repository: ShareLinkRepository):
        self._repository = repository
    
    async def execute(self, command: SaveSharedCardCommand) -> SaveSharedCardDto:
        # 공유 토큰으로 링크 조회
        token = ShareToken(command.share_token)
        aggregate = await self._repository.find_by_token(token)
        
        if not aggregate:
            raise ValueError("Share link not found")
        
        share_link = aggregate.share_link
        
        if share_link.is_expired():
            raise ValueError("Share link expired")
        
        # TODO: Unit3 API 호출로 중복 검사 및 카드 생성
        # 임시로 더미 응답 반환
        new_card = SavedCardDto(
            id=str(uuid.uuid4()),
            title="Sample Card Title",
            category_id=str(command.category_id or uuid.uuid4()),
            category_name="공유받은 카드"
        )
        
        return SaveSharedCardDto(new_card=new_card)
