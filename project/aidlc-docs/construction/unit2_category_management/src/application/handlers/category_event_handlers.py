import logging
from ...domain.events.category_events import CategoryCreated, CategoryDeleted, CategoryRenamed

logger = logging.getLogger(__name__)

class CategoryEventHandlers:
    
    async def handle_category_created(self, event: CategoryCreated):
        logger.info(f"카테고리 생성됨: {event.category_name} (ID: {event.category_id})")
    
    async def handle_category_deleted(self, event: CategoryDeleted):
        logger.info(f"카테고리 삭제됨: {event.category_name} (ID: {event.category_id})")
        
        # Unit3에 카드 이동 이벤트 발행 (추후 Unit3 통합 시 구현)
        if event.card_count > 0:
            logger.info(f"카드 이동 필요: {event.card_count}개")
    
    async def handle_category_renamed(self, event: CategoryRenamed):
        logger.info(f"카테고리 이름 변경: {event.old_name} -> {event.new_name}")
