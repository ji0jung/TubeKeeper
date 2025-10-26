import asyncio
import asyncpg
from infrastructure.persistence.repositories.postgresql_user_repository import PostgreSQLUserRepository


async def initialize_database():
    """데이터베이스 테이블 초기화"""
    repo = PostgreSQLUserRepository()
    
    try:
        conn = await repo._get_connection()
        
        # 테이블 생성 SQL
        create_tables_sql = """
        -- Enable UUID extension
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
        
        -- Users 테이블
        CREATE TABLE IF NOT EXISTS users (
            user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email VARCHAR(255) NOT NULL UNIQUE,
            status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INACTIVE', 'DEACTIVATED')),
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            last_active_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            deactivated_at TIMESTAMP WITH TIME ZONE NULL,
            version INTEGER NOT NULL DEFAULT 1
        );
        
        -- Profiles 테이블 (개인정보)
        CREATE TABLE IF NOT EXISTS profiles (
            profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
            gender VARCHAR(20) NULL CHECK (gender IN ('male', 'female', 'other')),
            birth_year INTEGER NULL CHECK (birth_year >= 1900 AND birth_year <= EXTRACT(YEAR FROM NOW())),
            language VARCHAR(10) NOT NULL DEFAULT 'ko' CHECK (language IN ('ko', 'en')),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            version INTEGER NOT NULL DEFAULT 1,
            UNIQUE(user_id)
        );
        
        -- 인덱스 생성
        CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email);
        CREATE INDEX IF NOT EXISTS idx_users_status ON users(status);
        CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active_at) WHERE status = 'ACTIVE';
        """
        
        await conn.execute(create_tables_sql)
        print("✅ 데이터베이스 테이블이 성공적으로 초기화되었습니다.")
        
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(initialize_database())
