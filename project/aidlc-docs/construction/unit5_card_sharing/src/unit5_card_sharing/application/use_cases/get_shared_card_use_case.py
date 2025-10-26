from ..dtos.commands import AccessShareLinkQuery
from ..dtos.response_dtos import SharedCardDto, CardDto
from ...domain.repositories.share_link_repository import ShareLinkRepository
from ...domain.value_objects.share_token import ShareToken

class GetSharedCardUseCase:
    def __init__(self, repository: ShareLinkRepository):
        self._repository = repository
    
    async def execute(self, query: AccessShareLinkQuery) -> SharedCardDto:
        # 공유 토큰으로 링크 조회
        token = ShareToken(query.share_token)
        aggregate = await self._repository.find_by_token(token)
        
        if not aggregate:
            raise ValueError("Share link not found")
        
        share_link = aggregate.share_link
        
        # 접근 기록
        if not share_link.is_expired():
            aggregate.access(query.user_agent, query.ip_address)
            await self._repository.save(aggregate)
        
        # TODO: Unit3에서 카드 정보 조회
        # 임시로 더미 데이터 반환
        card_dto = CardDto(
            title="Sample Video Title",
            thumbnail="https://example.com/thumbnail.jpg",
            youtube_url="https://youtube.com/watch?v=sample",
            summary="Sample summary",
            tags=["tag1", "tag2"]
        )
        
        return SharedCardDto(
            card=card_dto,
            is_expired=share_link.is_expired(),
            expires_at=share_link.expires_at.to_iso_string(),
            access_count=share_link.access_count
        )
