from typing import List
from uuid import UUID

from ..commands.category_commands import CreateCategoryCommand, RenameCategoryCommand, DeleteCategoryCommand
from ..queries.category_queries import GetCategoriesQuery, GetCategoryQuery, GetDeletionPreviewQuery
from ..dtos.category_dtos import CategoryDto, DeletionPreviewDto, CreateCategoryResult, DeleteCategoryResult
from ...domain.repositories.category_repository import CategoryRepository
from ...domain.services.cache_service import CacheService
from ...domain.services.event_publisher import EventPublisher
from ...domain.services.card_count_service import CardCountService
from ...domain.services.category_deletion_service import CategoryDeletionService
from ...domain.services.category_hierarchy_service import CategoryHierarchyService
from ...domain.entities.category_aggregate import CategoryAggregate
from ...domain.value_objects.category_name import CategoryName
from ...domain.exceptions.category_exceptions import *
from ..exceptions.application_exceptions import CategoryNotFoundException

class CategoryApplicationService:
    
    def __init__(
        self,
        category_repo: CategoryRepository,
        cache_service: CacheService,
        event_publisher: EventPublisher,
        card_count_service: CardCountService,
        deletion_service: CategoryDeletionService,
        hierarchy_service: CategoryHierarchyService
    ):
        self._category_repo = category_repo
        self._cache_service = cache_service
        self._event_publisher = event_publisher
        self._card_count_service = card_count_service
        self._deletion_service = deletion_service
        self._hierarchy_service = hierarchy_service
    
    async def create_category(self, command: CreateCategoryCommand) -> CreateCategoryResult:
        try:
            categories = await self._category_repo.find_by_user_id(command.user_id)
            aggregate = CategoryAggregate(command.user_id, categories)
            
            category = aggregate.create_category(
                CategoryName(command.name),
                command.parent_id
            )
            
            await self._category_repo.save(category)
            await self._cache_service.invalidate_user_categories(command.user_id)
            
            for event in category.get_domain_events():
                await self._event_publisher.publish(event)
            
            category_dto = await self._to_dto(category)
            return CreateCategoryResult(success=True, category=category_dto)
            
        except Exception as e:
            return CreateCategoryResult(success=False, error_message=str(e))
    
    async def get_categories(self, query: GetCategoriesQuery) -> List[CategoryDto]:
        cache_key = f"categories:user:{query.user_id}:list"
        cached = await self._cache_service.get(cache_key)
        
        if cached:
            return [CategoryDto(**item) for item in cached]
        
        categories = await self._category_repo.find_by_user_id(query.user_id)
        category_ids = [c.id for c in categories]
        card_counts = await self._card_count_service.get_card_counts(category_ids)
        
        dtos = []
        for category in categories:
            dto = await self._to_dto(category, card_counts.get(category.id, 0))
            dtos.append(dto)
        
        await self._cache_service.set(cache_key, [dto.__dict__ for dto in dtos])
        return dtos
    
    async def get_category(self, query: GetCategoryQuery) -> CategoryDto:
        category = await self._category_repo.find_by_id_and_user_id(query.category_id, query.user_id)
        if not category:
            raise CategoryNotFoundException(f"카테고리를 찾을 수 없습니다: {query.category_id}")
        
        card_count = await self._card_count_service.get_card_count_by_category(query.category_id)
        return await self._to_dto(category, card_count)
    
    async def get_deletion_preview(self, query: GetDeletionPreviewQuery) -> DeletionPreviewDto:
        category = await self._category_repo.find_by_id_and_user_id(query.category_id, query.user_id)
        if not category:
            raise CategoryNotFoundException(str(query.category_id))
        
        categories = await self._category_repo.find_by_user_id(query.user_id)
        subcategories = self._hierarchy_service.get_subcategories(categories, query.category_id)
        card_count = await self._card_count_service.get_card_count(query.category_id)
        
        impact = self._deletion_service.get_deletion_impact(category, card_count, subcategories)
        
        return DeletionPreviewDto(
            category_id=impact["category_id"],
            category_name=impact["category_name"],
            card_count=impact["card_count"],
            subcategory_count=impact["subcategory_count"],
            subcategories=impact["subcategories"],
            can_delete=impact["can_delete"],
            requires_card_migration=impact["requires_card_migration"],
            requires_subcategory_migration=impact["requires_subcategory_migration"]
        )
    
    async def rename_category(self, command: RenameCategoryCommand) -> CreateCategoryResult:
        try:
            category = await self._category_repo.find_by_id_and_user_id(command.category_id, command.user_id)
            if not category:
                raise CategoryNotFoundException(str(command.category_id))
            
            category.rename(CategoryName(command.new_name))
            await self._category_repo.save(category)
            await self._cache_service.invalidate_user_categories(command.user_id)
            
            for event in category.get_domain_events():
                await self._event_publisher.publish(event)
            
            category_dto = await self._to_dto(category)
            return CreateCategoryResult(success=True, category=category_dto)
            
        except Exception as e:
            return CreateCategoryResult(success=False, error_message=str(e))
    
    async def delete_category(self, command: DeleteCategoryCommand) -> DeleteCategoryResult:
        try:
            categories = await self._category_repo.find_by_user_id(command.user_id)
            aggregate = CategoryAggregate(command.user_id, categories)
            
            card_count = await self._card_count_service.get_card_count(command.category_id)
            aggregate.delete_category(command.category_id, card_count)
            
            await self._category_repo.delete(command.category_id)
            await self._cache_service.invalidate_user_categories(command.user_id)
            
            return DeleteCategoryResult(success=True)
            
        except Exception as e:
            return DeleteCategoryResult(success=False, error_message=str(e))
    
    async def _to_dto(self, category, card_count: int = 0) -> CategoryDto:
        if card_count == 0:
            card_count = await self._card_count_service.get_card_count(category.id)
        
        return CategoryDto(
            id=category.id,
            name=category.name.value,
            category_type=category.category_type.value.value,
            parent_id=category.parent_id,
            hierarchy_level=category.hierarchy_level.value,
            card_count=card_count,
            is_deletable=category.can_be_deleted(),
            created_at=category.created_at
        )
