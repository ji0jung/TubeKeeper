# Unit4: Card Search & Display - 도메인 모델

## 1. 도메인 분석 및 이해

### 1.1 사용자 스토리 분석

#### US-007: 메인 화면 카드 목록 표시
- **핵심 기능**: 최신 저장 순서로 카드 목록 조회
- **도메인 개념**: CardList, SortOrder, GridDisplay
- **비즈니스 가치**: 최근 활동 기반 빠른 접근

#### US-008: 카테고리별 필터링
- **핵심 기능**: 특정 카테고리 카드만 필터링
- **도메인 개념**: CategoryFilter, FilteredCardList
- **비즈니스 가치**: 주제별 콘텐츠 분류 조회

#### US-009: 태그 기반 검색
- **핵심 기능**: 단일 태그로 카드 검색
- **도메인 개념**: TagSearch, SingleTagFilter
- **비즈니스 가치**: 관련 주제 빠른 탐색

#### US-010: 내용 기반 검색
- **핵심 기능**: 제목, 요약, 메모에서 키워드 검색
- **도메인 개념**: ContentSearch, KeywordMatching
- **비즈니스 가치**: 기억 기반 콘텐츠 발견

#### US-011: 공개 카드 검색
- **핵심 기능**: 다른 사용자 공개 카드 검색 및 저장
- **도메인 개념**: PublicCardSearch, CardSaving
- **비즈니스 가치**: 새로운 콘텐츠 발견 및 공유

### 1.2 핵심 비즈니스 규칙

#### 검색 범위 분리
- **내 카드 검색**: 카테고리 필터링 + 태그/키워드 검색 가능
- **공개 카드 검색**: 태그 OR 키워드 중 하나만 사용, 카테고리 필터링 없음

#### 태그 검색 제약
- 태그는 단일 선택만 가능
- 공개 카드에서 태그와 키워드 동시 사용 불가

#### 페이징 전략
- **내 카드**: 커서 기반 페이징 (실시간 일관성)
- **공개 카드**: 오프셋 기반 페이징 (관련도 정렬)

#### 공개 카드 저장
- 공개 카드를 내 계정에 저장 시 **완전히 독립적인 새 카드로 복사 생성**
- 기본 카테고리: "공유받은 카드"
- 사용자가 저장 시 카테고리 변경 가능
- 중복 저장 방지
- **원본과 연결 관계 없음**: 원본 소유자의 변경사항 더 이상 반영 안됨
- **완전한 소유권**: 저장 후 내가 자유롭게 수정/삭제 가능

### 1.3 도메인 전문가 언어 (Ubiquitous Language)

#### 핵심 용어 정의
- **Search Query**: 사용자가 입력한 검색 조건
- **Search Scope**: 검색 범위 (내 카드 vs 공개 카드)
- **Content Search**: 제목, 요약, 메모에서 키워드 검색
- **Tag Search**: 태그 기반 검색
- **Category Filter**: 카테고리별 필터링
- **Search Result**: 검색 조건에 맞는 카드 목록
- **Cursor Pagination**: 커서 기반 페이징
- **Offset Pagination**: 오프셋 기반 페이징
- **Public Card**: 다른 사용자가 공개한 카드
- **Card Saving**: 공개 카드를 내 계정에 저장
- **Search Suggestion**: 검색 자동완성 제안
- **Recent Search**: 최근 검색어
- **Popular Tag**: 인기 태그

### 1.4 기존 Unit들과의 연관관계

#### Unit1 (Authentication) 연관성
- **UserId**: 사용자별 검색 범위 제한
- **Session**: 검색 권한 및 개인화

#### Unit2 (Category Management) 연관성
- **CategoryId**: 카테고리 필터링 (내 카드만)
- **SharedCardsCategory**: 공개 카드 저장 시 기본 카테고리

#### Unit3 (Card Creation) 연관성
- **Card Entity**: 검색 대상 엔티티
- **IsPublic**: 공개 카드 여부 판단
- **Tags, Title, Summary, Memo**: 검색 필드
- **CreatedAt**: 정렬 기준

## 2. 전술적 DDD 구성 요소 설계

### 2.1 애그리게이트 설계

#### SearchQueryAggregate
**애그리게이트 루트**: SearchQuery 엔티티
**식별자**: SearchQueryId (UUID)
**책임**: 검색 조건 관리, 검색 범위 제어, 결과 페이징

**경계 내부:**
- SearchQuery (애그리게이트 루트)
- SearchCriteria (값 객체)
- SearchScope (값 객체)
- PaginationInfo (값 객체)

**경계 외부 (참조만):**
- UserId (Unit1에서 관리)
- CategoryId (Unit2에서 관리)
- CardId (Unit3에서 관리)

**불변성 규칙:**
1. **검색 범위 일관성**: SearchScope에 따라 허용되는 SearchCriteria가 달라짐
2. **태그 단일성**: 태그 검색 시 하나의 태그만 선택 가능
3. **공개 카드 제약**: 공개 카드 검색 시 태그 OR 키워드 중 하나만 사용
4. **페이징 일관성**: SearchScope에 따라 페이징 방식이 결정됨

#### SearchResultAggregate
**애그리게이트 루트**: SearchResult 엔티티
**식별자**: SearchResultId (UUID)
**책임**: 검색 결과 관리, 결과 캐싱, 페이징 정보

**경계 내부:**
- SearchResult (애그리게이트 루트)
- CardSummary (엔티티)
- ResultMetadata (값 객체)

**불변성 규칙:**
1. **결과 일관성**: SearchQuery와 일치하는 결과만 포함
2. **페이징 무결성**: 페이징 정보와 실제 결과 수 일치
3. **캐시 유효성**: 검색 조건 변경 시 캐시 무효화

### 2.2 엔티티 설계

#### SearchQuery (애그리게이트 루트)
```
속성:
- SearchQueryId: UUID (식별자)
- UserId: UUID (외부 참조)
- SearchCriteria: SearchCriteria (값 객체)
- SearchScope: SearchScope (값 객체)
- PaginationInfo: PaginationInfo (값 객체)
- CreatedAt: DateTime
- LastUsedAt: DateTime

행위:
- Create(): 새 검색 쿼리 생성
- UpdateCriteria(): 검색 조건 수정
- ChangeScope(): 검색 범위 변경
- UpdatePagination(): 페이징 정보 업데이트
- MarkAsUsed(): 최근 사용 시간 갱신
- Validate(): 검색 조건 유효성 검증
```

#### SearchResult (애그리게이트 루트)
```
속성:
- SearchResultId: UUID (식별자)
- SearchQueryId: UUID (외부 참조)
- CardSummaries: List<CardSummary> (엔티티 컬렉션)
- ResultMetadata: ResultMetadata (값 객체)
- GeneratedAt: DateTime
- ExpiresAt: DateTime

행위:
- Create(): 검색 결과 생성
- AddCard(): 카드 요약 추가
- UpdateMetadata(): 메타데이터 갱신
- IsExpired(): 만료 여부 확인
- GetPage(): 특정 페이지 결과 반환
```

#### CardSummary (엔티티)
```
속성:
- CardId: UUID (식별자)
- Title: string
- Thumbnail: string
- Summary: string
- Tags: List<string>
- CategoryName: string (내 카드만)
- OwnerName: string (공개 카드만)
- IsFavorite: bool (내 카드만)
- IsPublic: bool
- CreatedAt: DateTime

행위:
- UpdateFromCard(): Card 엔티티에서 정보 동기화
- HighlightKeyword(): 키워드 하이라이트 정보 생성
```

### 2.3 값 객체 설계

#### SearchCriteria
```
속성:
- Keyword: string (선택적)
- Tag: string (선택적)
- CategoryId: UUID (선택적, 내 카드만)

제약사항:
- Keyword와 Tag 중 최소 하나는 필수 (공개 카드 검색 시)
- 공개 카드 검색 시 Keyword와 Tag 동시 사용 불가
- CategoryId는 내 카드 검색에서만 사용 가능

메서드:
- IsValid(): boolean
- HasKeyword(): boolean
- HasTag(): boolean
- HasCategoryFilter(): boolean
```

#### SearchScope
```
속성:
- Type: SearchScopeType (MY_CARDS | PUBLIC_CARDS)

메서드:
- IsMyCards(): boolean
- IsPublicCards(): boolean
- AllowsCategoryFilter(): boolean
- GetPaginationType(): PaginationType
```

#### PaginationInfo
```
속성:
- Type: PaginationType (CURSOR | OFFSET)
- Cursor: string (커서 기반 시)
- Page: int (오프셋 기반 시)
- Limit: int
- SortBy: SortOrder

메서드:
- IsCursorBased(): boolean
- IsOffsetBased(): boolean
- GetNextCursor(): string
- GetNextPage(): int
```

#### ResultMetadata
```
속성:
- TotalCount: int (오프셋 기반 시)
- HasMore: bool
- NextCursor: string (커서 기반 시)
- NextPage: int (오프셋 기반 시)
- ProcessingTime: TimeSpan

메서드:
- HasNextPage(): boolean
- GetPaginationInfo(): PaginationInfo
```

### 2.4 도메인 서비스 설계

#### SearchQueryValidationService
```
책임: 검색 쿼리 유효성 검증
메서드:
- ValidateSearchCriteria(criteria, scope): ValidationResult
- ValidateTagSearch(tag): ValidationResult
- ValidateKeywordSearch(keyword): ValidationResult
- ValidateCategoryFilter(categoryId, userId): ValidationResult
```

#### SearchExecutionService
```
책임: 검색 실행 및 결과 생성
메서드:
- ExecuteMyCardSearch(query): SearchResult
- ExecutePublicCardSearch(query): SearchResult
- ApplyCategoryFilter(cards, categoryId): List<Card>
- ApplyTagFilter(cards, tag): List<Card>
- ApplyKeywordFilter(cards, keyword): List<Card>
```

#### SearchSuggestionService
```
책임: 검색 자동완성 제안 생성
메서드:
- GetSuggestions(query, userId, scope): List<SearchSuggestion>
- GetRecentSearches(userId): List<string>
- GetMyCardTags(userId): List<TagSuggestion>
- GetPopularTags(scope): List<TagSuggestion>
```

#### PublicCardSavingService
```
책임: 공개 카드를 내 계정에 완전 독립적으로 복사 저장
메서드:
- SavePublicCardAsCopy(cardId, userId, categoryId?): SaveResult
- CreateIndependentCopy(originalCard, userId, categoryId): Card
- CheckDuplicate(cardId, userId): boolean
- GetDefaultCategory(userId): CategoryId
- ValidateSavePermission(cardId, userId): ValidationResult
```

### 2.5 도메인 이벤트 설계

#### SearchQueryCreated
```
속성: SearchQueryId, UserId, SearchCriteria, SearchScope, OccurredAt
발생 시점: 새로운 검색 쿼리 생성 시
```

#### SearchExecuted
```
속성: SearchQueryId, UserId, ResultCount, ProcessingTime, OccurredAt
발생 시점: 검색 실행 완료 시
```

#### PublicCardSaved
```
속성: OriginalCardId, NewCardId, UserId, CategoryId, SavedAt
발생 시점: 공개 카드를 내 계정에 독립 복사 저장 시
```

#### SearchSuggestionRequested
```
속성: UserId, Query, SearchScope, OccurredAt
발생 시점: 자동완성 제안 요청 시
```

### 2.6 리포지토리 인터페이스 설계

#### ISearchQueryRepository
```
메서드:
- Save(searchQuery): void
- FindById(searchQueryId): SearchQuery
- FindRecentByUser(userId, limit): List<SearchQuery>
- Delete(searchQueryId): void
```

#### ISearchResultRepository
```
메서드:
- Save(searchResult): void
- FindByQueryId(searchQueryId): SearchResult
- FindExpiredResults(): List<SearchResult>
- Delete(searchResultId): void
```

#### ICardSearchRepository
```
메서드:
- SearchMyCards(userId, criteria, pagination): SearchResult
- SearchPublicCards(criteria, pagination): SearchResult
- GetCardSummary(cardId): CardSummary
- CountMyCards(userId, criteria): int
- CountPublicCards(criteria): int
```

#### ISearchSuggestionRepository
```
메서드:
- GetRecentSearches(userId, limit): List<string>
- SaveRecentSearch(userId, query): void
- GetMyCardTags(userId): List<TagSuggestion>
- GetPopularTags(scope, limit): List<TagSuggestion>
```

## 3. 검색 및 필터링 로직 설계

### 3.1 검색 쿼리 모델 설계

#### 내 카드 검색 쿼리
```sql
-- 커서 기반 페이징
SELECT c.id, c.title, c.thumbnail, c.summary, c.tags, 
       cat.name as category_name, c.is_favorite, c.created_at
FROM cards c
LEFT JOIN categories cat ON c.category_id = cat.id
WHERE c.user_id = :userId
  AND c.created_at < :cursor  -- 커서 조건
  AND (:categoryId IS NULL OR c.category_id = :categoryId)
  AND (:keyword IS NULL OR (
    c.title ILIKE '%' || :keyword || '%' OR
    c.summary ILIKE '%' || :keyword || '%' OR
    c.memo ILIKE '%' || :keyword || '%'
  ))
  AND (:tag IS NULL OR :tag = ANY(c.tags))
ORDER BY c.created_at DESC
LIMIT :limit + 1;
```

#### 공개 카드 검색 쿼리
```sql
-- 오프셋 기반 페이징 (관련도 정렬)
SELECT c.id, c.title, c.thumbnail, c.summary, c.tags,
       u.name as owner_name, c.created_at,
       -- 관련도 점수 계산
       CASE 
         WHEN :keyword IS NOT NULL THEN
           ts_rank(to_tsvector('korean', c.title || ' ' || c.summary), 
                   plainto_tsquery('korean', :keyword))
         ELSE 1.0
       END as relevance_score
FROM cards c
JOIN users u ON c.user_id = u.id
WHERE c.is_public = true
  AND c.user_id != :currentUserId  -- 내 카드 제외
  AND (
    (:keyword IS NOT NULL AND (
      to_tsvector('korean', c.title || ' ' || c.summary) @@ 
      plainto_tsquery('korean', :keyword)
    )) OR
    (:tag IS NOT NULL AND :tag = ANY(c.tags))
  )
ORDER BY relevance_score DESC, c.created_at DESC
OFFSET :offset LIMIT :limit;
```

### 3.2 필터링 전략 설계

#### 카테고리 필터링 (내 카드만)
- 계층 구조 고려: 하위 카테고리 포함 검색
- 시스템 카테고리 특별 처리

#### 태그 필터링
- 정확한 매칭: 대소문자 구분 없음
- 단일 태그만 선택 가능

#### 키워드 필터링
- 전문 검색: PostgreSQL Full-text Search 활용
- 검색 대상: 제목, AI 요약, 사용자 메모
- 한국어 형태소 분석 지원

### 3.3 정렬 및 페이징 전략

#### 내 카드 정렬
- 기본: 최신 생성 순 (created_at DESC)
- 즐겨찾기: 즐겨찾기 설정 순 (favorited_at DESC)
- 커서: created_at 또는 favorited_at 기준

#### 공개 카드 정렬
- 기본: 관련도 점수 + 최신 순
- 관련도 계산: PostgreSQL ts_rank 함수 활용
- 페이지: 오프셋 기반 (1페이지당 20개)

### 3.4 검색 성능 최적화 전략

#### 인덱스 설계
```sql
-- 내 카드 검색용 복합 인덱스
CREATE INDEX idx_cards_user_created ON cards(user_id, created_at DESC);
CREATE INDEX idx_cards_user_category ON cards(user_id, category_id, created_at DESC);
CREATE INDEX idx_cards_user_favorite ON cards(user_id, favorited_at DESC) WHERE is_favorite = true;

-- 공개 카드 검색용 인덱스
CREATE INDEX idx_cards_public ON cards(is_public, created_at DESC) WHERE is_public = true;
CREATE INDEX idx_cards_tags_gin ON cards USING gin(tags);

-- 전문 검색용 인덱스
CREATE INDEX idx_cards_fts ON cards USING gin(to_tsvector('korean', title || ' ' || summary));
```

#### 캐싱 전략
- 검색 결과 캐싱: Redis (5분 TTL)
- 자동완성 캐싱: Redis (1시간 TTL)
- 인기 태그 캐싱: Redis (1일 TTL)

## 4. 통합 및 일관성 검토

### 4.1 기존 Unit들과의 일관성

#### Unit1 연동
- 사용자 인증 정보 활용
- 세션 기반 개인화 검색

#### Unit2 연동
- 카테고리 필터링 지원
- "공유받은 카드" 카테고리 활용

#### Unit3 연동
- Card 엔티티 검색 대상
- IsPublic 속성 활용
- 실시간 데이터 동기화

### 4.2 오류 코드 추가

```
SEARCH_001: Invalid search criteria
SEARCH_002: Search query too short
SEARCH_003: Search query too long
SEARCH_004: Invalid tag format
SEARCH_005: Category not accessible
SEARCH_006: Public card not found
SEARCH_007: Card already saved
SEARCH_008: Save permission denied
SEARCH_009: Search service unavailable
SEARCH_010: Invalid pagination parameters
```

---

## 설계 완료 요약

Unit4 도메인 모델 설계가 완료되었습니다:

### 주요 구성 요소
- **2개 애그리게이트**: SearchQuery, SearchResult
- **3개 엔티티**: SearchQuery, SearchResult, CardSummary  
- **4개 값 객체**: SearchCriteria, SearchScope, PaginationInfo, ResultMetadata
- **4개 도메인 서비스**: 검증, 실행, 제안, 저장
- **4개 도메인 이벤트**: 쿼리 생성, 검색 실행, 카드 저장, 제안 요청
- **4개 리포지토리**: 쿼리, 결과, 카드 검색, 제안

### 핵심 특징
- 하이브리드 페이징 전략 (내 카드: 커서, 공개 카드: 오프셋)
- 검색 범위별 제약사항 적용
- 성능 최적화된 인덱스 및 캐싱 전략
- 기존 Unit들과의 완전한 통합
