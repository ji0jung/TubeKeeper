from abc import ABC, abstractmethod
from ..events.base import DomainEvent

class EventPublisher(ABC):
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        pass
