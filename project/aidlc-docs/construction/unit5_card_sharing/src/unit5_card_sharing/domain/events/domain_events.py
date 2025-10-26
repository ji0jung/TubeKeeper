import uuid
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class ShareLinkCreated:
    share_token: str
    card_id: uuid.UUID
    user_id: uuid.UUID
    expires_at: datetime
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.utcnow()

@dataclass
class ShareLinkAccessed:
    share_token: str
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.utcnow()

@dataclass
class SharedCardSaved:
    share_token: str
    original_card_id: uuid.UUID
    new_card_id: uuid.UUID
    user_id: uuid.UUID
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.utcnow()
