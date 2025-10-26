from uuid import UUID
from typing import Optional
from domain.entities.profile import Profile
from domain.entities.user import User
from domain.value_objects.gender import Gender
from domain.value_objects.birth_year import BirthYear
from domain.value_objects.language import Language
from infrastructure.persistence.repositories.postgresql_profile_repository import PostgreSQLProfileRepository
from infrastructure.persistence.repositories.postgresql_user_repository import PostgreSQLUserRepository


class ProfileAppService:
    """프로필 애플리케이션 서비스"""
    
    def __init__(self, profile_repo: PostgreSQLProfileRepository, user_repo: PostgreSQLUserRepository):
        self.profile_repo = profile_repo
        self.user_repo = user_repo
    
    async def get_profile(self, user_id: UUID) -> dict:
        """프로필 조회"""
        # 사용자 존재 확인
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise Exception("사용자를 찾을 수 없습니다")
        
        # 프로필 조회
        profile = await self.profile_repo.find_by_user_id(user_id)
        
        if not profile:
            # 프로필이 없으면 기본 프로필 생성
            profile = Profile.create(user_id=user_id)
            await self.profile_repo.save(profile)
        
        return {
            "email": user.email.value,
            "gender": profile.gender.value if profile.gender else None,
            "birth_year": profile.birth_year.value if profile.birth_year else None,
            "language": profile.language.value
        }
    
    async def update_profile(self, user_id: UUID, gender: Optional[str], birth_year: Optional[int], language: Optional[str]) -> dict:
        """프로필 수정"""
        # 사용자 존재 확인
        user = await self.user_repo.find_by_id(user_id)
        if not user:
            raise Exception("사용자를 찾을 수 없습니다")
        
        # 기존 프로필 조회 또는 생성
        profile = await self.profile_repo.find_by_user_id(user_id)
        if not profile:
            profile = Profile.create(user_id=user_id)
        
        # 프로필 업데이트 (각 메서드에서 updated_at 자동 갱신)
        if gender is not None:
            profile.update_gender(Gender(gender))
        if birth_year is not None:
            profile.update_birth_year(BirthYear(birth_year))
        if language is not None:
            profile.update_language(Language(language))
        
        await self.profile_repo.save(profile)
        
        return {
            "email": user.email.value,
            "gender": profile.gender.value if profile.gender else None,
            "birth_year": profile.birth_year.value if profile.birth_year else None,
            "language": profile.language.value
        }
