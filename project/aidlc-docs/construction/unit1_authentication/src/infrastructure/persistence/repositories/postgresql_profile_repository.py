import os
from typing import Optional
from uuid import UUID
import asyncpg
from domain.entities.profile import Profile
from domain.value_objects.gender import Gender
from domain.value_objects.birth_year import BirthYear
from domain.value_objects.language import Language


class PostgreSQLProfileRepository:
    """PostgreSQL 프로필 리포지토리"""
    
    def __init__(self):
        self._database_url = None
    
    async def _get_database_url(self):
        """환경변수에서 DB 연결 정보 가져오기"""
        if self._database_url:
            return self._database_url
            
        host = os.getenv('DB_HOST')
        username = os.getenv('DB_USERNAME')
        password = os.getenv('DB_PASSWORD')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME', 'aidlc_auth')
        
        if not all([host, username, password]):
            raise Exception("DB 연결 정보가 환경변수에 설정되지 않았습니다")
            
        self._database_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        return self._database_url
    
    async def _get_connection(self):
        """데이터베이스 연결 획득"""
        database_url = await self._get_database_url()
        return await asyncpg.connect(database_url, ssl='prefer')
    
    async def find_by_user_id(self, user_id: UUID) -> Optional[Profile]:
        """사용자 ID로 프로필 조회"""
        conn = await self._get_connection()
        try:
            row = await conn.fetchrow(
                "SELECT * FROM profiles WHERE user_id = $1", user_id
            )
            if row:
                return Profile(
                    profile_id=row['profile_id'],
                    user_id=row['user_id'],
                    gender=Gender(row['gender']) if row['gender'] else None,
                    birth_year=BirthYear(row['birth_year']) if row['birth_year'] else None,
                    language=Language(row['language']),
                    updated_at=row['updated_at']
                )
            return None
        finally:
            await conn.close()
    
    async def save(self, profile: Profile) -> None:
        """프로필 저장"""
        conn = await self._get_connection()
        try:
            await conn.execute("""
                INSERT INTO profiles (profile_id, user_id, gender, birth_year, language, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                ON CONFLICT (user_id) DO UPDATE SET
                    gender = EXCLUDED.gender,
                    birth_year = EXCLUDED.birth_year,
                    language = EXCLUDED.language,
                    updated_at = EXCLUDED.updated_at,
                    version = profiles.version + 1
            """, 
                profile.profile_id,
                profile.user_id,
                profile.gender.value if profile.gender else None,
                profile.birth_year.value if profile.birth_year else None,
                profile.language.value,
                profile.updated_at
            )
        finally:
            await conn.close()
