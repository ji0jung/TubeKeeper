"""Command Objects for Unit4 Search"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime


@dataclass
class SearchMyCardsCommand:
    """내 카드 검색 명령"""
    user_id: UUID
    cursor: Optional[datetime] = None
    limit: int = 20
    category_id: Optional[UUID] = None
    keyword: Optional[str] = None
    tag: Optional[str] = None


@dataclass
class SearchPublicCardsCommand:
    """공개 카드 검색 명령"""
    user_id: UUID
    page: int = 1
    limit: int = 20
    keyword: Optional[str] = None
    tag: Optional[str] = None


@dataclass
class SavePublicCardCommand:
    """공개 카드 저장 명령"""
    card_id: UUID
    user_id: UUID
    category_id: Optional[UUID] = None


@dataclass
class GetSearchSuggestionsQuery:
    """검색 제안 조회 쿼리"""
    user_id: UUID
    query: str
    scope: str = "my"  # 'my' | 'public'


@dataclass
class GetTagsQuery:
    """태그 목록 조회 쿼리"""
    user_id: UUID
    scope: str = "my"  # 'my' | 'public'
