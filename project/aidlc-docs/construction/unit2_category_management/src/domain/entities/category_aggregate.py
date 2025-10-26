from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID

from .category import Category
from ..value_objects.category_name import CategoryName
from ..value_objects.category_type import CategoryType, CategoryTypeEnum
from ..value_objects.hierarchy_level import HierarchyLevel
from ..events.category_events import CategoryCreated, CategoryDeleted, SharedCardsCategoryCreated, TemporaryCategoryCreated

@dataclass
class CategoryAggregate:
    user_id: UUID
    categories: List[Category] = field(default_factory=list)
    
    def create_category(self, name: CategoryName, parent_id: Optional[UUID] = None) -> Category:
        self._validate_category_limit()
        self._validate_name_uniqueness(name, parent_id)
        
        hierarchy_level = self._calculate_hierarchy_level(parent_id)
        
        category = Category(
            user_id=self.user_id,
            name=name,
            category_type=CategoryType.regular(),
            parent_id=parent_id,
            hierarchy_level=hierarchy_level
        )
        
        category._domain_events.append(CategoryCreated(
            user_id=self.user_id,
            category_id=category.id,
            category_name=name.value,
            parent_id=parent_id
        ))
        
        self.categories.append(category)
        return category
    
    def create_shared_cards_category(self) -> Category:
        category = Category(
            user_id=self.user_id,
            name=CategoryName("공유받은 카드"),
            category_type=CategoryType.shared_cards(),
            hierarchy_level=HierarchyLevel(1)
        )
        
        category._domain_events.append(SharedCardsCategoryCreated(
            user_id=self.user_id,
            category_id=category.id
        ))
        
        self.categories.append(category)
        return category
    
    def create_temporary_category(self) -> Category:
        existing_temp = self._find_temporary_category()
        if existing_temp:
            return existing_temp
            
        category = Category(
            user_id=self.user_id,
            name=CategoryName("임시"),
            category_type=CategoryType.temporary(),
            hierarchy_level=HierarchyLevel(1)
        )
        
        category._domain_events.append(TemporaryCategoryCreated(
            user_id=self.user_id,
            category_id=category.id
        ))
        
        self.categories.append(category)
        return category
    
    def delete_category(self, category_id: UUID, card_count: int = 0):
        category = self._find_category(category_id)
        if not category.can_be_deleted():
            raise ValueError("시스템 카테고리는 삭제할 수 없습니다")
        
        if card_count > 0:
            raise ValueError("카드가 있는 카테고리는 삭제할 수 없습니다")
        
        category._domain_events.append(CategoryDeleted(
            user_id=self.user_id,
            category_id=category_id,
            category_name=category.name.value,
            card_count=card_count
        ))
        
        self.categories.remove(category)
    
    def _validate_category_limit(self):
        if len(self.categories) >= 100:
            raise ValueError("사용자당 최대 100개의 카테고리만 생성할 수 있습니다")
    
    def _validate_name_uniqueness(self, name: CategoryName, parent_id: Optional[UUID]):
        siblings = [c for c in self.categories if c.parent_id == parent_id]
        if any(c.name.value == name.value for c in siblings):
            raise ValueError("같은 계층에서 중복된 카테고리 이름은 사용할 수 없습니다")
    
    def _calculate_hierarchy_level(self, parent_id: Optional[UUID]) -> HierarchyLevel:
        if not parent_id:
            return HierarchyLevel(1)
        
        parent = self._find_category(parent_id)
        return parent.hierarchy_level.next_level()
    
    def _find_category(self, category_id: UUID) -> Category:
        for category in self.categories:
            if category.id == category_id:
                return category
        raise ValueError(f"카테고리를 찾을 수 없습니다: {category_id}")
    
    def _find_temporary_category(self) -> Optional[Category]:
        for category in self.categories:
            if category.category_type.value == CategoryTypeEnum.TEMPORARY:
                return category
        return None
