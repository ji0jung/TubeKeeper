from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "postgresql://aidlc_user:dev_password@localhost:5432/aidlc_auth"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "aidlc_auth"
    db_user: str = "aidlc_user"
    db_password: str = "dev_password"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # JWT Configuration
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_days: int = 7
    
    # AWS SES Configuration
    aws_region: str = "us-east-1"
    ses_sender_email: str = "jhrhee@amazon.com"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    
    # Application Configuration
    app_name: str = "AIDLC Authentication Service"
    app_version: str = "0.1.0"
    debug: bool = True
    log_level: str = "INFO"
    
    # Security Configuration
    session_max_count: int = 3
    verification_code_expire_minutes: int = 15
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
