from dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass(frozen=True)
class ExpirationDate:
    value: datetime
    
    def __post_init__(self):
        # timezone 정보 제거하여 naive datetime으로 저장 (Unit3 방식)
        if self.value.tzinfo is not None:
            object.__setattr__(self, 'value', self.value.replace(tzinfo=None))
    
    @classmethod
    def create_from_now(cls, days: int = 7) -> 'ExpirationDate':
        # naive datetime 사용
        expiry_time = datetime.utcnow() + timedelta(days=days)
        return cls(expiry_time.replace(tzinfo=None))
    
    def is_expired(self) -> bool:
        # naive datetime으로 비교
        return datetime.utcnow().replace(tzinfo=None) > self.value
    
    def to_iso_string(self) -> str:
        return self.value.isoformat() + 'Z'
