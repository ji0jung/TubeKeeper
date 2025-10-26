# Unit4: Card Search & Display - 논리적 설계

## 1. 아키텍처 개요

### 1.1 헥사고날 아키텍처 적용

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   REST API      │  │   GraphQL API   │                  │
│  │   Controllers   │  │   (Optional)    │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ Search Service  │  │ Suggestion      │                  │
│  │                 │  │ Service         │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Domain Layer                            │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ SearchQuery     │  │ SearchResult    │                  │
│  │ Aggregate       │  │ Aggregate       │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ PostgreSQL      │  │ Redis Cache     │                  │
│  │ Repository      │  │                 │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 레이어별 책임

#### Presentation Layer
- REST API 엔드포인트 제공
- 요청/응답 변환 (DTO ↔ Domain Model)
- 인증 및 권한 검증
- 입력 유효성 검사

#### Application Layer  
- 비즈니스 유스케이스 조율
- 트랜잭션 관리
- 도메인 서비스 호출
- 이벤트 발행

#### Domain Layer
- 핵심 비즈니스 로직
- 도메인 규칙 및 제약사항
- 애그리게이트 및 엔티티
- 도메인 이벤트

#### Infrastructure Layer
- 데이터 영속성
- 외부 시스템 연동
- 캐싱 구현
- 이벤트 발행/구독

## 2. 애플리케이션 서비스 설계

### 2.1 SearchApplicationService

```python
class SearchApplicationService:
    def __init__(self, 
                 search_query_repo: ISearchQueryRepository,
                 card_search_repo: ICardSearchRepository,
                 cache_service: ICacheService,
                 event_publisher: IEventPublisher):
        self._search_query_repo = search_query_repo
        self._card_search_repo = card_search_repo
        self._cache_service = cache_service
        self._event_publisher = event_publisher
    
    def search_my_cards(self, command: SearchMyCardsCommand) -> SearchMyCardsResult:
        # 1. 검색 쿼리 생성 및 검증
        search_query = SearchQuery.create(
            user_id=command.user_id,
            criteria=SearchCriteria(
                keyword=command.keyword,
                tag=command.tag,
                category_id=command.category_id
            ),
            scope=SearchScope.MY_CARDS,
            pagination=PaginationInfo.cursor_based(
                cursor=command.cursor,
                limit=command.limit
            )
        )
        
        # 2. 캐시 확인
        cache_key = f"search:my:{command.user_id}:{hash(search_query)}"
        cached_result = self._cache_service.get(cache_key)
        if cached_result:
            return cached_result
        
        # 3. 검색 실행
        search_result = self._card_search_repo.search_my_cards(
            user_id=command.user_id,
            criteria=search_query.criteria,
            pagination=search_query.pagination_info
        )
        
        # 4. 결과 캐싱 (3분 TTL)
        self._cache_service.set(cache_key, search_result, ttl=180)
        
        # 5. 이벤트 발행
        self._event_publisher.publish(SearchExecuted(
            search_query_id=search_query.id,
            user_id=command.user_id,
            result_count=len(search_result.card_summaries),
            processing_time=search_result.metadata.processing_time
        ))
        
        return SearchMyCardsResult.from_domain(search_result)
```

### 2.2 PublicCardSearchApplicationService

```python
class PublicCardSearchApplicationService:
    def search_public_cards(self, command: SearchPublicCardsCommand) -> SearchPublicCardsResult:
        # 1. 검색 쿼리 생성 및 검증
        search_query = SearchQuery.create(
            user_id=command.user_id,
            criteria=SearchCriteria(
                keyword=command.keyword,
                tag=command.tag
            ),
            scope=SearchScope.PUBLIC_CARDS,
            pagination=PaginationInfo.offset_based(
                page=command.page,
                limit=command.limit
            )
        )
        
        # 2. 캐시 확인 (5분 TTL)
        cache_key = f"search:public:{hash(search_query)}"
        cached_result = self._cache_service.get(cache_key)
        if cached_result:
            return cached_result
        
        # 3. 검색 실행
        search_result = self._card_search_repo.search_public_cards(
            criteria=search_query.criteria,
            pagination=search_query.pagination_info,
            exclude_user_id=command.user_id
        )
        
        # 4. 결과 캐싱
        self._cache_service.set(cache_key, search_result, ttl=300)
        
        return SearchPublicCardsResult.from_domain(search_result)
    
    def save_public_card(self, command: SavePublicCardCommand) -> SavePublicCardResult:
        # 1. 중복 확인
        if self._card_search_repo.check_duplicate(command.card_id, command.user_id):
            return SavePublicCardResult.already_exists()
        
        # 2. 원본 카드 조회
        original_card = self._card_search_repo.get_public_card(command.card_id)
        if not original_card:
            raise PublicCardNotFoundError()
        
        # 3. 독립적인 새 카드로 복사 생성
        new_card = Card.create_from_public_card(
            original_card=original_card,
            new_owner_id=command.user_id,
            category_id=command.category_id or self._get_default_shared_category(command.user_id)
        )
        
        # 4. 새 카드 저장
        self._card_repo.save(new_card)
        
        # 5. 캐시 무효화 (사용자의 내 카드 검색 캐시)
        self._cache_service.invalidate_pattern(f"search:my:{command.user_id}:*")
        
        # 6. 이벤트 발행
        self._event_publisher.publish(PublicCardSaved(
            original_card_id=command.card_id,
            new_card_id=new_card.id,
            user_id=command.user_id,
            category_id=new_card.category_id
        ))
        
        return SavePublicCardResult.success(new_card)
```
## 3. 인프라스트럭처 설계

### 3.1 PostgreSQL 리포지토리 구현

#### CardSearchRepository
```python
class PostgreSQLCardSearchRepository(ICardSearchRepository):
    def search_my_cards(self, user_id: UUID, criteria: SearchCriteria, 
                       pagination: PaginationInfo) -> SearchResult:
        query = """
        SELECT c.id, c.title, c.thumbnail, c.summary, c.tags, 
               cat.name as category_name, c.is_favorite, c.created_at,
               c.favorited_at
        FROM cards c
        LEFT JOIN categories cat ON c.category_id = cat.id
        WHERE c.user_id = %s
          AND (%s IS NULL OR c.created_at < %s)  -- 커서 조건
          AND (%s IS NULL OR c.category_id = %s)
          AND (%s IS NULL OR (
            c.title ILIKE %s OR
            c.summary ILIKE %s OR
            c.memo ILIKE %s
          ))
          AND (%s IS NULL OR %s = ANY(c.tags))
        ORDER BY c.created_at DESC
        LIMIT %s
        """
        
    def search_public_cards(self, criteria: SearchCriteria, 
                           pagination: PaginationInfo, 
                           exclude_user_id: UUID) -> SearchResult:
        query = """
        SELECT c.id, c.title, c.thumbnail, c.summary, c.tags,
               u.name as owner_name, c.created_at,
               -- 관련도 점수 계산 (제목과 요약만 사용)
               CASE 
                 WHEN %s IS NOT NULL THEN
                   ts_rank(to_tsvector('korean', c.title || ' ' || c.summary), 
                           plainto_tsquery('korean', %s))
                 ELSE 1.0
               END as relevance_score
        FROM cards c
        JOIN users u ON c.user_id = u.id
        WHERE c.is_public = true
          AND c.user_id != %s
          AND (
            (%s IS NOT NULL AND (
              to_tsvector('korean', c.title || ' ' || c.summary) @@ 
              plainto_tsquery('korean', %s)
            )) OR
            (%s IS NOT NULL AND %s = ANY(c.tags))
          )
        ORDER BY relevance_score DESC, c.created_at DESC
        OFFSET %s LIMIT %s
        """
```

### 3.2 Redis 캐싱 전략

#### 캐싱 키 전략
```
# 내 카드 검색: 3분 TTL + 변경시 무효화
search:my:{user_id}:{criteria_hash}:{pagination_hash}

# 공개 카드 검색: 5분 TTL
search:public:{criteria_hash}:{pagination_hash}

# 검색 제안: 1시간 TTL
suggestions:my:{user_id}:{query_hash}
suggestions:public:{query_hash}

# 인기 태그: 1일 TTL
tags:popular:my:{user_id}
tags:popular:public
```

#### CacheService 구현
```python
class RedisCacheService(ICacheService):
    def invalidate_user_search_cache(self, user_id: UUID):
        """사용자가 카드를 변경했을 때 호출"""
        pattern = f"search:my:{user_id}:*"
        self.invalidate_pattern(pattern)
```

### 3.3 검색 인덱스 최적화

```sql
-- 내 카드 검색용 복합 인덱스
CREATE INDEX idx_cards_user_created ON cards(user_id, created_at DESC);
CREATE INDEX idx_cards_user_category_created ON cards(user_id, category_id, created_at DESC);
CREATE INDEX idx_cards_user_favorite ON cards(user_id, favorited_at DESC) 
WHERE is_favorite = true;

-- 공개 카드 검색용 인덱스
CREATE INDEX idx_cards_public_created ON cards(is_public, created_at DESC) 
WHERE is_public = true;

-- 태그 검색용 GIN 인덱스
CREATE INDEX idx_cards_tags_gin ON cards USING gin(tags);

-- 전문 검색용 GIN 인덱스 (제목과 요약만)
CREATE INDEX idx_cards_fts_title_summary ON cards 
USING gin(to_tsvector('korean', title || ' ' || summary));
```

## 4. API 설계

### 4.1 요청/응답 DTO

#### 내 카드 검색 DTO
```python
class SearchMyCardsRequest(BaseModel):
    cursor: Optional[str] = None
    limit: int = Field(20, ge=1, le=100)
    category_id: Optional[UUID] = None
    search: Optional[str] = None
    tag: Optional[str] = None

class MyCardsResponse(BaseModel):
    cards: List[CardSummaryDTO]
    next_cursor: Optional[str]
    has_more: bool

class CardSummaryDTO(BaseModel):
    id: UUID
    title: str
    thumbnail: str
    summary: str
    tags: List[str]
    category_name: Optional[str]
    is_favorite: bool
    created_at: datetime
```

#### 공개 카드 검색 DTO
```python
class SearchPublicCardsRequest(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)
    search: Optional[str] = None
    tag: Optional[str] = None
    
    @validator('search', 'tag')
    def validate_search_or_tag(cls, v, values):
        # search와 tag 동시 사용 금지
        if values.get('search') and v and 'tag' in values:
            raise ValueError('Cannot use both search and tag')
        return v

class PublicCardsResponse(BaseModel):
    cards: List[PublicCardSummaryDTO]
    total_count: int
    current_page: int
    total_pages: int

class PublicCardSummaryDTO(BaseModel):
    id: UUID
    title: str
    thumbnail: str
    summary: str
    tags: List[str]
    owner_name: str
    created_at: datetime
```

#### 공개 카드 저장 DTO
```python
class SavePublicCardRequest(BaseModel):
    category_id: Optional[UUID] = None

class SavePublicCardResponse(BaseModel):
    success: bool
    new_card: Optional[CardSummaryDTO] = None
    already_exists: bool = False
    message: str
```

### 4.2 검색 제안 API

```python
class SearchSuggestionsResponse(BaseModel):
    suggestions: List[SearchSuggestionDTO]

class SearchSuggestionDTO(BaseModel):
    type: str  # 'recent', 'my_tag', 'popular_tag'
    value: str
    count: Optional[int] = None

@router.get("/api/search/suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=1),
    scope: str = Query('my', regex='^(my|public)$'),
    current_user: User = Depends(get_current_user)
) -> SearchSuggestionsResponse:
    
    command = GetSearchSuggestionsCommand(
        user_id=current_user.id,
        query=query,
        scope=SearchScope.from_string(scope)
    )
    
    result = await suggestion_service.get_suggestions(command)
    
## 4. API 설계 (표준 응답 형식)

### 4.1 REST API 엔드포인트

#### 내 카드 검색 API
```python
@router.get("/my-cards")
async def search_my_cards(
    cursor: Optional[str] = None,
    limit: int = 20,
    category_id: Optional[UUID] = None,
    search: Optional[str] = None,
    tag: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> StandardResponse:
    """내 카드 검색 (커서 기반 페이징)"""
    try:
        result = await search_service.search_my_cards(
            SearchMyCardsCommand(
                user_id=current_user.id,
                cursor=cursor,
                limit=limit,
                category_id=category_id,
                keyword=search,
                tag=tag
            )
        )
        
        return StandardResponse.success_response(
            data=MyCardsResponse(
                cards=[CardSummaryResponse.from_domain(card) for card in result.cards],
                nextCursor=result.next_cursor,
                hasMore=result.has_more
            ),
            message="Success"
        )
    except ValidationError as e:
        return StandardResponse.error_response("SEARCH_001", str(e))
    except Exception as e:
        return StandardResponse.error_response("SEARCH_009", "Search service unavailable")
```

#### 공개 카드 검색 API
```python
@router.get("/public-cards")
async def search_public_cards(
    page: int = 1,
    limit: int = 20,
    search: Optional[str] = None,
    tag: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> StandardResponse:
    """공개 카드 검색 (오프셋 기반 페이징)"""
    try:
        result = await search_service.search_public_cards(
            SearchPublicCardsCommand(
                user_id=current_user.id,
                page=page,
                limit=limit,
                keyword=search,
                tag=tag
            )
        )
        
        return StandardResponse.success_response(
            data=PublicCardsResponse(
                cards=[CardSummaryResponse.from_domain(card) for card in result.cards],
                totalCount=result.total_count,
                currentPage=page,
                totalPages=result.total_pages
            ),
            message="Success"
        )
    except ValidationError as e:
        return StandardResponse.error_response("SEARCH_001", str(e))
```

#### 공개 카드 저장 API
```python
@router.post("/public-cards/{card_id}/save")
async def save_public_card(
    card_id: UUID,
    request: SavePublicCardRequest,
    current_user: User = Depends(get_current_user)
) -> StandardResponse:
    """공개 카드를 내 계정에 저장"""
    try:
        result = await search_service.save_public_card(
            SavePublicCardCommand(
                card_id=card_id,
                user_id=current_user.id,
                category_id=request.category_id
            )
        )
        
        if result.already_exists:
            return StandardResponse.success_response(
                data=SavePublicCardResponse(alreadyExists=True),
                message="Card already exists in your collection"
            )
        
        return StandardResponse.success_response(
            data=SavePublicCardResponse(
                newCard=CardSummaryResponse.from_domain(result.new_card),
                alreadyExists=False
            ),
            message="Card saved successfully"
        )
    except PublicCardNotFoundError:
        return StandardResponse.error_response("SEARCH_006", "Public card not found")
    except DuplicateCardError:
        return StandardResponse.error_response("SEARCH_007", "Card already saved")
```
```

## 5. 성능 최적화 설계

### 5.1 쿼리 최적화 전략

#### 커서 기반 페이징 최적화
- `created_at` 기준 내림차순 정렬로 최신 데이터 우선
- 복합 인덱스 활용으로 `WHERE` + `ORDER BY` 최적화
- `LIMIT + 1` 방식으로 `has_more` 판단

#### 전문 검색 최적화
- PostgreSQL Full-text Search 활용
- 한국어 형태소 분석 지원
- `ts_rank` 함수로 관련도 점수 계산

### 5.2 캐싱 최적화

#### 계층적 캐싱 전략
1. **L1 Cache**: 애플리케이션 메모리 (자주 사용되는 검색 결과)
2. **L2 Cache**: Redis (검색 결과, 자동완성)
3. **L3 Cache**: PostgreSQL 쿼리 캐시

#### 캐시 무효화 전략
- **즉시 무효화**: 사용자가 직접 변경한 경우
- **TTL 기반**: 다른 사용자 변경사항 반영
- **패턴 기반**: 사용자별 캐시 일괄 무효화

## 6. 보안 및 권한 설계

### 6.1 인증 통합
- JWT 토큰 기반 사용자 인증
- Unit1 Authentication Service와 연동
- 모든 API 엔드포인트에 인증 필수

### 6.2 권한 제어
- **내 카드 검색**: 본인 카드만 접근 가능
- **공개 카드 검색**: 공개 설정된 카드만 접근
- **카드 저장**: 공개 카드를 본인 계정에만 저장 가능

### 6.3 입력 검증
- 검색어 길이 제한 (1-100자)
- SQL Injection 방지 (파라미터 바인딩)
- XSS 방지 (입력값 이스케이프)
