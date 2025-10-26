from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from uuid import UUID

@dataclass
class CategoryDto:
    id: UUID
    name: str
    category_type: str
    parent_id: Optional[UUID]
    hierarchy_level: int
    card_count: int
    is_deletable: bool
    created_at: datetime

@dataclass
class DeletionPreviewDto:
    category_id: UUID
    category_name: str
    card_count: int
    subcategory_count: int
    subcategories: List[dict]
    can_delete: bool
    requires_card_migration: bool
    requires_subcategory_migration: bool

@dataclass
class CreateCategoryResult:
    success: bool
    category: Optional[CategoryDto] = None
    error_message: Optional[str] = None

@dataclass
class DeleteCategoryResult:
    success: bool
    error_message: Optional[str] = None
