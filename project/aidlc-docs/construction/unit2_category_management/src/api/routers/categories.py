from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID

from ..models.category_models import CreateCategoryRequest, RenameCategoryRequest, CategoryData, CategoriesResponse, CategoryResponse, DeletionPreviewResponse
from ..middleware.auth import get_current_user
from ..dependencies import get_category_service
from ...application.services.category_application_service import CategoryApplicationService
from ...application.commands.category_commands import CreateCategoryCommand, RenameCategoryCommand, DeleteCategoryCommand
from ...application.queries.category_queries import GetCategoriesQuery, GetCategoryQuery, GetDeletionPreviewQuery
from ...application.exceptions.application_exceptions import ApplicationException

router = APIRouter(prefix="/api/categories", tags=["categories"])

@router.get("", response_model=CategoriesResponse)
async def get_categories(
    current_user: dict = Depends(get_current_user),
    service: CategoryApplicationService = Depends(get_category_service)
):
    query = GetCategoriesQuery(user_id=current_user["user_id"])
    categories = await service.get_categories(query)
    category_data = [CategoryData.from_dto(dto) for dto in categories]
    
    return CategoriesResponse(
        success=True,
        data={"categories": [cat.dict() for cat in category_data]},
        message="Categories retrieved successfully"
    )

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: CategoryApplicationService = Depends(get_category_service)
):
    query = GetCategoryQuery(user_id=current_user["user_id"], category_id=category_id)
    try:
        category = await service.get_category(query)
        category_data = CategoryData.from_dto(category)
        return CategoryResponse(
            success=True,
            data={"category": category_data.dict()},
            message="Category retrieved successfully"
        )
    except ApplicationException as e:
        if e.error_code == "CATEGORY_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    request: CreateCategoryRequest,
    current_user: dict = Depends(get_current_user),
    service: CategoryApplicationService = Depends(get_category_service)
):
    command = CreateCategoryCommand(
        user_id=current_user["user_id"],
        name=request.name,
        parent_id=request.parent_id
    )
    
    result = await service.create_category(command)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error_message
        )
    
    category_data = CategoryData.from_dto(result.category)
    return CategoryResponse(
        success=True,
        data={"category": category_data.dict()},
        message="Category created successfully"
    )

@router.put("/{category_id}", response_model=CategoryResponse)
async def rename_category(
    category_id: UUID,
    request: RenameCategoryRequest,
    current_user: dict = Depends(get_current_user),
    service: CategoryApplicationService = Depends(get_category_service)
):
    command = RenameCategoryCommand(
        user_id=current_user["user_id"],
        category_id=category_id,
        new_name=request.name
    )
    
    try:
        result = await service.rename_category(command)
        if not result.success:
            if "카테고리를 찾을 수 없습니다" in result.error_message:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.error_message)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=result.error_message)
        
        category_data = CategoryData.from_dto(result.category)
        return CategoryResponse(
            success=True,
            data={"category": category_data.dict()},
            message="Category updated successfully"
        )
    except ApplicationException as e:
        if e.error_code == "CATEGORY_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

@router.get("/{category_id}/deletion-preview", response_model=DeletionPreviewResponse)
async def get_deletion_preview(
    category_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: CategoryApplicationService = Depends(get_category_service)
):
    query = GetDeletionPreviewQuery(
        user_id=current_user["user_id"],
        category_id=category_id
    )
    
    try:
        preview = await service.get_deletion_preview(query)
        preview_data = {
            "category_id": preview.category_id,
            "category_name": preview.category_name,
            "card_count": preview.card_count,
            "subcategory_count": preview.subcategory_count,
            "subcategories": [{"id": sub["id"], "name": sub["name"]} for sub in preview.subcategories],
            "can_delete": preview.can_delete,
            "requires_card_migration": preview.requires_card_migration,
            "requires_subcategory_migration": preview.requires_subcategory_migration
        }
        return DeletionPreviewResponse(
            success=True,
            data=preview_data,
            message="Deletion preview generated successfully"
        )
    except ApplicationException as e:
        if e.error_code == "CATEGORY_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: CategoryApplicationService = Depends(get_category_service)
):
    command = DeleteCategoryCommand(
        user_id=current_user["user_id"],
        category_id=category_id
    )
    
    try:
        result = await service.delete_category(command)
        if not result.success:
            # CategoryNotFoundException이 발생한 경우 404 반환
            if "카테고리를 찾을 수 없습니다" in result.error_message:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result.error_message)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.error_message
            )
    except ApplicationException as e:
        if e.error_code == "CATEGORY_NOT_FOUND":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
