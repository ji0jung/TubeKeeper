"""Response DTO Classes"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

from ...domain.entities.card_summary import CardSummary
from ...domain.entities.search_result import SearchResult
from ...domain.services.search_suggestion_service import SearchSuggestion, TagSuggestion


@dataclass
class CardSummaryDto:
    """카드 요약 DTO"""
    id: str
    title: str
    thumbnail: str
    summary: str
    tags: List[str]
    category_name: Optional[str] = None
    owner_name: Optional[str] = None
    is_favorite: bool = False
    is_public: bool = False
    created_at: str
    
    @classmethod
    def from_domain(cls, card: CardSummary) -> 'CardSummaryDto':
        return cls(
            id=str(card.card_id),
            title=card.title,
            thumbnail=card.thumbnail,
            summary=card.summary,
            tags=card.tags,
            category_name=card.category_name,
            owner_name=card.owner_name,
            is_favorite=card.is_favorite,
            is_public=card.is_public,
            created_at=card.created_at.isoformat() if card.created_at else ""
        )


@dataclass
class SearchMyCardsDto:
    """내 카드 검색 결과 DTO"""
    cards: List[CardSummaryDto]
    next_cursor: Optional[str] = None
    has_more: bool = False
    
    @classmethod
    def from_domain(cls, result: SearchResult) -> 'SearchMyCardsDto':
        return cls(
            cards=[CardSummaryDto.from_domain(card) for card in result.card_summaries],
            next_cursor=result.metadata.next_cursor.isoformat() if result.metadata.next_cursor else None,
            has_more=result.metadata.has_more
        )


@dataclass
class SearchPublicCardsDto:
    """공개 카드 검색 결과 DTO"""
    cards: List[CardSummaryDto]
    total_count: int
    current_page: int
    total_pages: int
    
    @classmethod
    def from_domain(cls, result: SearchResult, current_page: int, limit: int) -> 'SearchPublicCardsDto':
        total_pages = (result.metadata.total_count + limit - 1) // limit if result.metadata.total_count else 0
        
        return cls(
            cards=[CardSummaryDto.from_domain(card) for card in result.card_summaries],
            total_count=result.metadata.total_count or 0,
            current_page=current_page,
            total_pages=total_pages
        )


@dataclass
class SavePublicCardDto:
    """공개 카드 저장 결과 DTO"""
    new_card: Optional[CardSummaryDto] = None
    already_exists: bool = False


@dataclass
class SearchSuggestionDto:
    """검색 제안 DTO"""
    type: str
    value: str
    count: int = 0
    
    @classmethod
    def from_domain(cls, suggestion: SearchSuggestion) -> 'SearchSuggestionDto':
        return cls(
            type=suggestion.type,
            value=suggestion.value,
            count=suggestion.count
        )


@dataclass
class TagDto:
    """태그 DTO"""
    name: str
    count: int
    
    @classmethod
    def from_domain(cls, tag: TagSuggestion) -> 'TagDto':
        return cls(
            name=tag.name,
            count=tag.count
        )
