from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from uuid import UUID


class CardSummaryResponse(BaseModel):
    card_id: UUID
    content_url: str
    video_title: str
    thumbnail_url: str
    is_favorite: bool
    created_at: datetime


class CardDetailResponse(BaseModel):
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


class CreateCardResponse(BaseModel):
    success: bool
    data: dict
    message: str


class CardListResponse(BaseModel):
    cards: List[CardSummaryResponse]
    next_cursor: Optional[str]
    has_more: bool


class ToggleFavoriteResponse(BaseModel):
    success: bool
    data: dict
    message: str
