"""Unit4: Card Search & Display - Configuration Settings"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings for Unit4 Card Search & Display"""
    
    # Database Configuration
    database_url: str
    database_pool_size: int = 20
    database_max_overflow: int = 30
    
    # Redis Configuration
    redis_url: str
    redis_search_cache_db: int = 1
    redis_suggestion_cache_db: int = 2
    
    # Search Configuration
    search_cache_ttl_my_cards: int = 180
    search_cache_ttl_public_cards: int = 300
    suggestion_cache_ttl: int = 3600
    popular_tags_cache_ttl: int = 86400
    
    # Pagination Configuration
    default_page_size: int = 20
    max_page_size: int = 100
    cursor_page_size: int = 20
    
    # Full-text Search Configuration
    postgres_fts_language: str = "korean"
    search_min_query_length: int = 2
    search_max_query_length: int = 100
    
    # Statistics Configuration
    enable_search_statistics: bool = True
    statistics_retention_days: int = 90
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"
    
    # Unit3 Integration
    unit3_service_url: str
    unit3_api_key: Optional[str] = None
    
    # JWT Configuration
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 10080
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
