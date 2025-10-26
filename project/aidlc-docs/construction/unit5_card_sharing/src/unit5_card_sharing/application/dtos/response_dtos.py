import uuid
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class CreateShareLinkDto:
    share_url: str
    share_token: str
    expires_at: str

@dataclass
class CardDto:
    title: str
    thumbnail: str
    youtube_url: str
    summary: Optional[str] = None
    tags: Optional[List[str]] = None

@dataclass
class SharedCardDto:
    card: CardDto
    is_expired: bool
    expires_at: str
    access_count: Optional[int] = None

@dataclass
class SavedCardDto:
    id: str
    title: str
    category_id: str
    category_name: str

@dataclass
class SaveSharedCardDto:
    new_card: Optional[SavedCardDto] = None
    already_exists: Optional[bool] = None
