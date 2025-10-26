import uuid
from dataclasses import dataclass
from typing import Optional

@dataclass
class CreateShareLinkCommand:
    card_id: uuid.UUID
    user_id: uuid.UUID

@dataclass
class AccessShareLinkQuery:
    share_token: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None

@dataclass
class SaveSharedCardCommand:
    share_token: str
    user_id: uuid.UUID
    category_id: Optional[uuid.UUID] = None
