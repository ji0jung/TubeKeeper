from dataclasses import dataclass
from uuid import UUID

@dataclass
class GetCategoriesQuery:
    user_id: UUID

@dataclass
class GetCategoryQuery:
    user_id: UUID
    category_id: UUID

@dataclass
class GetDeletionPreviewQuery:
    user_id: UUID
    category_id: UUID
