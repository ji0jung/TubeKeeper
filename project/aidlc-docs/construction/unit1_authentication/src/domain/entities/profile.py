from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from common.utils import generate_uuid, utc_now
from domain.value_objects.gender import Gender
from domain.value_objects.birth_year import BirthYear
from domain.value_objects.language import Language


@dataclass
class Profile:
    """프로필 엔티티"""
    profile_id: UUID
    user_id: UUID
    gender: Optional[Gender]
    birth_year: Optional[BirthYear]
    language: Language
    updated_at: datetime
    
    def __post_init__(self):
        """초기화 후 처리"""
        if not self.updated_at:
            self.updated_at = utc_now()
    
    @classmethod
    def create(cls, user_id: UUID, gender: Optional[Gender] = None, 
               birth_year: Optional[BirthYear] = None) -> 'Profile':
        """새 프로필 생성"""
        return cls(
            profile_id=generate_uuid(),
            user_id=user_id,
            gender=gender,
            birth_year=birth_year,
            language=Language.KOREAN,  # 기본값
            updated_at=utc_now()
        )
    
    def update_gender(self, gender: Gender) -> None:
        """성별 업데이트"""
        self.gender = gender
        self.updated_at = utc_now()
    
    def update_birth_year(self, birth_year: BirthYear) -> None:
        """출생년도 업데이트"""
        self.birth_year = birth_year
        self.updated_at = utc_now()
    
    def update_language(self, language: Language) -> None:
        """언어 업데이트"""
        self.language = language
        self.updated_at = utc_now()
