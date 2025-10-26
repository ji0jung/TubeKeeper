from typing import Dict
from uuid import UUID

from ...domain.services.card_count_service import CardCountService

class MockCardCountService(CardCountService):
    """Unit2 독립 테스트용 Mock 서비스"""
    
    def __init__(self):
        self._mock_counts = {}
    
    async def get_card_count(self, category_id: UUID) -> int:
        return self._mock_counts.get(category_id, 0)
    
    async def get_card_count_by_category(self, category_id: UUID) -> int:
        """개별 카테고리 조회용 메서드"""
        return self._mock_counts.get(category_id, 0)
    
    async def get_card_counts(self, category_ids: list[UUID]) -> Dict[UUID, int]:
        return {cat_id: self._mock_counts.get(cat_id, 0) for cat_id in category_ids}
    
    def set_mock_count(self, category_id: UUID, count: int):
        """테스트용 카드 수 설정"""
        self._mock_counts[category_id] = count
