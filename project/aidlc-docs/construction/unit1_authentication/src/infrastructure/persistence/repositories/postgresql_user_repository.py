import os
from typing import Optional
from uuid import UUID
import asyncpg
from domain.entities.user import User
from domain.repositories.user_repository import UserRepository
from domain.value_objects.email import Email
from domain.value_objects.user_status import UserStatus


class PostgreSQLUserRepository(UserRepository):
    """PostgreSQL 사용자 리포지토리"""
    
    def __init__(self):
        self._database_url = None
    
    async def _get_database_url(self):
        """환경변수에서 DB 연결 정보 가져오기"""
        if self._database_url:
            return self._database_url
            
        # 환경변수에서 DB 연결 정보 가져오기
        host = os.getenv('DB_HOST')
        username = os.getenv('DB_USERNAME')
        password = os.getenv('DB_PASSWORD')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME', 'aidlc_auth')
        
        if not all([host, username, password]):
            raise Exception("DB 연결 정보가 환경변수에 설정되지 않았습니다")
            
        self._database_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        print(f"✅ DB 연결 URL 생성: postgresql://{username}:***@{host}:{port}/{database}")
        return self._database_url
    
    async def _get_connection(self):
        """데이터베이스 연결 획득"""
        database_url = await self._get_database_url()
        # SSL을 선호하지만 필수는 아니도록 설정
        return await asyncpg.connect(database_url, ssl='prefer')
    
    async def save(self, user: User) -> None:
        """사용자 저장"""
        conn = await self._get_connection()
        try:
            await conn.execute("""
                INSERT INTO users (user_id, email, status, created_at, last_active_at, deactivated_at)
                VALUES ($1, $2, $3::VARCHAR, $4, $5, $6)
                ON CONFLICT (user_id) DO UPDATE SET
                    email = EXCLUDED.email,
                    status = EXCLUDED.status,
                    last_active_at = EXCLUDED.last_active_at,
                    deactivated_at = EXCLUDED.deactivated_at
            """, user.user_id, user.email.value, user.status.value.upper(), 
                user.created_at, user.last_active_at, user.deactivated_at)
        finally:
            await conn.close()
    
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        """ID로 사용자 조회"""
        conn = await self._get_connection()
        try:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE user_id = $1", user_id
            )
            if row:
                return User(
                    user_id=row['user_id'],
                    email=Email(row['email']),
                    status=UserStatus(row['status']),
                    created_at=row['created_at'],
                    last_active_at=row['last_active_at'],
                    deactivated_at=row['deactivated_at']
                )
            return None
        finally:
            await conn.close()
    
    async def find_by_email(self, email: Email) -> Optional[User]:
        """이메일로 사용자 조회"""
        conn = await self._get_connection()
        try:
            row = await conn.fetchrow(
                "SELECT * FROM users WHERE email = $1", email.value
            )
            if row:
                return User(
                    user_id=row['user_id'],
                    email=Email(row['email']),
                    status=UserStatus(row['status']),
                    created_at=row['created_at'],
                    last_active_at=row['last_active_at'],
                    deactivated_at=row['deactivated_at']
                )
            return None
        finally:
            await conn.close()
    
    async def exists_by_email(self, email: Email) -> bool:
        """이메일 존재 여부 확인"""
        conn = await self._get_connection()
        try:
            count = await conn.fetchval(
                "SELECT COUNT(*) FROM users WHERE email = $1", email.value
            )
            return count > 0
        finally:
            await conn.close()
