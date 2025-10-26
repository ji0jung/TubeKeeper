from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/unit3_cards"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # JWT
    jwt_secret: str = "your-jwt-secret-key-for-unit3-cards"
    jwt_algorithm: str = "HS256"
    
    # AWS
    aws_region: str = "us-east-1"
    s3_bucket_name: str = "youtube-keeper-thumbnails-dev"
    
    # External APIs
    youtube_api_key: str
    
    # Application
    log_level: str = "INFO"
    environment: str = "development"
    
    class Config:
        env_file = ".env"


settings = Settings()
