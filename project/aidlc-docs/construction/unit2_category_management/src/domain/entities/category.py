from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from ..value_objects.category_name import CategoryName
from ..value_objects.category_type import CategoryType
from ..value_objects.hierarchy_level import HierarchyLevel
from ..events.base import DomainEvent

@dataclass
class Category:
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = None
    name: CategoryName = None
    category_type: CategoryType = None
    parent_id: Optional[UUID] = None
    hierarchy_level: HierarchyLevel = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    _domain_events: List[DomainEvent] = field(default_factory=list, init=False)
    
    def rename(self, new_name: CategoryName):
        if not self.category_type.is_deletable():
            raise ValueError("시스템 카테고리는 이름을 변경할 수 없습니다")
        
        old_name = self.name.value
        self.name = new_name
        self.updated_at = datetime.utcnow()
        
        from ..events.category_events import CategoryRenamed
        self._domain_events.append(CategoryRenamed(
            user_id=self.user_id,
            category_id=self.id,
            old_name=old_name,
            new_name=new_name.value
        ))
    
    def can_be_deleted(self) -> bool:
        return self.category_type.is_deletable()
    
    def get_domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()
    
    def clear_domain_events(self):
        self._domain_events.clear()
