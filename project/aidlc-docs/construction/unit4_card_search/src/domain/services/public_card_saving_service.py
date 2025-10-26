"""PublicCardSavingService"""

from uuid import UUID
from dataclasses import dataclass
from typing import Optional

from ..entities.card_summary import CardSummary


@dataclass
class SaveResult:
    success: bool
    new_card: Optional[CardSummary] = None
    already_exists: bool = False
    error_message: str = ""


class PublicCardNotFoundError(Exception):
    pass


class DuplicateCardError(Exception):
    pass


class PublicCardSavingService:
    """공개 카드를 내 계정에 완전 독립적으로 복사 저장하는 서비스"""
    
    def __init__(self, card_search_repository, card_repository, category_repository):
        self._card_search_repository = card_search_repository
        self._card_repository = card_repository
        self._category_repository = category_repository
    
    async def save_public_card_as_copy(self, card_id: UUID, user_id: UUID, 
                                     category_id: Optional[UUID] = None) -> SaveResult:
        """공개 카드를 독립적인 새 카드로 복사 저장"""
        
        # 1. 중복 확인
        if await self._check_duplicate(card_id, user_id):
            return SaveResult(success=False, already_exists=True)
        
        # 2. 원본 카드 조회
        original_card = await self._card_search_repository.get_public_card(card_id)
        if not original_card:
            raise PublicCardNotFoundError(f"Public card not found: {card_id}")
        
        # 3. 저장 권한 확인
        validation_result = await self._validate_save_permission(card_id, user_id)
        if not validation_result.is_valid:
            return SaveResult(success=False, error_message=validation_result.error_message)
        
        # 4. 카테고리 결정
        target_category_id = category_id or await self._get_default_category(user_id)
        
        # 5. 독립적인 새 카드 생성
        new_card = await self._create_independent_copy(original_card, user_id, target_category_id)
        
        # 6. 새 카드 저장
        saved_card = await self._card_repository.save(new_card)
        
        return SaveResult(
            success=True,
            new_card=CardSummary.from_card(saved_card),
            already_exists=False
        )
    
    async def _create_independent_copy(self, original_card, user_id: UUID, category_id: UUID):
        """원본 카드에서 완전히 독립적인 새 카드 생성"""
        # Unit3의 Card.create 메서드 활용
        # 원본과 연결 관계 없이 완전히 새로운 카드로 생성
        return await self._card_repository.create_card(
            user_id=user_id,
            category_id=category_id,
            title=original_card.title,
            content_url=original_card.content_url,
            thumbnail=original_card.thumbnail,
            summary=original_card.summary,
            tags=original_card.tags.copy() if original_card.tags else [],
            memo="",  # 메모는 빈 문자열로 시작
            is_public=False  # 저장된 카드는 기본적으로 비공개
        )
    
    async def _check_duplicate(self, card_id: UUID, user_id: UUID) -> bool:
        """중복 저장 확인 (동일한 content_url 기준)"""
        original_card = await self._card_search_repository.get_public_card(card_id)
        if not original_card:
            return False
        
        return await self._card_repository.exists_by_url_and_user(
            content_url=original_card.content_url,
            user_id=user_id
        )
    
    async def _get_default_category(self, user_id: UUID) -> UUID:
        """기본 "공유받은 카드" 카테고리 조회/생성"""
        shared_category = await self._category_repository.get_or_create_shared_category(user_id)
        return shared_category.id
    
    async def _validate_save_permission(self, card_id: UUID, user_id: UUID) -> 'ValidationResult':
        """저장 권한 검증"""
        # 공개 카드이고 본인 카드가 아닌지 확인
        original_card = await self._card_search_repository.get_public_card(card_id)
        
        if not original_card.is_public:
            return ValidationResult(False, "비공개 카드는 저장할 수 없습니다")
        
        if original_card.user_id == user_id:
            return ValidationResult(False, "본인 카드는 저장할 수 없습니다")
        
        return ValidationResult(True)


class ValidationResult:
    def __init__(self, is_valid: bool, error_message: str = ""):
        self.is_valid = is_valid
        self.error_message = error_message
