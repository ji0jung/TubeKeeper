from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

@dataclass(frozen=True)
class CategoryPath:
    path: List[UUID]
    
    def __post_init__(self):
        if len(self.path) > 3:
            raise ValueError("카테고리 경로는 최대 3단계까지만 허용됩니다")
    
    def get_depth(self) -> int:
        return len(self.path)
    
    def get_parent_id(self) -> Optional[UUID]:
        return self.path[-2] if len(self.path) > 1 else None
    
    def get_root_id(self) -> UUID:
        return self.path[0]
    
    def add_child(self, child_id: UUID):
        if len(self.path) >= 3:
            raise ValueError("최대 계층 깊이를 초과할 수 없습니다")
        return CategoryPath(self.path + [child_id])
