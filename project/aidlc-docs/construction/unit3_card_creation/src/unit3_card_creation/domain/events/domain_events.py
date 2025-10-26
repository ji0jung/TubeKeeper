from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from abc import ABC


class DomainEvent(ABC):
    def __init__(self):
        self.occurred_at = datetime.utcnow()


@dataclass
class CardCreated(DomainEvent):
    card_id: UUID
    user_id: UUID
    category_id: UUID
    content_url: str
    
    def __post_init__(self):
        super().__init__()


@dataclass
class MetadataCollected(DomainEvent):
    card_id: UUID
    video_title: str
    
    def __post_init__(self):
        super().__init__()


@dataclass
class SummaryGenerated(DomainEvent):
    card_id: UUID
    summary_content: str
    
    def __post_init__(self):
        super().__init__()


@dataclass
class SummaryGenerationFailed(DomainEvent):
    card_id: UUID
    retry_count: int
    error_message: str
    
    def __post_init__(self):
        super().__init__()
