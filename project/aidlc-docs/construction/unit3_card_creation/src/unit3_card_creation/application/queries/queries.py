from dataclasses import dataclass
from uuid import UUID
from typing import Optional


@dataclass
class GetCardQuery:
    card_id: UUID
    user_id: UUID


@dataclass
class GetCardsByUserQuery:
    user_id: UUID
    limit: int = 20
    cursor: Optional[str] = None
    favorites_only: bool = False
