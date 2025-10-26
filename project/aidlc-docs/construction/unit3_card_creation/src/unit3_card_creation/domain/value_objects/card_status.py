from dataclasses import dataclass
from enum import Enum


class CardStatusType(Enum):
    CREATING = "CREATING"
    METADATA_EXTRACTING = "METADATA_EXTRACTING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class CardStatus:
    value: CardStatusType
    
    def is_completed(self) -> bool:
        return self.value == CardStatusType.COMPLETED
    
    def is_failed(self) -> bool:
        return self.value == CardStatusType.FAILED
    
    def can_edit(self) -> bool:
        """편집 가능한 상태인지 확인"""
        return self.value in [CardStatusType.COMPLETED]
