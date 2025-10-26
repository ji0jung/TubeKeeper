# Unit3: Card Creation & Management - 시퀀스 다이어그램

## 1. 카드 생성 플로우

```mermaid
sequenceDiagram
    participant U as User
    participant API as CardController
    participant UC as CreateCardUseCase
    participant R as CardRepository
    participant E as EventPublisher
    participant Redis as Redis
    participant Handler as MetadataHandler
    participant YouTube as YouTubeAPI
    
    U->>API: POST /api/cards {content_url, category_id}
    API->>UC: execute(CreateCardCommand)
    
    UC->>R: check_duplicate(user_id, content_url)
    R-->>UC: null (중복 없음)
    
    UC->>UC: create CardAggregate (CREATING 상태)
    UC->>R: save(CardAggregate)
    UC->>E: publish(CardCreated)
    UC->>E: publish(MetadataCollectionRequested)
    
    E->>Redis: publish to events.MetadataCollectionRequested
    UC-->>API: CreateCardResult
    API-->>U: 201 Created {card_id, status: "CREATING"}
    
    Note over Redis,Handler: 비동기 메타데이터 수집
    Redis->>Handler: MetadataCollectionRequested event
    Handler->>YouTube: extract_metadata(video_id)
    YouTube-->>Handler: {title, thumbnail, duration, published_at}
    
    Handler->>R: find_by_id(card_id)
    R-->>Handler: CardAggregate
    Handler->>Handler: card.update_metadata(metadata)
    Handler->>R: save(CardAggregate)
    Handler->>E: publish(MetadataCollected)
```

## 2. 카드 목록 조회 (커서 기반 페이지네이션)

```mermaid
sequenceDiagram
    participant U as User
    participant API as CardController
    participant UC as GetCardsByUserUseCase
    participant R as CardRepository
    participant CS as CategoryService
    
    U->>API: GET /api/cards?cursor=2024-01-15T10:30:00&limit=20
    API->>UC: execute(GetCardsByUserQuery)
    
    UC->>R: find_by_user_with_cursor(user_id, cursor, limit+1)
    R-->>UC: List<CardAggregate> (21개)
    
    UC->>UC: has_more = cards.length > limit
    UC->>UC: cards = cards[0:20] (마지막 제거)
    
    UC->>CS: get_categories_by_ids([category_ids])
    CS-->>UC: List<Category>
    
    UC->>UC: map to CardSummaryResult
    UC-->>API: CardListResult {cards, next_cursor, has_more}
    API-->>U: 200 OK {cards, next_cursor, has_more}
```

## 3. 즐겨찾기 토글

```mermaid
sequenceDiagram
    participant U as User
    participant API as CardController
    participant UC as ToggleFavoriteUseCase
    participant R as CardRepository
    participant E as EventPublisher
    
    U->>API: POST /api/cards/{card_id}/favorite
    API->>UC: execute(ToggleFavoriteCommand)
    
    UC->>R: find_by_id(card_id)
    R-->>UC: CardAggregate
    
    UC->>UC: validate user ownership
    UC->>UC: card.toggle_favorite()
    
    UC->>R: save(CardAggregate)
    UC->>E: publish(CardFavoriteToggled)
    
    UC-->>API: ToggleFavoriteResult
    API-->>U: 200 OK {is_favorite, message}
```

## 4. 메타데이터 수집 실패 처리

```mermaid
sequenceDiagram
    participant Handler as MetadataHandler
    participant YouTube as YouTubeAPI
    participant R as CardRepository
    participant Retry as RetryHandler
    participant DLQ as DeadLetterQueue
    
    Handler->>YouTube: extract_metadata(video_id)
    YouTube-->>Handler: Error (API 제한, 네트워크 오류 등)
    
    alt 재시도 가능한 오류
        Handler->>Retry: schedule_retry(event_data, retry_count)
        Retry->>Retry: 지수 백오프 계산 (2^retry_count)
        Retry->>Redis: zadd retry_queue with delay
        
        Note over Retry: 지연 후 재시도
        Retry->>Handler: retry MetadataCollectionRequested
        Handler->>YouTube: extract_metadata(video_id) (재시도)
        
        alt 재시도 성공
            YouTube-->>Handler: metadata
            Handler->>R: update card with metadata
        else 최대 재시도 초과
            Handler->>DLQ: send_to_dead_letter_queue
            Handler->>R: mark_metadata_collection_failed
        end
    else 재시도 불가능한 오류 (잘못된 URL 등)
        Handler->>R: find_by_id(card_id)
        R-->>Handler: CardAggregate
        Handler->>Handler: card.mark_metadata_collection_failed(error)
        Handler->>R: save(CardAggregate)
    end
```

## 5. AI 요약 생성 플로우

```mermaid
sequenceDiagram
    participant SQS as SQS
    participant Handler as AiSummaryHandler
    participant AI as BedrockAI
    participant R as CardRepository
    participant E as EventPublisher
    
    SQS->>Handler: receive_message(SummaryGenerationRequest)
    Handler->>Handler: parse message {card_id, script_content}
```

## 5. 카드 상세 조회

```mermaid
sequenceDiagram
    participant U as User
    participant API as CardController
    participant UC as GetCardUseCase
    participant R as CardRepository
    participant CS as CategoryService
    
    U->>API: GET /api/cards/{card_id}
    API->>UC: execute(GetCardQuery)
    
    UC->>R: find_by_id(card_id)
    R-->>UC: CardAggregate
    
    UC->>UC: validate user ownership
    UC->>CS: get_category(category_id)
    CS-->>UC: Category
    
    UC->>UC: map to CardDetailResult
    UC-->>API: CardDetailResult
    API-->>U: 200 OK {card details with metadata}
```

## 6. 오류 처리 시나리오

```mermaid
sequenceDiagram
    participant U as User
    participant API as CardController
    participant UC as CreateCardUseCase
    participant R as CardRepository
    
    U->>API: POST /api/cards {invalid_url}
    API->>UC: execute(CreateCardCommand)
    
    UC->>UC: validate content_url format
    UC-->>API: ValidationException
    
    API->>API: global_exception_handler
    API-->>U: 400 Bad Request {error: "URL 형식이 올바르지 않습니다"}
    
    Note over U,R: 중복 카드 생성 시도
    U->>API: POST /api/cards {existing_url}
    API->>UC: execute(CreateCardCommand)
    
    UC->>R: check_duplicate(user_id, content_url)
    R-->>UC: existing CardAggregate
    
    UC-->>API: CreateCardResult {status: "DUPLICATE"}
    API-->>U: 200 OK {message: "이미 동일한 URL의 카드가 존재합니다"}
```

## 7. 다중 플랫폼 지원 (확장)

```mermaid
sequenceDiagram
    participant U as User
    participant API as CardController
    participant UC as CreateCardUseCase
    participant Handler as MetadataHandler
    participant YT as YouTubeAdapter
    participant IG as InstagramAdapter
    participant WS as WebScraperAdapter
    
    U->>API: POST /api/cards {instagram_reel_url}
    API->>UC: execute(CreateCardCommand)
    UC->>UC: create CardAggregate
    UC-->>API: CreateCardResult
    
    Note over Handler: URL 타입별 어댑터 선택
    Handler->>Handler: select_adapter(content_url)
    
    alt YouTube URL
        Handler->>YT: extract_metadata(content_url)
        YT-->>Handler: VideoMetadata {title, thumbnail, duration}
    else Instagram URL
        Handler->>IG: extract_metadata(content_url)
        IG-->>Handler: VideoMetadata {title, thumbnail, duration}
    else 일반 웹 URL
        Handler->>WS: extract_metadata(content_url)
        WS-->>Handler: VideoMetadata {title, thumbnail, duration}
    end
    
    Handler->>Handler: update card with metadata
```

이 시퀀스 다이어그램들은 Unit3의 주요 플로우와 오류 처리, 확장성을 보여줍니다. 비동기 처리, 재시도 로직, 다중 플랫폼 지원이 명확히 표현되어 있습니다.
