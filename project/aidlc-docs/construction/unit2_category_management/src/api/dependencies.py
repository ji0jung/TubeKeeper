from sqlalchemy.orm import Session
from fastapi import Depends

from ..infrastructure.database import SessionLocal
from ..infrastructure.repositories.sqlalchemy_category_repository import SQLAlchemyCategoryRepository
from ..infrastructure.cache.redis_cache_service import RedisCacheService
from ..infrastructure.events.redis_event_publisher import RedisEventPublisher
from ..infrastructure.external.mock_card_count_service import MockCardCountService
from ..domain.services.category_deletion_service import CategoryDeletionService
from ..domain.services.category_hierarchy_service import CategoryHierarchyService
from ..application.services.category_application_service import CategoryApplicationService

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_category_service(db: Session = Depends(get_db)) -> CategoryApplicationService:
    category_repo = SQLAlchemyCategoryRepository(db)
    cache_service = RedisCacheService()
    event_publisher = RedisEventPublisher()
    card_count_service = MockCardCountService()  # Unit2 독립 테스트용
    deletion_service = CategoryDeletionService()
    hierarchy_service = CategoryHierarchyService()
    
    return CategoryApplicationService(
        category_repo=category_repo,
        cache_service=cache_service,
        event_publisher=event_publisher,
        card_count_service=card_count_service,
        deletion_service=deletion_service,
        hierarchy_service=hierarchy_service
    )
