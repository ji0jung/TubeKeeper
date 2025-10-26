"""SavePublicCardUseCase"""

from ..dto.commands import SavePublicCardCommand
from ...domain.services.public_card_saving_service import PublicCardSavingService
from ...domain.events.domain_events import PublicCardSaved
from datetime import datetime


class SavePublicCardUseCase:
    """공개 카드 저장 유스케이스"""
    
    def __init__(self, saving_service: PublicCardSavingService, event_publisher):
        self._saving_service = saving_service
        self._event_publisher = event_publisher
    
    async def execute(self, command: SavePublicCardCommand):
        """공개 카드를 내 계정에 독립적으로 복사 저장"""
        
        # 공개 카드 저장 실행
        result = await self._saving_service.save_public_card_as_copy(
            card_id=command.card_id,
            user_id=command.user_id,
            category_id=command.category_id
        )
        
        # 성공 시 도메인 이벤트 발행
        if result.success and result.new_card:
            event = PublicCardSaved(
                original_card_id=command.card_id,
                new_card_id=result.new_card.card_id,
                user_id=command.user_id,
                category_id=command.category_id or await self._get_default_category_id(command.user_id),
                saved_at=datetime.utcnow()
            )
            await self._event_publisher.publish(event)
        
        return result
    
    async def _get_default_category_id(self, user_id):
        """기본 카테고리 ID 조회"""
        # 실제 구현에서는 카테고리 서비스에서 조회
        return None
