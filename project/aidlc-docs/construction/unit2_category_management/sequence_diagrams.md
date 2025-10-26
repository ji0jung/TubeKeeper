# Unit2: Category Management - Sequence Diagrams

## 1. 카테고리 생성 시퀀스 다이어그램

```mermaid
sequenceDiagram
    participant Client
    participant Controller
    participant AppService
    participant ValidationService
    participant CategoryRepo
    participant Category
    participant EventPublisher
    participant Cache

    Client->>Controller: POST /api/categories {name, parent_id}
    Controller->>AppService: create_category(CreateCategoryCommand)
    
    AppService->>ValidationService: validate_category_creation(name, parent_id, user_id)
    ValidationService->>CategoryRepo: count_by_user_id(user_id)
    CategoryRepo-->>ValidationService: category_count
    ValidationService->>CategoryRepo: find_by_name_and_parent(name, parent_id, user_id)
    CategoryRepo-->>ValidationService: existing_category
    ValidationService-->>AppService: validation_result
    
    AppService->>Category: create_new(user_id, name, parent_id)
    Category->>Category: _add_domain_event(CategoryCreated)
    Category-->>AppService: new_category
    
    AppService->>CategoryRepo: save(category)
    CategoryRepo-->>AppService: saved_category
    
    AppService->>Category: get_domain_events()
    Category-->>AppService: [CategoryCreated]
    AppService->>EventPublisher: publish_domain_events(events)
    EventPublisher->>Cache: invalidate_user_cache(user_id)
    
    AppService-->>Controller: CategoryDto
    Controller-->>Client: 201 Created + { success: true, data: { category: CategoryResponseSchema }, message: "Category created successfully" }
```

## 2. 카테고리 삭제 미리보기 시퀀스 다이어그램

```mermaid
sequenceDiagram
    participant Client
    participant Controller
    participant AppService
    participant DeletionService
    participant CategoryRepo
    participant CardCountService
    participant HierarchyService

    Client->>Controller: GET /api/categories/{id}/deletion-preview
    Controller->>AppService: get_deletion_preview(GetDeletionPreviewQuery)
    
    AppService->>CategoryRepo: find_by_id(category_id)
    CategoryRepo-->>AppService: category
    
    AppService->>DeletionService: can_delete(category_id)
    DeletionService->>CategoryRepo: find_by_id(category_id)
    CategoryRepo-->>DeletionService: category
    DeletionService-->>AppService: is_deletable
    
    AppService->>CategoryRepo: find_by_parent_id(category_id)
    CategoryRepo-->>AppService: subcategories
    
    AppService->>CardCountService: get_card_count(category_id)
    CardCountService-->>AppService: card_count
    
    AppService->>HierarchyService: get_possible_migration_targets(user_id, category_id)
    HierarchyService->>CategoryRepo: find_by_user_id(user_id)
    CategoryRepo-->>HierarchyService: all_categories
    HierarchyService->>HierarchyService: filter_valid_targets(categories, category_id)
    HierarchyService-->>AppService: possible_targets
    
    AppService-->>Controller: DeletionPreviewDto
    Controller-->>Client: DeletionPreviewResponseSchema
```

## 3. 카테고리 삭제 (즉시 처리) 시퀀스 다이어그램

```mermaid
sequenceDiagram
    participant Client
    participant Controller
    participant AppService
    participant DeletionService
    participant CategoryRepo
    participant Category
    participant CardMigrationService
    participant EventPublisher

    Client->>Controller: DELETE /api/categories/{id} {subcategory_target_id}
    Controller->>AppService: delete_category(DeleteCategoryCommand)
    
    AppService->>DeletionService: prepare_deletion(category_id)
    DeletionService->>CategoryRepo: find_by_id(category_id)
    CategoryRepo-->>DeletionService: category
    DeletionService->>CategoryRepo: find_by_parent_id(category_id)
    CategoryRepo-->>DeletionService: subcategories
    DeletionService->>CardMigrationService: get_card_count(category_id)
    CardMigrationService-->>DeletionService: card_count
    DeletionService-->>AppService: DeletionPlan(total_operations < 10)
    
    AppService->>DeletionService: execute_immediate_deletion(plan, target_id)
    
    alt Has Subcategories
        loop For each subcategory
            DeletionService->>Category: move_to_parent(target_id, new_level)
            Category->>Category: _add_domain_event(CategoryMoved)
            DeletionService->>CategoryRepo: save(subcategory)
        end
    end
    
    alt Has Cards
        DeletionService->>CardMigrationService: migrate_cards_from_category(category_id, target_id)
        CardMigrationService-->>DeletionService: migration_result
    end
    
    DeletionService->>CategoryRepo: delete(category_id)
    CategoryRepo-->>DeletionService: deletion_success
    
    DeletionService->>EventPublisher: publish(CategoryDeleted)
    EventPublisher->>Cache: invalidate_user_cache(user_id)
    
    AppService-->>Controller: DeleteCategoryResult(immediate)
    Controller-->>Client: { success: true, data: {}, message: "Category deleted successfully" }
```

## 4. 카테고리 삭제 (백그라운드 처리) 시퀀스 다이어그램

```mermaid
sequenceDiagram
    participant Client
    participant Controller
    participant AppService
    participant DeletionService
    participant CategoryRepo
    participant Category
    participant BackgroundTask
    participant TaskQueue

    Client->>Controller: DELETE /api/categories/{id}
    Controller->>AppService: delete_category(DeleteCategoryCommand)
    
    AppService->>DeletionService: prepare_deletion(category_id)
    DeletionService-->>AppService: DeletionPlan(total_operations >= 10)
    
    AppService->>CategoryRepo: find_by_id(category_id)
    CategoryRepo-->>AppService: category
    AppService->>Category: mark_as_deleting()
    Category->>Category: status = "DELETING"
    AppService->>CategoryRepo: save(category)
    
    AppService->>TaskQueue: schedule_background_deletion(plan, task_id)
    TaskQueue-->>AppService: task_scheduled
    
    AppService-->>Controller: DeleteCategoryResult(background, task_id)
    Controller-->>Client: 202 Accepted + task_id
    
    Note over BackgroundTask: 백그라운드 처리 시작
    
    BackgroundTask->>DeletionService: execute_background_deletion(plan)
    DeletionService->>CategoryRepo: migrate_subcategories(subcategories, target_id)
    DeletionService->>CardMigrationService: migrate_cards(category_id, target_id)
    DeletionService->>CategoryRepo: delete(category_id)
    DeletionService->>EventPublisher: publish(CategoryDeletionCompleted)
```

## 5. 카테고리 이름 수정 시퀀스 다이어그램

```mermaid
sequenceDiagram
    participant Client
    participant Controller
    participant AppService
    participant ValidationService
    participant CategoryRepo
    participant Category
    participant EventPublisher
    participant Cache

    Client->>Controller: PUT /api/categories/{id} {new_name}
    Controller->>AppService: rename_category(RenameCategoryCommand)
    
    AppService->>CategoryRepo: find_by_id(category_id)
    CategoryRepo-->>AppService: category
    
    AppService->>ValidationService: validate_category_name(new_name, parent_id, user_id)
    ValidationService->>CategoryRepo: find_by_name_and_parent(new_name, parent_id, user_id)
    CategoryRepo-->>ValidationService: existing_category
    ValidationService-->>AppService: validation_result
    
    AppService->>Category: rename(new_name)
    Category->>Category: CategoryName(new_name) # 값 객체 검증
    Category->>Category: _add_domain_event(CategoryRenamed)
    Category-->>AppService: renamed_category
    
    AppService->>CategoryRepo: save(category)
    CategoryRepo-->>AppService: saved_category
    
    AppService->>Category: get_domain_events()
    Category-->>AppService: [CategoryRenamed]
    AppService->>EventPublisher: publish_domain_events(events)
    EventPublisher->>Cache: invalidate_user_cache(user_id)
    
    AppService-->>Controller: CategoryDto
    Controller-->>Client: { success: true, data: { category: CategoryResponseSchema }, message: "Category retrieved successfully" }
```

## 6. 시스템 카테고리 자동 생성 시퀀스 다이어그램

```mermaid
sequenceDiagram
    participant UserService
    participant SystemCategoryService
    participant CategoryRepo
    participant Category
    participant EventPublisher

    Note over UserService: 회원가입 완료 이벤트 수신
    
    UserService->>SystemCategoryService: create_shared_cards_category(user_id)
    
    SystemCategoryService->>CategoryRepo: find_system_categories(user_id, SHARED_CARDS)
    CategoryRepo-->>SystemCategoryService: existing_category
    
    alt No Existing Category
        SystemCategoryService->>Category: create_new(user_id, "공유받은 카드", SHARED_CARDS)
        Category->>Category: _add_domain_event(SystemCategoryCreated)
        Category-->>SystemCategoryService: shared_cards_category
        
        SystemCategoryService->>CategoryRepo: save(category)
        CategoryRepo-->>SystemCategoryService: saved_category
        
        SystemCategoryService->>Category: get_domain_events()
        Category-->>SystemCategoryService: [SystemCategoryCreated]
        SystemCategoryService->>EventPublisher: publish_domain_events(events)
    end
    
    SystemCategoryService-->>UserService: category_ready
```

## 7. 값 객체 검증 실패 시퀀스 다이어그램

```mermaid
sequenceDiagram
    participant Client
    participant Controller
    participant AppService
    participant Category
    participant CategoryName
    participant ExceptionHandler

    Client->>Controller: POST /api/categories {name: "너무긴카테고리이름입니다"}
    Controller->>AppService: create_category(command)
    
    AppService->>Category: create_new(user_id, invalid_name)
    Category->>CategoryName: CategoryName(invalid_name)
    CategoryName->>CategoryName: __post_init__() validation
    CategoryName-->>Category: InvalidCategoryNameException
    Category-->>AppService: InvalidCategoryNameException
    
    AppService-->>Controller: InvalidCategoryNameException
    Controller->>ExceptionHandler: handle_domain_exception(exception)
    ExceptionHandler-->>Controller: error_response
    
    Controller-->>Client: 400 Bad Request
    Note over Client: {"error": {"code": "CATEGORY_005", "message": "Category name cannot exceed 10 characters"}}
```

## 9. 개별 카테고리 조회 시퀀스 다이어그램

```mermaid
sequenceDiagram
    participant Client
    participant Controller
    participant AppService
    participant CategoryRepo
    participant CardCountService
    participant Cache

    Client->>Controller: GET /api/categories/{id}
    Controller->>AppService: get_category(GetCategoryQuery)
    
    AppService->>CategoryRepo: find_by_id_and_user_id(category_id, user_id)
    CategoryRepo-->>AppService: category
    
    alt Category Not Found
        AppService-->>Controller: CategoryNotFoundException
        Controller-->>Client: 404 Not Found
    else Category Found
        AppService->>CardCountService: get_card_count_by_category(category_id)
        CardCountService-->>AppService: card_count
        
        AppService->>AppService: build_category_dto(category, card_count)
        AppService-->>Controller: CategoryDto
        Controller-->>Client: { success: true, data: { category: CategoryResponseSchema }, message: "Category retrieved successfully" }
    end
```

## 10. CRUD 오류 처리 시퀀스 다이어그램

```mermaid
sequenceDiagram
    participant Client
    participant Controller
    participant AppService
    participant CategoryRepo
    participant ExceptionHandler

    Client->>Controller: PUT /api/categories/{fake_id} {name}
    Controller->>AppService: rename_category(RenameCategoryCommand)
    
    AppService->>CategoryRepo: find_by_id_and_user_id(fake_id, user_id)
    CategoryRepo-->>AppService: null
    
    AppService-->>Controller: CategoryNotFoundException
    Controller->>ExceptionHandler: handle_application_exception(exception)
    ExceptionHandler-->>Controller: 404 error_response
    
    Controller-->>Client: 404 Not Found
    Note over Client: {"detail": "카테고리를 찾을 수 없습니다: {id}"}
```
