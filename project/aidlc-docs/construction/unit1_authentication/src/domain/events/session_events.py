from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.events.base_event import EventMixin
from domain.value_objects.device_info import DeviceInfo


@dataclass
class UserLoggedIn(EventMixin):
    """사용자 로그인 이벤트"""
    user_id: UUID
    session_id: UUID
    device_info: DeviceInfo


@dataclass
class SessionExtended(EventMixin):
    """세션 연장 이벤트"""
    user_id: UUID
    session_id: UUID
    new_expiry_time: datetime


@dataclass
class MaxSessionLimitReached(EventMixin):
    """최대 세션 제한 도달 이벤트"""
    user_id: UUID
    new_session_id: UUID
    terminated_session_id: UUID
    device_info: DeviceInfo
