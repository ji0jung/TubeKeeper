from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import List, Optional


@dataclass
class CardSummaryDto:
    card_id: UUID
    content_url: str
    video_title: str
    thumbnail_url: str
    is_favorite: bool
    tags: List[str]
    created_at: datetime


@dataclass
class CardDetailDto:
    card_id: UUID
    content_url: str
    video_title: str
    thumbnail_url: str
    memo: str
    tags: List[str]
    is_favorite: bool
    is_public: bool
    status: str
    created_at: datetime
    updated_at: datetime


@dataclass
class CreateCardResult:
    card_id: UUID
    status: str
    message: str = ""


@dataclass
class CardListResult:
    cards: List[CardSummaryDto]
    next_cursor: Optional[str]
    has_more: bool
