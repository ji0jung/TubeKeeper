"""SearchScope Value Object"""

from enum import Enum
from dataclasses import dataclass


class SearchScopeType(Enum):
    """검색 범위 타입"""
    MY_CARDS = "MY_CARDS"
    PUBLIC_CARDS = "PUBLIC_CARDS"


class PaginationType(Enum):
    """페이징 타입"""
    CURSOR = "CURSOR"
    OFFSET = "OFFSET"


@dataclass(frozen=True)
class SearchScope:
    """검색 범위를 나타내는 값 객체"""
    
    type: SearchScopeType
    
    def is_my_cards(self) -> bool:
        """내 카드 검색 여부"""
        return self.type == SearchScopeType.MY_CARDS
    
    def is_public_cards(self) -> bool:
        """공개 카드 검색 여부"""
        return self.type == SearchScopeType.PUBLIC_CARDS
    
    def allows_category_filter(self) -> bool:
        """카테고리 필터링 허용 여부"""
        return self.is_my_cards()
    
    def get_pagination_type(self) -> PaginationType:
        """페이징 타입 반환"""
        return PaginationType.CURSOR if self.is_my_cards() else PaginationType.OFFSET
    
    @classmethod
    def my_cards(cls) -> 'SearchScope':
        """내 카드 검색 범위 생성"""
        return cls(SearchScopeType.MY_CARDS)
    
    @classmethod
    def public_cards(cls) -> 'SearchScope':
        """공개 카드 검색 범위 생성"""
        return cls(SearchScopeType.PUBLIC_CARDS)
