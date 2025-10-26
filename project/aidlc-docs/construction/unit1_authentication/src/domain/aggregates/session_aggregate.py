from typing import List, Any
from uuid import UUID

from domain.entities.session import Session
from domain.events.session_events import UserLoggedIn, SessionExtended
from domain.value_objects.device_info import DeviceInfo


class SessionAggregate:
    """세션 애그리게이트 - 독립적 세션 관리"""
    
    def __init__(self, session: Session):
        self._session = session
        self._domain_events: List[Any] = []
    
    @classmethod
    def create_new_session(cls, user_id: UUID, device_info: DeviceInfo, 
                          expire_days: int = 7) -> 'SessionAggregate':
        """새 세션 생성"""
        session = Session.create(user_id, device_info, expire_days)
        
        aggregate = cls(session)
        aggregate._add_event(UserLoggedIn(
            user_id=user_id,
            session_id=session.session_id,
            device_info=device_info
        ))
        
        return aggregate
    
    @classmethod
    def from_existing(cls, session: Session) -> 'SessionAggregate':
        """기존 세션으로부터 애그리게이트 생성"""
        return cls(session)
    
    def extend(self, expire_days: int = 7) -> None:
        """세션 연장"""
        self._session.extend(expire_days)
        self._add_event(SessionExtended(
            user_id=self._session.user_id,
            session_id=self._session.session_id,
            new_expiry_time=self._session.expires_at
        ))
    
    def expire(self) -> None:
        """세션 만료"""
        self._session.expire()
    
    def is_expired(self) -> bool:
        """세션 만료 여부 확인"""
        return self._session.is_expired()
    
    def is_same_device(self, device_info: DeviceInfo) -> bool:
        """동일 디바이스 여부 확인"""
        return self._session.is_same_device(device_info)
    
    @property
    def session(self) -> Session:
        return self._session
    
    @property
    def domain_events(self) -> List[Any]:
        return self._domain_events.copy()
    
    def clear_events(self) -> None:
        """이벤트 목록 초기화"""
        self._domain_events.clear()
    
    def _add_event(self, event: Any) -> None:
        """도메인 이벤트 추가"""
        self._domain_events.append(event)
