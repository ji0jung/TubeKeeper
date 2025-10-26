from typing import List, Optional, Any
from uuid import UUID

from domain.entities.user import User
from domain.entities.profile import Profile
from domain.events.user_events import UserRegistered, ProfileUpdated, UserDeactivated
from domain.value_objects.email import Email
from domain.value_objects.gender import Gender
from domain.value_objects.birth_year import BirthYear
from domain.value_objects.language import Language


class UserAggregate:
    """사용자 애그리게이트 - User와 Profile을 함께 관리"""
    
    def __init__(self, user: User, profile: Profile):
        self._user = user
        self._profile = profile
        self._domain_events: List[Any] = []
    
    @classmethod
    def create_new_user(cls, email: Email, gender: Optional[Gender] = None, 
                       birth_year: Optional[BirthYear] = None) -> 'UserAggregate':
        """새 사용자 생성"""
        user = User.create(email)
        profile = Profile.create(user.user_id, gender, birth_year)
        
        aggregate = cls(user, profile)
        aggregate._add_event(UserRegistered(
            user_id=user.user_id,
            email=email,
            profile_id=profile.profile_id
        ))
        
        return aggregate
    
    @classmethod
    def from_existing(cls, user: User, profile: Profile) -> 'UserAggregate':
        """기존 사용자로부터 애그리게이트 생성"""
        return cls(user, profile)
    
    def activate(self) -> None:
        """사용자 활성화"""
        self._user.activate()
    
    def deactivate(self) -> None:
        """사용자 비활성화"""
        self._user.deactivate()
        self._add_event(UserDeactivated(
            user_id=self._user.user_id,
            deactivated_at=self._user.deactivated_at
        ))
    
    def update_profile(self, gender: Optional[Gender] = None, 
                      birth_year: Optional[BirthYear] = None) -> None:
        """프로필 업데이트"""
        changed_fields = {}
        
        if gender is not None:
            self._profile.update_gender(gender)
            changed_fields['gender'] = gender.value
        
        if birth_year is not None:
            self._profile.update_birth_year(birth_year)
            changed_fields['birth_year'] = birth_year.value
        
        if changed_fields:
            self._add_event(ProfileUpdated(
                user_id=self._user.user_id,
                profile_id=self._profile.profile_id,
                changed_fields=changed_fields
            ))
    
    def change_language(self, language: Language) -> None:
        """언어 변경"""
        self._profile.update_language(language)
        self._add_event(ProfileUpdated(
            user_id=self._user.user_id,
            profile_id=self._profile.profile_id,
            changed_fields={'language': language.value}
        ))
    
    def can_login(self) -> bool:
        """로그인 가능 여부 확인"""
        return self._user.can_login()
    
    def update_last_activity(self) -> None:
        """마지막 활동 시간 업데이트"""
        self._user.update_last_activity()
    
    @property
    def user(self) -> User:
        return self._user
    
    @property
    def profile(self) -> Profile:
        return self._profile
    
    @property
    def domain_events(self) -> List[Any]:
        return self._domain_events.copy()
    
    def clear_events(self) -> None:
        """이벤트 목록 초기화"""
        self._domain_events.clear()
    
    def _add_event(self, event: Any) -> None:
        """도메인 이벤트 추가"""
        self._domain_events.append(event)
