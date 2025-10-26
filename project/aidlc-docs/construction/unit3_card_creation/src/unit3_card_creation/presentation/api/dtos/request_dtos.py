from pydantic import BaseModel, HttpUrl
from typing import List, Optional
from uuid import UUID


class CreateCardRequest(BaseModel):
    content_url: str
    category_id: UUID
    memo: Optional[str] = ""
    tags: Optional[List[str]] = []


class UpdateCardRequest(BaseModel):
    memo: Optional[str] = ""
    tags: Optional[List[str]] = []


class GetCardsRequest(BaseModel):
    limit: Optional[int] = 20
    cursor: Optional[str] = None
    favorites_only: Optional[bool] = False
