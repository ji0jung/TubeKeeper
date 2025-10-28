from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from ...domain.repositories.category_repository import CategoryRepository
from ...domain.entities.category import Category
from ...domain.value_objects.category_name import CategoryName
from ...domain.value_objects.category_type import CategoryType, CategoryTypeEnum
from ...domain.value_objects.hierarchy_level import HierarchyLevel
from ..models.category_model import CategoryModel

class SQLAlchemyCategoryRepository(CategoryRepository):
    
    def __init__(self, session: Session):
        self._session = session
    
    async def save(self, category: Category) -> Category:
        model = self._to_model(category)
        self._session.merge(model)
        self._session.commit()
        return category
    
    async def find_by_id(self, category_id: UUID) -> Optional[Category]:
        model = self._session.query(CategoryModel).filter(CategoryModel.id == category_id).first()
        return self._to_entity(model) if model else None
    
    async def find_by_user_id(self, user_id: UUID) -> List[Category]:
        models = self._session.query(CategoryModel).filter(CategoryModel.user_id == user_id).all()
        return [self._to_entity(model) for model in models]
    
    async def find_by_id_and_user_id(self, category_id: UUID, user_id: UUID) -> Optional[Category]:
        model = self._session.query(CategoryModel).filter(
            and_(
                CategoryModel.id == category_id,
                CategoryModel.user_id == user_id
            )
        ).first()
        return self._to_entity(model) if model else None
    
    async def delete(self, category_id: UUID) -> None:
        # 카드 존재 여부 확인
        card_count = self._session.execute(
            "SELECT COUNT(*) FROM cards WHERE category_id = :category_id",
            {"category_id": str(category_id)}
        ).scalar()
        
        if card_count > 0:
            raise ValueError("카테고리에 카드가 존재하여 삭제할 수 없습니다")
            
        self._session.query(CategoryModel).filter(CategoryModel.id == category_id).delete()
        self._session.commit()
    
    async def exists_by_name_and_parent(self, user_id: UUID, name: str, parent_id: Optional[UUID]) -> bool:
        query = self._session.query(CategoryModel).filter(
            and_(
                CategoryModel.user_id == user_id,
                CategoryModel.name == name,
                CategoryModel.parent_id == parent_id
            )
        )
        return query.first() is not None
    
    def _to_model(self, category: Category) -> CategoryModel:
        return CategoryModel(
            id=category.id,
            user_id=category.user_id,
            name=category.name.value,
            category_type=category.category_type.value,
            parent_id=category.parent_id,
            hierarchy_level=category.hierarchy_level.value,
            created_at=category.created_at,
            updated_at=category.updated_at
        )
    
    def _to_entity(self, model: CategoryModel) -> Category:
        return Category(
            id=model.id,
            user_id=model.user_id,
            name=CategoryName(model.name),
            category_type=CategoryType(model.category_type),
            parent_id=model.parent_id,
            hierarchy_level=HierarchyLevel(model.hierarchy_level),
            created_at=model.created_at,
            updated_at=model.updated_at
        )
