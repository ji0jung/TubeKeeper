# Unit5: Card Sharing - 시퀀스 다이어그램

## 개요
Unit5 Card Sharing의 주요 API별 시퀀스 다이어그램을 Mermaid 형식으로 제공합니다.

## 1. 공유 링크 생성 (US-011)

### 1.1 정상 케이스
```mermaid
sequenceDiagram
    participant User as 사용자
    participant API as REST API
    participant Auth as 인증 서비스
    participant Rate as 레이트 리미터
    participant App as 애플리케이션 서비스
    participant Domain as 도메인 서비스
    participant Unit3 as Unit3 (Card)
    participant DB as 데이터베이스
    participant Cache as Redis 캐시
    participant Event as 이벤트 발행자

    User->>API: POST /api/cards/{cardId}/share
    API->>Auth: JWT 토큰 검증
    Auth-->>API: UserId 반환
    
    API->>Rate: 레이트 리미팅 확인
    Rate->>Cache: 최근 1시간 생성 횟수 조회
    Cache-->>Rate: 현재 횟수 (예: 15)
    Rate-->>API: 허용 (20 미만)
    
    API->>App: CreateShareLinkCommand
    App->>Unit3: 원본 카드 정보 조회
    Unit3-->>App: CardInfo 반환
    
    App->>Domain: ShareLinkCreationService.create()
    Domain->>Domain: UUID 토큰 생성
    Domain->>Domain: 만료일 계산 (7일 후)
    Domain->>Domain: ShareLink 애그리게이트 생성
    Domain->>Domain: OpenGraphMetadata 생성
    
    Domain->>DB: ShareLink 저장
    Domain->>DB: OpenGraphMetadata 저장
    DB-->>Domain: 저장 완료
    
    Domain->>Cache: 공유 링크 캐싱 (TTL: 1시간)
    Domain->>Cache: 메타데이터 캐싱 (TTL: 6시간)
    
    Domain->>Event: ShareLinkCreated 이벤트 발행
    Event->>Event: Redis Pub/Sub 전송
    
    Domain-->>App: ShareLink 반환
    App-->>API: ShareLinkResponse
    API-->>User: 201 Created + 공유 URL
```

### 1.2 레이트 리미팅 초과 케이스
```mermaid
sequenceDiagram
    participant User as 사용자
    participant API as REST API
    participant Auth as 인증 서비스
    participant Rate as 레이트 리미터
    participant Cache as Redis 캐시

    User->>API: POST /api/cards/{cardId}/share
    API->>Auth: JWT 토큰 검증
    Auth-->>API: UserId 반환
    
    API->>Rate: 레이트 리미팅 확인
    Rate->>Cache: 최근 1시간 생성 횟수 조회
    Cache-->>Rate: 현재 횟수 (예: 22)
    Rate-->>API: 거부 (20 초과)
    
    API-->>User: 429 Too Many Requests
    Note over User,API: { "error": "SHARE_011", "message": "시간당 생성 한도 초과" }
```

## 2. 공유 카드 조회 - 익명 사용자 (US-012)

### 2.1 정상 케이스 (일반 브라우저)
```mermaid
sequenceDiagram
    participant User as 익명 사용자
    participant API as REST API
    participant Cache as Redis 캐시
    participant App as 애플리케이션 서비스
    participant DB as 데이터베이스
    participant Event as 이벤트 발행자

    User->>API: GET /api/shared/{shareToken}
    Note over User,API: User-Agent: Mozilla/5.0...
    
    API->>Cache: 공유 링크 캐시 조회
    Cache-->>API: ShareLink 반환 (캐시 히트)
    
    API->>App: GetShareLinkQuery
    App->>App: 만료 여부 확인
    Note over App: 현재 날짜 vs 만료 날짜 비교
    
    App->>DB: 접근 횟수 증가 (비동기)
    App->>Event: ShareLinkAccessed 이벤트 발행
    
    App-->>API: ShareLinkResponse (JSON)
    API-->>User: 200 OK + 카드 정보
    
    Note over User,API: {
    Note over User,API:   "card": {
    Note over User,API:     "title": "영상 제목",
    Note over User,API:     "thumbnail": "썸네일 URL",
    Note over User,API:     "summary": "AI 요약",
    Note over User,API:     "youtubeUrl": "원본 URL"
    Note over User,API:   }
    Note over User,API: }
```

### 2.2 메신저 크롤러 케이스
```mermaid
sequenceDiagram
    participant Crawler as 카카오톡 크롤러
    participant API as REST API
    participant Cache as Redis 캐시
    participant App as 애플리케이션 서비스

    Crawler->>API: GET /api/shared/{shareToken}
    Note over Crawler,API: User-Agent: kakaotalk-scrap/1.0
    
    API->>Cache: 메타데이터 캐시 조회
    Cache-->>API: OpenGraphMetadata 반환
    
    API->>App: GetMetadataQuery
    App->>App: User-Agent 패턴 확인
    App->>App: HTML 메타태그 생성
    
    App-->>API: HTML Response
    API-->>Crawler: 200 OK + HTML
    
    Note over Crawler,API: <meta property="og:title" content="영상 제목">
    Note over Crawler,API: <meta property="og:description" content="AI 요약">
    Note over Crawler,API: <meta property="og:image" content="썸네일 URL">
    Note over Crawler,API: <meta property="og:site_name" content="AIDLC">
```

### 2.3 만료된 링크 케이스
```mermaid
sequenceDiagram
    participant User as 사용자
    participant API as REST API
    participant Cache as Redis 캐시
    participant App as 애플리케이션 서비스
    participant DB as 데이터베이스

    User->>API: GET /api/shared/{shareToken}
    
    API->>Cache: 공유 링크 캐시 조회
    Cache-->>API: 캐시 미스 (만료로 삭제됨)
    
    API->>App: GetShareLinkQuery
    App->>DB: ShareLink 조회
    DB-->>App: ShareLink 반환 (deleted_at: null)
    
    App->>App: 만료 여부 확인
    Note over App: 현재 날짜 > 만료 날짜
    
    App-->>API: ExpiredLinkResponse
    API-->>User: 404 Not Found
    
    Note over User,API: {
    Note over User,API:   "error": "SHARE_001",
    Note over User,API:   "message": "링크가 만료되었습니다"
    Note over User,API: }
```

## 3. 공유 카드 조회 - 인증된 사용자 (US-012)

### 3.1 정상 케이스 (자동 저장 포함)
```mermaid
sequenceDiagram
    participant User as 인증된 사용자
    participant API as REST API
    participant Auth as 인증 서비스
    participant Cache as Redis 캐시
    participant App as 애플리케이션 서비스
    participant Domain as 도메인 서비스
    participant Unit2 as Unit2 (Category)
    participant Unit3 as Unit3 (Card)
    participant DB as 데이터베이스
    participant Event as 이벤트 발행자

    User->>API: GET /api/shared/{shareToken}
    Note over User,API: Authorization: Bearer {token}
    
    API->>Auth: JWT 토큰 검증
    Auth-->>API: UserId 반환
    
    API->>Cache: 공유 링크 캐시 조회
    Cache-->>API: ShareLink 반환
    
    API->>App: GetShareLinkQuery (with UserId)
    App->>App: 만료 여부 확인 (정상)
    
    App->>Domain: CardDuplicationCheckService
    Domain->>Unit3: YouTube URL로 중복 확인
    Unit3-->>Domain: 중복 없음
    
    App->>Unit2: "공유받은 카드" 카테고리 조회
    Unit2-->>App: CategoryId 반환
    
    App->>Domain: SharedCardSaveService
    Domain->>Unit3: 새 카드 생성 (독립 복사본)
    Unit3-->>Domain: 새 CardId 반환
    
    Domain->>Event: SharedCardSaved 이벤트 발행
    
    App-->>API: ShareLinkResponse + SaveResult
    API-->>User: 200 OK + 카드 정보 + 저장 완료
    
    Note over User,API: {
    Note over User,API:   "card": {...},
    Note over User,API:   "saved": true,
    Note over User,API:   "newCardId": "card789"
    Note over User,API: }
```

### 3.2 중복 저장 시도 케이스
```mermaid
sequenceDiagram
    participant User as 인증된 사용자
    participant API as REST API
    participant Auth as 인증 서비스
    participant App as 애플리케이션 서비스
    participant Domain as 도메인 서비스
    participant Unit3 as Unit3 (Card)
    participant Event as 이벤트 발행자

    User->>API: GET /api/shared/{shareToken}
    API->>Auth: JWT 토큰 검증
    Auth-->>API: UserId 반환
    
    API->>App: GetShareLinkQuery (with UserId)
    App->>App: 만료 여부 확인 (정상)
    
    App->>Domain: CardDuplicationCheckService
    Domain->>Unit3: YouTube URL로 중복 확인
    Unit3-->>Domain: 기존 카드 존재 (cardId: "existing123")
    
    Domain->>Event: SharedCardDuplicateAttempted 이벤트 발행
    
    App-->>API: ShareLinkResponse + DuplicateResult
    API-->>User: 200 OK + 카드 정보 + 중복 안내
    
    Note over User,API: {
    Note over User,API:   "card": {...},
    Note over User,API:   "saved": false,
    Note over User,API:   "alreadyExists": true,
    Note over User,API:   "existingCardId": "existing123"
    Note over User,API: }
```

## 4. 공유 카드 자동 저장 (US-012)

### 4.1 별도 API 호출 케이스
```mermaid
sequenceDiagram
    participant User as 인증된 사용자
    participant API as REST API
    participant Auth as 인증 서비스
    participant App as 애플리케이션 서비스
    participant Domain as 도메인 서비스
    participant Unit2 as Unit2 (Category)
    participant Unit3 as Unit3 (Card)
    participant DB as 데이터베이스
    participant Event as 이벤트 발행자

    User->>API: POST /api/shared/{shareToken}/save
    Note over User,API: Authorization: Bearer {token}
    
    API->>Auth: JWT 토큰 검증
    Auth-->>API: UserId 반환
    
    API->>App: SaveSharedCardCommand
    App->>DB: ShareLink 조회 및 유효성 확인
    DB-->>App: ShareLink 반환 (유효)
    
    App->>Domain: CardDuplicationCheckService
    Domain->>Unit3: YouTube URL로 중복 확인
    Unit3-->>Domain: 중복 없음
    
    App->>Unit2: "공유받은 카드" 카테고리 확인
    Unit2-->>App: CategoryId 반환
    
    App->>Domain: SharedCardSaveService
    Domain->>Unit3: 원본 카드 정보 조회
    Unit3-->>Domain: CardInfo 반환
    
    Domain->>Unit3: 새 카드 생성 요청
    Note over Domain,Unit3: {
    Note over Domain,Unit3:   "contentUrl": "원본 YouTube URL",
    Note over Domain,Unit3:   "categoryId": "공유받은카드_ID",
    Note over Domain,Unit3:   "memo": "공유받은 카드"
    Note over Domain,Unit3: }
    Unit3-->>Domain: 새 CardId 반환
    
    Domain->>Event: SharedCardSaved 이벤트 발행
    
    App-->>API: SaveResult
    API-->>User: 201 Created + 새 카드 정보
    
    Note over User,API: {
    Note over User,API:   "success": true,
    Note over User,API:   "newCard": {
    Note over User,API:     "id": "card789",
    Note over User,API:     "title": "영상 제목",
    Note over User,API:     "category": "공유받은 카드"
    Note over User,API:   }
    Note over User,API: }
```

## 5. Open Graph 메타데이터 제공

### 5.1 활성 링크 메타데이터
```mermaid
sequenceDiagram
    participant Crawler as 메신저 크롤러
    participant API as REST API
    participant Cache as Redis 캐시
    participant App as 애플리케이션 서비스
    participant DB as 데이터베이스

    Crawler->>API: GET /api/shared/{shareToken}
    Note over Crawler,API: User-Agent: TelegramBot

    API->>Cache: 메타데이터 캐시 조회
    Cache-->>API: 캐시 미스
    
    API->>App: GetMetadataQuery
    App->>DB: ShareLink + OpenGraphMetadata 조회
    DB-->>App: 메타데이터 반환
    
    App->>App: User-Agent 패턴 매칭
    Note over App: 크롤러 요청으로 판단
    
    App->>App: HTML 메타태그 생성
    App->>Cache: 메타데이터 캐싱 (TTL: 6시간)
    
    App-->>API: HTML Response
    API-->>Crawler: 200 OK + HTML
    
    Note over Crawler,API: <!DOCTYPE html>
    Note over Crawler,API: <html>
    Note over Crawler,API: <head>
    Note over Crawler,API:   <meta property="og:title" content="영상 제목">
    Note over Crawler,API:   <meta property="og:description" content="AI 요약 첫 2줄">
    Note over Crawler,API:   <meta property="og:image" content="유튜브 썸네일">
    Note over Crawler,API:   <meta property="og:url" content="공유 링크">
    Note over Crawler,API:   <meta property="og:site_name" content="AIDLC">
    Note over Crawler,API: </head>
    Note over Crawler,API: </html>
```

### 5.2 만료/삭제된 링크 기본 메타데이터
```mermaid
sequenceDiagram
    participant Crawler as 메신저 크롤러
    participant API as REST API
    participant App as 애플리케이션 서비스
    participant DB as 데이터베이스

    Crawler->>API: GET /api/shared/{shareToken}
    Note over Crawler,API: User-Agent: kakaotalk-scrap/1.0

    API->>App: GetMetadataQuery
    App->>DB: ShareLink 조회
    
    alt 만료된 링크 (소프트 삭제)
        DB-->>App: ShareLink 반환 (deleted_at: 설정됨)
        App->>App: 만료 상태 확인
    else 삭제된 링크 (물리 삭제)
        DB-->>App: 링크 없음
    end
    
    App->>App: 기본 메타데이터 생성
    Note over App: 앱 홍보용 기본 정보
    
    App-->>API: HTML Response (기본 메타데이터)
    API-->>Crawler: 200 OK + HTML
    
    Note over Crawler,API: <meta property="og:title" content="AIDLC - 유튜브 링크 저장 앱">
    Note over Crawler,API: <meta property="og:description" content="만료된 공유 링크입니다. AIDLC에서 유튜브 영상을 체계적으로 관리하세요.">
    Note over Crawler,API: <meta property="og:image" content="기본 앱 썸네일">
    Note over Crawler,API: <meta property="og:url" content="https://app.com">
    Note over Crawler,API: <meta property="og:site_name" content="AIDLC">
```

## 6. 배치 정리 작업

### 6.1 만료된 링크 소프트 삭제
```mermaid
sequenceDiagram
    participant Scheduler as 스케줄러
    participant Batch as 배치 서비스
    participant DB as 데이터베이스
    participant Cache as Redis 캐시
    participant Event as 이벤트 발행자

    Note over Scheduler: 매일 새벽 2시
    Scheduler->>Batch: 만료 링크 정리 작업 시작
    
    Batch->>DB: 만료된 링크 조회
    Note over Batch,DB: WHERE expiration_date < CURRENT_DATE AND deleted_at IS NULL
    DB-->>Batch: 만료된 링크 목록 반환
    
    loop 각 만료된 링크
        Batch->>DB: deleted_at 설정 (소프트 삭제)
        Batch->>Cache: 캐시에서 제거
        Batch->>Event: ShareLinkExpired 이벤트 발행
    end
    
    Batch-->>Scheduler: 소프트 삭제 완료 (처리 건수)
```

### 6.2 오래된 링크 물리 삭제
```mermaid
sequenceDiagram
    participant Scheduler as 스케줄러
    participant Batch as 배치 서비스
    participant DB as 데이터베이스
    participant Event as 이벤트 발행자

    Note over Scheduler: 매일 새벽 2시 (소프트 삭제 후)
    Scheduler->>Batch: 오래된 링크 물리 삭제 시작
    
    Batch->>DB: 30일 이전 소프트 삭제된 링크 조회
    Note over Batch,DB: WHERE deleted_at < CURRENT_DATE - INTERVAL '30 days'
    DB-->>Batch: 삭제 대상 링크 목록
    
    Batch->>DB: OpenGraphMetadata 물리 삭제
    Note over Batch,DB: CASCADE로 자동 삭제됨
    
    Batch->>DB: ShareLink 물리 삭제
    DB-->>Batch: 삭제 완료
    
    Batch->>Event: 물리 삭제 완료 이벤트 발행
    Batch-->>Scheduler: 물리 삭제 완료 (처리 건수)
```

## 시퀀스 다이어그램 요약

### 주요 플로우
1. **공유 링크 생성**: 레이트 리미팅 → 카드 검증 → 링크 생성 → 캐싱 → 이벤트 발행
2. **익명 조회**: 캐시 조회 → 만료 확인 → 응답 (JSON/HTML 구분)
3. **인증된 조회**: 토큰 검증 → 중복 확인 → 자동 저장 → 이벤트 발행
4. **메타데이터 제공**: User-Agent 구분 → HTML 메타태그 생성 → 캐싱
5. **배치 정리**: 소프트 삭제 → 물리 삭제 → 이벤트 발행

### 성능 최적화 포인트
- Redis 캐시 우선 조회
- 비동기 이벤트 처리
- 접근 횟수 업데이트 분리
- 메타데이터 장기 캐싱

### 오류 처리 패턴
- 레이트 리미팅 초과 시 즉시 차단
- 만료된 링크의 우아한 처리
- 중복 저장 시도의 친화적 안내
- 삭제된 링크의 기본 메타데이터 제공
