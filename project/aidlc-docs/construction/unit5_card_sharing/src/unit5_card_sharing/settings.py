import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5435/unit5_sharing"
    redis_url: str = "redis://localhost:6381/0"
    jwt_secret_key: str = "unit5-secret-key"
    share_link_base_url: str = "http://localhost:8005"
    rate_limit_share_creation: int = 20
    rate_limit_share_access: int = 60
    
    def __init__(self, **kwargs):
        # 환경변수 우선 적용
        env_values = {
            'database_url': os.getenv('DATABASE_URL'),
            'redis_url': os.getenv('REDIS_URL'),
            'jwt_secret_key': os.getenv('JWT_SECRET_KEY'),
            'share_link_base_url': os.getenv('SHARE_LINK_BASE_URL'),
        }
        # None이 아닌 값만 업데이트
        env_values = {k: v for k, v in env_values.items() if v is not None}
        kwargs.update(env_values)
        super().__init__(**kwargs)
    
    class Config:
        env_file = ".env"

settings = Settings()
