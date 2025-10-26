# Unit4: Card Search & Display - 시퀀스 다이어그램

## 1. 내 카드 검색 시퀀스

```mermaid
sequenceDiagram
    participant Client
    participant API as MyCardsController
    participant App as SearchApplicationService
    participant Cache as RedisCacheService
    participant Repo as CardSearchRepository
    participant DB as PostgreSQL
    participant Event as EventPublisher

    Client->>API: GET /api/my-cards?search=keyword&cursor=abc
    API->>API: 인증 및 입력 검증
    API->>App: SearchMyCardsCommand
    
    App->>App: SearchQuery 생성 및 검증
    App->>Cache: get(cache_key)
    
    alt 캐시 히트
        Cache-->>App: cached_result
        App-->>API: SearchMyCardsResult
    else 캐시 미스
        App->>Repo: search_my_cards(user_id, criteria, pagination)
        Repo->>DB: SELECT with cursor pagination
        DB-->>Repo: card_summaries
        Repo-->>App: SearchResult
        
        App->>Cache: set(cache_key, result, ttl=180)
        App->>Event: publish(SearchExecuted)
        App-->>API: SearchMyCardsResult
    end
    
    API->>API: DTO 변환
    API-->>Client: MyCardsResponse
```

## 2. 공개 카드 검색 시퀀스

```mermaid
sequenceDiagram
    participant Client
    participant API as PublicCardsController
    participant App as PublicCardSearchApplicationService
    participant Cache as RedisCacheService
    participant Repo as CardSearchRepository
    participant DB as PostgreSQL

    Client->>API: GET /api/public-cards?search=keyword&page=1
    API->>API: 인증 및 입력 검증 (search/tag 중복 금지)
    API->>App: SearchPublicCardsCommand
    
    App->>App: SearchQuery 생성 및 검증
    App->>Cache: get(cache_key)
    
    alt 캐시 히트
        Cache-->>App: cached_result
        App-->>API: SearchPublicCardsResult
    else 캐시 미스
        App->>Repo: search_public_cards(criteria, pagination, exclude_user_id)
        Repo->>DB: SELECT with relevance scoring & offset pagination
        DB-->>Repo: public_card_summaries
        Repo-->>App: SearchResult
        
        App->>Cache: set(cache_key, result, ttl=300)
        App-->>API: SearchPublicCardsResult
    end
    
    API->>API: DTO 변환
    API-->>Client: PublicCardsResponse
```

## 3. 공개 카드 저장 시퀀스

```mermaid
sequenceDiagram
    participant Client
    participant API as PublicCardsController
    participant App as PublicCardSearchApplicationService
    participant SearchRepo as CardSearchRepository
    participant CardRepo as CardRepository
    participant Cache as RedisCacheService
    participant Event as EventPublisher
    participant DB as PostgreSQL

    Client->>API: POST /api/public-cards/{id}/save
    API->>API: 인증 및 입력 검증
    API->>App: SavePublicCardCommand
    
    App->>SearchRepo: check_duplicate(card_id, user_id)
    SearchRepo->>DB: SELECT COUNT(*) WHERE original_card_id = ? AND user_id = ?
    DB-->>SearchRepo: count
    SearchRepo-->>App: duplicate_exists
    
    alt 중복 존재
        App-->>API: SavePublicCardResult.already_exists()
        API-->>Client: SavePublicCardResponse(already_exists=true)
    else 중복 없음
        App->>SearchRepo: get_public_card(card_id)
        SearchRepo->>DB: SELECT * FROM cards WHERE id = ? AND is_public = true
        DB-->>SearchRepo: original_card
        SearchRepo-->>App: original_card
        
        alt 카드 없음
            App-->>API: PublicCardNotFoundError
            API-->>Client: 404 Not Found
        else 카드 존재
            App->>App: Card.create_from_public_card(original, new_owner, category)
            App->>CardRepo: save(new_card)
            CardRepo->>DB: INSERT INTO cards (새 카드 데이터)
            DB-->>CardRepo: success
            CardRepo-->>App: success
            
            App->>Cache: invalidate_pattern(f"search:my:{user_id}:*")
            App->>Event: publish(PublicCardSaved)
            App-->>API: SavePublicCardResult.success(new_card)
            API-->>Client: SavePublicCardResponse(success=true, new_card=...)
        end
    end
```

## 4. 검색 제안 시퀀스

```mermaid
sequenceDiagram
    participant Client
    participant API as SearchController
    participant App as SearchSuggestionApplicationService
    participant Cache as RedisCacheService
    participant Repo as SearchSuggestionRepository
    participant DB as PostgreSQL

    Client->>API: GET /api/search/suggestions?query=key&scope=my
    API->>API: 인증 및 입력 검증
    API->>App: GetSearchSuggestionsCommand
    
    App->>Cache: get(suggestions_cache_key)
    
    alt 캐시 히트
        Cache-->>App: cached_suggestions
        App-->>API: SearchSuggestionsResult
    else 캐시 미스
        par 최근 검색어 조회
            App->>Repo: get_recent_searches(user_id, limit=3)
            Repo->>DB: SELECT FROM recent_searches WHERE user_id = ? ORDER BY created_at DESC LIMIT 3
            DB-->>Repo: recent_searches
            Repo-->>App: recent_searches
        and 내 카드 태그 조회
            App->>Repo: get_my_card_tags(user_id, query_prefix, limit=4)
            Repo->>DB: SELECT DISTINCT unnest(tags) FROM cards WHERE user_id = ? AND tag ILIKE ?
            DB-->>Repo: my_tags
            Repo-->>App: my_tags
        and 인기 태그 조회
            App->>Repo: get_popular_tags(scope, query_prefix, limit=3)
            Repo->>DB: SELECT tag, COUNT(*) FROM cards WHERE is_public = true AND tag ILIKE ? GROUP BY tag ORDER BY COUNT(*) DESC
            DB-->>Repo: popular_tags
            Repo-->>App: popular_tags
        end
        
        App->>App: 제안 목록 조합 및 우선순위 정렬
        App->>Cache: set(suggestions_cache_key, suggestions, ttl=3600)
        App-->>API: SearchSuggestionsResult
    end
    
    API->>API: DTO 변환
    API-->>Client: SearchSuggestionsResponse
```

## 5. 캐시 무효화 시퀀스

```mermaid
sequenceDiagram
    participant CardService as Unit3 CardService
    participant Event as EventPublisher
    participant Handler as SearchCacheInvalidationHandler
    participant Cache as RedisCacheService

    Note over CardService: 사용자가 카드 생성/수정/삭제
    
    CardService->>Event: publish(CardCreated/Updated/Deleted)
    Event->>Handler: handle_card_event(event)
    
    Handler->>Cache: invalidate_user_search_cache(user_id)
    Cache->>Cache: keys(f"search:my:{user_id}:*")
    Cache->>Cache: delete(matching_keys)
    
    Note over Cache: 사용자의 모든 검색 캐시 무효화 완료
```

## 6. 오류 처리 시퀀스

```mermaid
sequenceDiagram
    participant Client
    participant API as Controller
    participant App as ApplicationService
    participant Repo as Repository
    participant DB as PostgreSQL

    Client->>API: 잘못된 검색 요청
    API->>API: 입력 검증 실패
    
    alt 검증 오류
        API-->>Client: 400 Bad Request (SEARCH_001: Invalid search criteria)
    else 서비스 오류
        API->>App: 유효한 요청
        App->>Repo: 데이터베이스 조회
        Repo->>DB: SQL 쿼리 실행
        DB-->>Repo: 데이터베이스 오류
        Repo-->>App: RepositoryException
        App-->>API: ApplicationException
        API-->>Client: 500 Internal Server Error (SEARCH_009: Search service unavailable)
    else 권한 오류
        API->>API: 인증 실패
        API-->>Client: 401 Unauthorized (AUTH_002: Token expired)
    end
```

## 시퀀스 다이어그램 요약

### 주요 특징
1. **하이브리드 페이징**: 내 카드(커서) vs 공개 카드(오프셋) 방식 분리
2. **계층적 캐싱**: 3분/5분 TTL + 사용자별 무효화
3. **독립적 카드 복사**: 공개 카드 저장 시 완전히 새로운 카드 생성
4. **실시간 제안**: 최근 검색어 + 내 태그 + 인기 태그 조합
5. **이벤트 기반 캐시 무효화**: Unit3 카드 변경 시 자동 캐시 갱신

### 성능 최적화 포인트
- 캐시 우선 조회로 응답 시간 단축
- 병렬 처리로 검색 제안 성능 향상
- 인덱스 최적화로 데이터베이스 쿼리 성능 향상
- 패턴 기반 캐시 무효화로 일관성 보장
