import uuid
from dataclasses import dataclass

@dataclass(frozen=True)
class ShareToken:
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Share token cannot be empty")
        try:
            uuid.UUID(self.value)
        except ValueError:
            raise ValueError("Invalid share token format")
    
    @classmethod
    def generate(cls) -> 'ShareToken':
        return cls(str(uuid.uuid4()))
    
    def __str__(self) -> str:
        return self.value
