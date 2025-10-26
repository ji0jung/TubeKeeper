# Unit 2: Category Management 도메인 모델

## 1. 도메인 이해 및 분석

### 1.1 사용자 스토리 분석

#### US-015: 카테고리 생성 및 관리
- **핵심 기능**: 카테고리 CRUD 작업
- **도메인 개념**: Category, CategoryName, CategoryHierarchy
- **비즈니스 가치**: 체계적인 분류 체계 구축

#### US-016: 카테고리 삭제 시 안전장치
- **핵심 기능**: 안전한 카테고리 삭제 프로세스
- **도메인 개념**: CategoryDeletion, CardMigration, TemporaryCategory
- **비즈니스 가치**: 데이터 손실 방지

#### US-021: 공유받은 카드 카테고리 자동 생성
- **핵심 기능**: 시스템 카테고리 자동 생성
- **도메인 개념**: SharedCardsCategory, SystemCategory
- **비즈니스 가치**: 공유 카드 자동 분류

### 1.2 비즈니스 규칙 및 제약사항

#### 카테고리 구조 규칙
- 최대 3계층의 계층 구조 지원
- 사용자당 최대 100개 카테고리 (시스템 카테고리 포함)
- 카테고리 이름: 최대 10글자, 영어/숫자/한글/밑줄(_)만 허용, 띄어쓰기 금지, 동일 계층 내 중복 불가

#### 카테고리 유형별 규칙
- **일반 카테고리**: 생성/수정/삭제 가능, 계층 구조 지원
- **공유받은 카드 카테고리**: 회원가입 시 자동 생성, 삭제/이름변경 불가, 최상위 계층
- **임시 카테고리**: 카테고리 삭제 시 자동 생성, 최상위 계층

#### 카테고리 삭제 규칙
- 빈 카테고리만 직접 삭제 가능
- 카드가 있는 카테고리 삭제 시 카드 이동 필수
- 카드 이동 방식: 자동(임시 카테고리) 또는 수동(사용자 선택)
- 하위 카테고리가 있는 경우 삭제 불가

### 1.3 도메인 전문가 언어 (Ubiquitous Language)

#### 핵심 용어
- **Category (카테고리)**: 카드를 분류하기 위한 논리적 그룹
- **Category Hierarchy (카테고리 계층)**: 카테고리 간의 부모-자식 관계 구조
- **Category Path (카테고리 경로)**: 루트부터 특정 카테고리까지의 전체 경로
- **System Category (시스템 카테고리)**: 시스템에서 자동 생성/관리하는 특수 카테고리
- **Regular Category (일반 카테고리)**: 사용자가 직접 생성/관리하는 카테고리

#### 특수 카테고리
- **Shared Cards Category (공유받은 카드 카테고리)**: 공유받은 카드들이 저장되는 시스템 카테고리
- **Temporary Category (임시 카테고리)**: 카테고리 삭제 시 카드들이 임시로 이동되는 카테고리

#### 프로세스 용어
- **Category Migration (카테고리 이동)**: 카테고리를 다른 부모 카테고리 하위로 이동
- **Card Migration (카드 이동)**: 카드를 다른 카테고리로 이동
- **Safe Deletion (안전 삭제)**: 카드가 있는 카테고리의 안전한 삭제 프로세스
- **Auto Migration (자동 이동)**: 시스템이 자동으로 수행하는 카드 이동
- **Manual Migration (수동 이동)**: 사용자가 직접 선택하는 카드 이동

#### 제약 용어
- **Hierarchy Level (계층 레벨)**: 카테고리의 깊이 (1~3)
- **Category Limit (카테고리 제한)**: 사용자당 최대 카테고리 수 (100개)
- **Name Constraint (이름 제약)**: 카테고리 이름 규칙 (10글자, 영어/숫자/한글/밑줄만 허용, 띄어쓰기 금지, 중복 금지)

## 2. 전술적 설계 - 핵심 도메인 객체

### 2.1 애그리게이트 루트

#### CategoryAggregate
- **책임**: 카테고리 계층 구조의 일관성 보장 및 비즈니스 규칙 적용
- **경계**: 단일 사용자의 모든 카테고리와 그들 간의 계층 관계
- **식별자**: UserId (사용자별로 하나의 애그리게이트)

### 2.2 엔티티

#### Category
- **식별자**: CategoryId (UUID)
- **속성**:
  - CategoryName (값 객체)
  - CategoryType (값 객체)
  - ParentCategoryId (선택적)
  - HierarchyLevel (값 객체)
  - CreatedAt
  - UpdatedAt
  - CardCount (읽기 전용)
- **불변식**: 
  - 계층 레벨은 1~3 사이
  - 동일 부모 하위에서 이름 중복 불가
  - 시스템 카테고리는 수정/삭제 불가

### 2.3 값 객체

#### CategoryName
- **속성**: value (string)
- **제약사항**: 
  - 1~10글자
  - 영어/숫자/한글/밑줄(_)만 허용
  - 띄어쓰기 금지
- **불변성**: 생성 후 변경 불가

#### CategoryType
- **열거값**: 
  - REGULAR (일반 카테고리)
  - SHARED_CARDS (공유받은 카드)
  - TEMPORARY (임시)
- **불변성**: 생성 후 변경 불가

#### HierarchyLevel
- **속성**: level (int)
- **제약사항**: 1~3 사이의 값
- **불변성**: 값 객체 자체는 불변이지만, 카테고리 이동 시 새로운 객체로 교체됨

#### CategoryPath
- **속성**: pathSegments (List<CategoryName>)
- **책임**: 루트부터 현재 카테고리까지의 전체 경로 표현
- **불변성**: 값 객체 자체는 불변이지만, 카테고리 이동 시 새로운 객체로 교체됨

### 2.4 도메인 이벤트

#### CategoryCreated
- **속성**: CategoryId, CategoryName, CategoryType, ParentCategoryId, UserId, OccurredAt
- **발생 시점**: 새 카테고리 생성 시

#### CategoryRenamed
- **속성**: CategoryId, OldName, NewName, UserId, OccurredAt
- **발생 시점**: 카테고리 이름 변경 시

#### CategoryMoved
- **속성**: CategoryId, OldParentId, NewParentId, UserId, OccurredAt
- **발생 시점**: 카테고리가 다른 부모로 이동 시

#### CategoryDeleted
- **속성**: CategoryId, CategoryName, ParentCategoryId, UserId, OccurredAt
- **발생 시점**: 카테고리 삭제 시

#### SystemCategoryCreated
- **속성**: CategoryId, CategoryType, UserId, OccurredAt
- **발생 시점**: 시스템 카테고리 자동 생성 시

#### CardsAutoMigrated
- **속성**: SourceCategoryId, TargetCategoryId, CardIds, UserId, OccurredAt
- **발생 시점**: 카테고리 삭제로 인한 카드 자동 이동 시

#### CardsManuallyMigrated
- **속성**: SourceCategoryId, MigrationMap (CardId -> CategoryId), UserId, OccurredAt
- **발생 시점**: 사용자가 수동으로 카드 이동 시

## 3. 전술적 설계 - 도메인 서비스 및 정책

### 3.1 도메인 서비스

#### CategoryHierarchyService
- **책임**: 카테고리 계층 구조 관리 및 검증
- **메서드**:
  - `validateHierarchyMove(categoryId, newParentId)`: 계층 이동 가능성 검증
  - `calculateNewHierarchyLevel(parentId)`: 새로운 계층 레벨 계산
  - `buildCategoryPath(categoryId)`: 카테고리 경로 생성
  - `findDescendants(categoryId)`: 하위 카테고리 조회

#### CategoryDeletionService
- **책임**: 안전한 카테고리 삭제 프로세스 관리
- **메서드**:
  - `canDelete(categoryId)`: 삭제 가능 여부 확인
  - `prepareAutoMigration(categoryId)`: 자동 이동 준비
  - `prepareManualMigration(categoryId)`: 수동 이동 준비
  - `executeCardMigration(migrationPlan)`: 카드 이동 실행

#### SystemCategoryService
- **책임**: 시스템 카테고리 생성 및 관리
- **메서드**:
  - `createSharedCardsCategory(userId)`: 공유받은 카드 카테고리 생성
  - `ensureTemporaryCategory(userId)`: 임시 카테고리 확보
  - `isSystemCategory(categoryId)`: 시스템 카테고리 여부 확인

#### CategoryValidationService
- **책임**: 카테고리 생성/수정 시 비즈니스 규칙 검증
- **메서드**:
  - `validateCategoryName(name, parentId, userId)`: 이름 유효성 검증
  - `validateCategoryLimit(userId)`: 카테고리 수 제한 검증
  - `validateHierarchyConstraints(parentId)`: 계층 제약 검증

### 3.2 비즈니스 정책 및 규칙

#### CategoryCreationPolicy
- 사용자당 최대 100개 카테고리 제한
- 카테고리 이름은 동일 부모 하위에서 중복 불가
- 최대 3계층까지만 생성 가능
- 시스템 카테고리는 사용자가 직접 생성 불가

#### CategoryNamingPolicy
- 1~10글자 제한
- 영어, 숫자, 한글, 밑줄(_)만 허용
- 띄어쓰기 및 특수문자 금지
- 빈 문자열 또는 공백만으로 구성된 이름 금지

#### CategoryDeletionPolicy
- 빈 카테고리만 직접 삭제 가능
- 시스템 카테고리는 삭제 불가
- 하위 카테고리가 있는 경우 삭제 불가
- 카드가 있는 경우 이동 후 삭제 가능

#### CategoryHierarchyPolicy
- 순환 참조 방지 (자신의 하위 카테고리로 이동 불가)
- 3계층 초과 이동 불가
- 시스템 카테고리는 최상위 계층에만 위치

#### CardMigrationPolicy
- 자동 이동: 임시 카테고리로 일괄 이동
- 수동 이동: 사용자가 카드별로 대상 카테고리 선택
- 이동 대상 카테고리는 존재하고 접근 가능해야 함
- 공유받은 카드는 일반 카테고리로 이동 시 소유권 변경

### 3.3 애그리게이트 경계

#### CategoryAggregate 경계
- **포함**: 
  - 단일 사용자의 모든 Category 엔티티
  - 카테고리 간 계층 관계
  - 카테고리별 카드 수 정보
- **제외**:
  - 실제 Card 엔티티 (다른 애그리게이트)
  - 다른 사용자의 카테고리
  - 카드의 상세 정보

#### 트랜잭션 경계
- 카테고리 생성/수정/삭제는 단일 트랜잭션
- 카드 이동은 별도 트랜잭션 (Card 애그리게이트와 협력)
- 계층 구조 변경은 영향받는 모든 하위 카테고리 포함

#### 일관성 규칙
- 강한 일관성: 동일 애그리게이트 내 카테고리 계층 구조
- 최종 일관성: 카테고리와 카드 간의 관계 (이벤트 기반)

## 4. 인프라스트럭처 설계

### 4.1 리포지토리 인터페이스

#### CategoryRepository
- **책임**: Category 애그리게이트의 영속성 관리
- **메서드**:
  - `findByUserId(userId)`: 사용자의 모든 카테고리 조회
  - `findById(categoryId)`: 특정 카테고리 조회
  - `findByIdAndUserId(categoryId, userId)`: 사용자별 카테고리 조회 (권한 검증)
  - `findByParentId(parentId)`: 특정 부모의 하위 카테고리 조회
  - `findByNameAndParent(name, parentId, userId)`: 이름과 부모로 카테고리 검색
  - `findSystemCategories(userId, categoryType)`: 시스템 카테고리 조회
  - `save(category)`: 카테고리 저장
  - `delete(categoryId)`: 카테고리 삭제
  - `countByUserId(userId)`: 사용자의 카테고리 수 조회
  - `findDescendants(categoryId)`: 하위 카테고리 재귀 조회

#### CategoryQueryRepository (읽기 전용)
- **책임**: 카테고리 조회 최적화
- **메서드**:
  - `findCategoryTree(userId)`: 계층 구조 트리 조회
  - `findCategoryWithCardCount(userId)`: 카드 수 포함 카테고리 목록
  - `findCategoriesForDropdown(userId)`: 드롭다운용 카테고리 목록
  - `searchCategories(userId, searchTerm)`: 카테고리 검색

### 4.2 외부 서비스 인터페이스

#### CardCountService
- **책임**: 카테고리별 카드 수 조회 (Card 애그리게이트와 협력)
- **메서드**:
  - `getCardCount(categoryId)`: 특정 카테고리의 카드 수
  - `getCardCountByCategory(categoryId)`: 개별 카테고리 조회용 카드 수
  - `getCardCounts(categoryIds)`: 여러 카테고리의 카드 수 일괄 조회
  - `hasCards(categoryId)`: 카테고리에 카드 존재 여부

#### CardMigrationService
- **책임**: 카드 이동 처리 (Card 애그리게이트와 협력)
- **메서드**:
  - `moveCardsToCategory(cardIds, targetCategoryId)`: 카드 일괄 이동
  - `moveCardsByCategory(sourceCategoryId, targetCategoryId)`: 카테고리별 카드 이동
  - `getCardsInCategory(categoryId)`: 카테고리 내 카드 목록

#### EventPublisher
- **책임**: 도메인 이벤트 발행
- **메서드**:
  - `publish(domainEvent)`: 도메인 이벤트 발행
  - `publishBatch(domainEvents)`: 도메인 이벤트 일괄 발행

### 4.3 데이터 모델 (DynamoDB)

#### Category 테이블
```
PK: USER#{userId}
SK: CATEGORY#{categoryId}
GSI1PK: USER#{userId}#PARENT#{parentId}
GSI1SK: CATEGORY#{categoryName}

Attributes:
- categoryId (String)
- categoryName (String)
- categoryType (String)
- parentCategoryId (String, optional)
- hierarchyLevel (Number)
- createdAt (String, ISO timestamp)
- updatedAt (String, ISO timestamp)
- isSystemCategory (Boolean)
```

#### CategoryHierarchy 테이블 (계층 구조 최적화)
```
PK: USER#{userId}
SK: PATH#{categoryPath}

Attributes:
- categoryId (String)
- fullPath (String)
- level (Number)
- parentIds (List<String>)
```

## 5. 통합 및 검증

### 5.1 Integration Contract 일관성 검증

#### API 엔드포인트 매핑
- `GET /api/categories` → CategoryQueryRepository.findCategoryWithCardCount()
- `POST /api/categories` → CategoryAggregate.createCategory()
- `PUT /api/categories/:id` → CategoryAggregate.renameCategory()
- `DELETE /api/categories/:id` → CategoryDeletionService.executeDelete()

#### 응답 데이터 구조 일치 확인
- `{ id, name, cardCount, isDeletable }` 형식과 도메인 모델 일치
- isDeletable은 CategoryDeletionService.canDelete() 결과 반영

### 5.2 추가된 오류 코드

integration_contract.md에 다음 오류 코드 추가 완료:

```
CATEGORY_003: Category name already exists
CATEGORY_004: Category limit exceeded
CATEGORY_005: Invalid category name format
CATEGORY_006: Cannot delete system category
CATEGORY_007: Cannot move to descendant category
CATEGORY_008: Maximum hierarchy level exceeded
CATEGORY_009: Cannot delete category with subcategories
```

### 5.3 도메인 모델 완성도 검증

#### 사용자 스토리 커버리지
- ✅ US-015: 카테고리 CRUD → Category 애그리게이트, CategoryRepository
- ✅ US-016: 안전 삭제 → CategoryDeletionService, CardMigrationService  
- ✅ US-021: 자동 생성 → SystemCategoryService

#### 비즈니스 규칙 구현
- ✅ 계층 구조 (3레벨) → HierarchyLevel, CategoryHierarchyService
- ✅ 이름 제약 → CategoryName, CategoryNamingPolicy
- ✅ 카테고리 제한 → CategoryValidationService
- ✅ 시스템 카테고리 → CategoryType, SystemCategoryService

---

## 도메인 모델 설계 완료

Unit 2: Category Management의 도메인 모델 설계가 완료되었습니다.

### 핵심 설계 결과
- **애그리게이트**: CategoryAggregate (사용자별 카테고리 계층 관리)
- **엔티티**: Category (카테고리 정보 및 계층 관계)
- **값 객체**: CategoryName, CategoryType, HierarchyLevel, CategoryPath
- **도메인 서비스**: 4개 (계층관리, 삭제, 시스템카테고리, 검증)
- **도메인 이벤트**: 7개 (생성, 수정, 삭제, 이동, 카드이동 관련)

### 주요 비즈니스 규칙 반영
- 3계층 계층 구조 지원
- 카테고리 이름 제약 (10글자, 영어/숫자/한글/밑줄만)
- 시스템 카테고리 특별 관리
- 안전한 카테고리 삭제 프로세스
