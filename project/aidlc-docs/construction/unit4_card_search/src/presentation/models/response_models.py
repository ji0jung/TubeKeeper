"""Standard Response Models for Unit4"""

from typing import Any, Optional, Dict, List
from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """오류 상세 정보"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class StandardResponse(BaseModel):
    """표준 응답 형식"""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[ErrorDetail] = None
    
    @classmethod
    def success_response(cls, data: Any = None, message: str = "Success") -> "StandardResponse":
        """성공 응답 생성"""
        return cls(success=True, data=data, message=message)
    
    @classmethod
    def error_response(cls, code: str, message: str, details: Optional[Dict] = None) -> "StandardResponse":
        """오류 응답 생성"""
        return cls(
            success=False,
            error=ErrorDetail(code=code, message=message, details=details)
        )


class CardSummaryResponse(BaseModel):
    """카드 요약 응답"""
    id: str
    title: str
    thumbnail: str
    summary: str
    tags: List[str]
    categoryName: Optional[str] = None
    ownerName: Optional[str] = None
    isFavorite: bool = False
    isPublic: bool = False
    createdAt: str
    
    @classmethod
    def from_domain_summary(cls, card_summary) -> "CardSummaryResponse":
        """CardSummary 도메인 객체에서 변환"""
        return cls(
            id=str(card_summary.card_id),
            title=card_summary.title,
            thumbnail=card_summary.thumbnail,
            summary=card_summary.summary,
            tags=card_summary.tags,
            categoryName=card_summary.category_name,
            ownerName=card_summary.owner_name,
            isFavorite=card_summary.is_favorite,
            isPublic=card_summary.is_public,
            createdAt=card_summary.created_at.isoformat() if card_summary.created_at else ""
        )


class MyCardsResponse(BaseModel):
    """내 카드 검색 응답 (커서 기반)"""
    cards: List[CardSummaryResponse]
    nextCursor: Optional[str] = None
    hasMore: bool = False


class PublicCardsResponse(BaseModel):
    """공개 카드 검색 응답 (오프셋 기반)"""
    cards: List[CardSummaryResponse]
    totalCount: int
    currentPage: int
    totalPages: int


class SavePublicCardResponse(BaseModel):
    """공개 카드 저장 응답"""
    newCard: Optional[CardSummaryResponse] = None
    alreadyExists: bool = False


class SearchSuggestion(BaseModel):
    """검색 제안"""
    type: str  # 'recent', 'tag', 'popular'
    value: str


class SearchSuggestionsResponse(BaseModel):
    """검색 제안 응답"""
    suggestions: List[SearchSuggestion]


class TagInfo(BaseModel):
    """태그 정보"""
    name: str
    count: int


class TagsResponse(BaseModel):
    """태그 목록 응답"""
    tags: List[TagInfo]
