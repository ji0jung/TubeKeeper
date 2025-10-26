from dataclasses import dataclass, field
from uuid import UUID
from typing import List, Optional


@dataclass
class CreateCardCommand:
    user_id: UUID
    category_id: UUID
    content_url: str
    memo: Optional[str] = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class UpdateCardCommand:
    card_id: UUID
    user_id: UUID
    memo: str = ""
    tags: List[str] = None


@dataclass
class ToggleFavoriteCommand:
    card_id: UUID
    user_id: UUID


@dataclass
class DeleteCardCommand:
    card_id: UUID
    user_id: UUID
