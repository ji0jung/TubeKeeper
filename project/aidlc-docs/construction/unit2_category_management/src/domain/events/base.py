from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

@dataclass
class DomainEvent(ABC):
    event_id: UUID
    occurred_at: datetime
    user_id: UUID
    
    def __init__(self, user_id: UUID):
        self.event_id = uuid4()
        self.occurred_at = datetime.utcnow()
        self.user_id = user_id
