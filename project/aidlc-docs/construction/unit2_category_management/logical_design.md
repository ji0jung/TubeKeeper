# Unit2: Category Management - Logical Design

## 1. 애플리케이션 서비스 계층 설계

### 1.1 CategoryApplicationService

```python
class CategoryApplicationService:
    def __init__(
        self,
        category_repo: CategoryRepository,
        card_count_service: CardCountServiceInterface,
        event_publisher: EventPublisher,
        cache_service: CacheServiceInterface
    ):
        self._category_repo = category_repo
        self._card_count_service = card_count_service
        self._event_publisher = event_publisher
        self._cache_service = cache_service
    
    async def create_category(self, command: CreateCategoryCommand) -> CategoryDto:
        # 검증 → 생성 → 저장 → 이벤트 발행
        
    async def get_categories(self, query: GetCategoriesQuery) -> List[CategoryDto]:
        # 캐시 확인 → DB 조회 → 카드 수 조회 → 캐싱
        
    async def get_category(self, query: GetCategoryQuery) -> CategoryDto:
        # 개별 카테고리 조회 (사용자 권한 검증 포함)
        
    async def get_deletion_preview(self, query: GetDeletionPreviewQuery) -> DeletionPreviewDto:
        # 삭제 영향도 미리보기 (하위 카테고리, 카드 수, 이동 옵션)
        
    async def delete_category(self, command: DeleteCategoryCommand) -> DeleteCategoryResult:
        # 삭제 가능 검증 → 하위 카테고리/카드 이동 → 동기/비동기 분기
```

### 1.2 커맨드/쿼리 객체

```python
@dataclass
class DeleteCategoryCommand:
    user_id: UUID
    category_id: UUID
    subcategory_target_id: Optional[UUID] = None  # 하위 카테고리 이동 대상
    card_migration_strategy: MigrationStrategy = MigrationStrategy.AUTO

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

@dataclass
class MigrationStrategy:
    AUTO = "auto"  # 임시 카테고리로 자동 이동
    MANUAL = "manual"  # 사용자가 개별 지정
    DISTRIBUTE = "distribute"  # 하위 카테고리별로 분산
```

## 2. 도메인 서비스 구현 명세

### 2.1 CategoryDeletionService (개선됨)

```python
class CategoryDeletionService:
    SYNC_THRESHOLD = 10
    
    async def can_delete(self, category_id: UUID) -> bool:
        category = await self._category_repo.find_by_id(category_id)
        # 시스템 카테고리만 삭제 불가 (하위 카테고리 존재 여부 무관)
        return category.category_type not in [CategoryType.SHARED_CARDS, CategoryType.TEMPORARY]
    
    async def prepare_deletion(self, category_id: UUID) -> DeletionPlan:
        category = await self._category_repo.find_by_id(category_id)
        subcategories = await self._category_repo.find_by_parent_id(category_id)
        cards_count = await self._card_count_service.get_card_count(category_id)
        
        return DeletionPlan(
            category_id=category_id,
            subcategories_to_move=subcategories,
            cards_to_move=cards_count,
            requires_subcategory_migration=len(subcategories) > 0,
            total_operations=len(subcategories) + cards_count
        )
    
    async def execute_deletion_with_migration(self, plan: DeletionPlan, target_id: Optional[UUID]) -> DeleteCategoryResult:
        # 1. 하위 카테고리 이동
        if plan.subcategories_to_move:
            await self._migrate_subcategories(plan.subcategories_to_move, target_id)
        
        # 2. 카드 이동 (동기/비동기 분기)
        if plan.total_operations < self.SYNC_THRESHOLD:
            return await self._execute_sync_deletion(plan)
        else:
            return await self._execute_async_deletion(plan)
    
    async def _migrate_subcategories(self, subcategories: List[Category], target_id: Optional[UUID]):
        for subcategory in subcategories:
            subcategory.move_to_parent(target_id)
            await self._category_repo.save(subcategory)
```

### 2.2 CategoryHierarchyService

```python
class CategoryHierarchyService:
    async def get_possible_migration_targets(self, user_id: UUID, category_id: UUID) -> List[Category]:
        all_categories = await self._category_repo.find_by_user_id(user_id)
        descendants = await self.find_descendants(category_id)
        
        # 자기 자신과 하위 카테고리는 제외
        excluded_ids = {category_id} | set(descendants)
        return [cat for cat in all_categories if cat.id not in excluded_ids]
```

## 3. DTO 및 스키마 설계

### 3.1 개선된 DTO

```python
@dataclass
class CategoryDto:
    id: UUID
    name: str
    card_count: int
    subcategory_count: int  # 추가
    is_deletable: bool
    status: CategoryStatus
    parent_id: Optional[UUID] = None
    hierarchy_level: int = 1

@dataclass
class DeletionPreviewDto:
    category: CategoryDto
    subcategories: List[CategoryDto]
    total_cards: int
    possible_targets: List[CategoryDto]
    deletion_complexity: str  # "simple" | "complex"

@dataclass
class DeleteCategoryResult:
    category_id: UUID
    deletion_type: str  # "immediate" | "background"
    task_id: Optional[UUID] = None
    migrated_subcategories: int = 0
    migrated_cards: int = 0
```

### 3.2 API 스키마 (Integration Contract 표준)

```python
# Integration Contract 표준 카테고리 데이터
class CategoryData(BaseModel):
    id: UUID
    name: str
    card_count: int
    is_deletable: bool
    # Unit2 추가 항목들
    category_type: str
    parent_id: Optional[UUID]
    hierarchy_level: int
    created_at: datetime

# Integration Contract 표준 응답 구조
class CategoriesResponse(BaseModel):
    success: bool = True
    data: dict  # { "categories": [CategoryData] }
    message: str = "Categories retrieved successfully"

class CategoryResponse(BaseModel):
    success: bool = True
    data: dict  # { "category": CategoryData }
    message: str = "Category operation completed successfully"

class DeletionPreviewResponse(BaseModel):
    success: bool = True
    data: dict  # 삭제 미리보기 정보
    message: str = "Deletion preview generated successfully"
```

## 4. API 컨트롤러 설계

### 4.1 CategoryController (Integration Contract 표준)

```python
@router.get("/categories", response_model=CategoriesResponse)
async def get_categories(
    current_user: User = Depends(get_current_user),
    service: CategoryApplicationService = Depends()
) -> CategoriesResponse:
    query = GetCategoriesQuery(user_id=current_user.id)
    categories = await service.get_categories(query)
    category_data = [CategoryData.from_dto(dto) for dto in categories]
    
    return CategoriesResponse(
        success=True,
        data={"categories": [cat.dict() for cat in category_data]},
        message="Categories retrieved successfully"
    )

@router.delete("/categories/{category_id}", response_model=CategoryResponse)
async def delete_category(
    category_id: UUID,
    current_user: User = Depends(get_current_user),
    service: CategoryApplicationService = Depends()
) -> CategoryResponse:
    command = DeleteCategoryCommand(user_id=current_user.id, category_id=category_id)
    result = await service.delete_category(command)
    return CategoryResponse(
        success=True,
        data={},
        message="Category deleted successfully"
    )
```
    command = DeleteCategoryCommand(
        user_id=current_user.id,
        category_id=category_id,
        subcategory_target_id=request.subcategory_target_id,
        card_migration_strategy=request.card_migration_strategy
    )
    result = await service.delete_category(command)
    return DeleteCategoryResponseSchema.from_result(result)
```

## 5. 도메인 엔티티 개선

### 5.1 Category 엔티티

```python
class Category:
    def is_deletable(self) -> bool:
        # 시스템 카테고리만 삭제 불가
        return self.category_type not in [CategoryType.SHARED_CARDS, CategoryType.TEMPORARY]
    
    def move_to_parent(self, new_parent_id: Optional[UUID]) -> None:
        if new_parent_id == self.parent_category_id:
            return
        
        self.parent_category_id = new_parent_id
        self.hierarchy_level = self._calculate_new_level(new_parent_id)
        self._add_domain_event(CategoryMoved(
            category_id=self.id,
            old_parent_id=self.parent_category_id,
            new_parent_id=new_parent_id
        ))
```

## 6. 이벤트 핸들러 설계

### 6.1 백그라운드 삭제 처리 (개선됨)

```python
class BackgroundCategoryDeletionTask:
    async def execute_category_deletion(self, deletion_plan: DeletionPlan, task_id: UUID):
        try:
            # 1. 카테고리 상태를 DELETING으로 변경
            await self._update_category_status(deletion_plan.category_id, CategoryStatus.DELETING)
            
            # 2. 하위 카테고리 이동
            if deletion_plan.subcategories_to_move:
                await self._migrate_subcategories(deletion_plan)
            
            # 3. 카드 이동 처리
            await self._migrate_cards(deletion_plan)
            
            # 4. 카테고리 최종 삭제
            await self._finalize_deletion(deletion_plan.category_id)
            
            # 5. 완료 이벤트 발행
            await self._publish_completion_event(task_id, deletion_plan)
            
        except Exception as e:
            await self._handle_deletion_failure(deletion_plan.category_id, e)
```

## 7. PostgreSQL 테이블 설계

### 7.1 categories 테이블 (개선됨)

```sql
CREATE TABLE categories (
    category_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    name VARCHAR(10) NOT NULL,
    category_type VARCHAR(20) NOT NULL,
    parent_category_id UUID,
    hierarchy_level INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id) ON DELETE SET NULL,
    UNIQUE(user_id, parent_category_id, name),
    CHECK (hierarchy_level BETWEEN 1 AND 3)
);

CREATE INDEX idx_categories_user_id ON categories(user_id);
CREATE INDEX idx_categories_parent_id ON categories(parent_category_id);
CREATE INDEX idx_categories_status ON categories(status) WHERE status != 'ACTIVE';
```

## 8. 도메인 이벤트

### 8.1 새로운 이벤트

```python
@dataclass
class SubcategoriesMigrated(DomainEvent):
    source_category_id: UUID
    target_category_id: Optional[UUID]
    migrated_category_ids: List[UUID]
    user_id: UUID

@dataclass
class CategoryDeletionCompleted(DomainEvent):
    category_id: UUID
    user_id: UUID
    migrated_subcategories: int
    migrated_cards: int
    task_id: Optional[UUID] = None
```

## 9. 캐시 무효화 전략

### 9.1 계층 구조 변경 시 캐시 처리

```python
async def invalidate_hierarchy_cache(self, user_id: UUID, affected_category_ids: List[UUID]):
    # 사용자 전체 카테고리 캐시 무효화
    await self._redis.delete(f"categories:user:{user_id}")
    await self._redis.delete(f"categories:tree:{user_id}")
    
    # 영향받은 카테고리들의 개별 캐시도 무효화
    for category_id in affected_category_ids:
        await self._redis.delete(f"category:details:{category_id}")
```
