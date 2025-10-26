from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from ...application.dtos.category_dtos import CategoryDto, DeletionPreviewDto

class CreateCategoryRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=10, pattern=r'^[a-zA-Z0-9가-힣_]+$')
    parent_id: Optional[UUID] = None

class RenameCategoryRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=10, pattern=r'^[a-zA-Z0-9가-힣_]+$')

# Integration Contract 표준 + Unit2 추가 항목
class CategoryData(BaseModel):
    id: UUID
    name: str
    card_count: int  # snake_case 사용
    is_deletable: bool  # snake_case 사용
    # Unit2에서 추가된 항목들
    category_type: str
    parent_id: Optional[UUID]
    hierarchy_level: int
    created_at: datetime
    
    @classmethod
    def from_dto(cls, dto: CategoryDto):
        return cls(
            id=dto.id,
            name=dto.name,
            card_count=dto.card_count,
            is_deletable=dto.is_deletable,
            category_type=dto.category_type,
            parent_id=dto.parent_id,
            hierarchy_level=dto.hierarchy_level,
            created_at=dto.created_at
        )

# Integration Contract 표준 응답 구조
class CategoriesResponse(BaseModel):
    success: bool = True
    data: dict
    message: str = "Categories retrieved successfully"

class CategoryResponse(BaseModel):
    success: bool = True
    data: dict
    message: str = "Category operation completed successfully"

class DeletionPreviewResponse(BaseModel):
    success: bool = True
    data: dict
    message: str = "Deletion preview generated successfully"
