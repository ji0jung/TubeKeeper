import os

class Settings:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/unit2_categories")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.jwt_secret = os.getenv("JWT_SECRET", "your-jwt-secret-key")
        self.jwt_algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.cache_ttl = int(os.getenv("CACHE_TTL", "1800"))
        self.max_categories_per_user = int(os.getenv("MAX_CATEGORIES_PER_USER", "100"))
        self.max_category_hierarchy_depth = int(os.getenv("MAX_CATEGORY_HIERARCHY_DEPTH", "3"))

settings = Settings()
