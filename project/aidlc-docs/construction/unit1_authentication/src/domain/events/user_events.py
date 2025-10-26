from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from domain.events.base_event import EventMixin
from domain.value_objects.email import Email
from domain.value_objects.gender import Gender
from domain.value_objects.birth_year import BirthYear


@dataclass
class UserRegistrationRequested(EventMixin):
    """사용자 등록 요청 이벤트"""
    email: Email
    gender: Optional[Gender]
    birth_year: Optional[BirthYear]


@dataclass
class UserRegistered(EventMixin):
    """사용자 등록 완료 이벤트"""
    user_id: UUID
    email: Email
    profile_id: UUID


@dataclass
class UserDeactivated(EventMixin):
    """사용자 비활성화 이벤트"""
    user_id: UUID
    deactivated_at: datetime


@dataclass
class ProfileUpdated(EventMixin):
    """프로필 업데이트 이벤트"""
    user_id: UUID
    profile_id: UUID
    changed_fields: Dict[str, Any]
