from dataclasses import dataclass
from typing import Optional
from uuid import UUID

@dataclass
class CreateCategoryCommand:
    user_id: UUID
    name: str
    parent_id: Optional[UUID] = None

@dataclass
class RenameCategoryCommand:
    user_id: UUID
    category_id: UUID
    new_name: str

@dataclass
class DeleteCategoryCommand:
    user_id: UUID
    category_id: UUID
