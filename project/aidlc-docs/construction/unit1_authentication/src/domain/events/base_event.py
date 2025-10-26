from datetime import datetime
from uuid import UUID
from common.utils import generate_uuid, utc_now


class EventMixin:
    """이벤트 믹스인 - 공통 이벤트 속성 자동 설정"""
    
    def __post_init__(self):
        if not hasattr(self, 'event_id'):
            self.event_id = generate_uuid()
        if not hasattr(self, 'occurred_at'):
            self.occurred_at = utc_now()
        if not hasattr(self, 'event_version'):
            self.event_version = 1
