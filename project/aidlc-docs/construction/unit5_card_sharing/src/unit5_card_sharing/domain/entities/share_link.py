import uuid
from datetime import datetime
from dataclasses import dataclass, field
from ..value_objects.share_token import ShareToken
from ..value_objects.expiration_date import ExpirationDate

@dataclass
class ShareLink:
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    share_token: ShareToken = field(default_factory=ShareToken.generate)
    card_id: uuid.UUID = field(default=None)
    user_id: uuid.UUID = field(default=None)
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: ExpirationDate = field(default_factory=ExpirationDate.create_from_now)
    access_count: int = field(default=0)
    is_active: bool = field(default=True)
    
    def __post_init__(self):
        if not self.card_id:
            raise ValueError("Card ID is required")
        if not self.user_id:
            raise ValueError("User ID is required")
    
    def is_expired(self) -> bool:
        return self.expires_at.is_expired()
    
    def increment_access_count(self) -> None:
        self.access_count += 1
    
    def deactivate(self) -> None:
        self.is_active = False
