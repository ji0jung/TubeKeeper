# Unit5: Card Sharing - 논리적 설계

## 개요
Unit5는 카드를 다른 사용자와 공유하고 공유받은 카드를 처리하는 기능을 담당합니다. 헥사고날 아키텍처를 기반으로 한 이벤트 기반 시스템으로 설계되었습니다.

## 1. 아키텍처 패턴

### 1.1 헥사고날 아키텍처 적용

```
┌─────────────────────────────────────────────────────────────┐
│                        Adapters                             │
├─────────────────────────────────────────────────────────────┤
│  REST API    │  Event Publisher  │  Redis Cache  │  DB      │
│  Controller  │  Adapter          │  Adapter      │  Adapter │
├─────────────────────────────────────────────────────────────┤
│                         Ports                               │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                        │
│  ShareLinkService  │  SharedCardService  │  MetadataService │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                           │
│  ShareLinkAggregate  │  Domain Services  │  Domain Events   │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 포트와 어댑터 정의

#### Inbound Ports (Primary)
- **ShareLinkPort**: 공유 링크 생성 및 조회
- **SharedCardPort**: 공유 카드 저장 및 처리
- **MetadataPort**: Open Graph 메타데이터 제공

#### Outbound Ports (Secondary)
- **ShareLinkRepositoryPort**: 공유 링크 영속성
- **CachePort**: Redis 캐싱
- **EventPublisherPort**: 도메인 이벤트 발행
- **ExternalServicePort**: 다른 Unit과의 통신

### 1.3 의존성 역전 원칙 적용

```
Domain Layer (고수준)
    ↑ (의존성 역전)
Application Layer
    ↑ (의존성 역전)  
Infrastructure Layer (저수준)
```

- 도메인 레이어는 외부 의존성 없음
- 애플리케이션 레이어는 포트 인터페이스에만 의존
- 인프라 레이어가 포트 구현체 제공

### 1.4 계층별 책임 분리

#### Domain Layer
- 비즈니스 규칙 및 정책
- 애그리게이트 및 엔티티
- 도메인 서비스 및 이벤트

#### Application Layer  
- 유스케이스 조정
- 트랜잭션 관리
- 도메인 서비스 호출

#### Infrastructure Layer
- 데이터베이스 연동
- 외부 API 호출
- 캐싱 및 메시징

## 2. 애플리케이션 서비스 설계

### 2.1 애플리케이션 서비스 식별

#### ShareLinkApplicationService
```python
class ShareLinkApplicationService:
    def create_share_link(self, command: CreateShareLinkCommand) -> ShareLinkResponse
    def get_share_link(self, query: GetShareLinkQuery) -> ShareLinkResponse
    def get_metadata(self, query: GetMetadataQuery) -> MetadataResponse
```

#### SharedCardApplicationService
```python
class SharedCardApplicationService:
    def save_shared_card(self, command: SaveSharedCardCommand) -> SaveResult
    def check_duplicate(self, query: CheckDuplicateQuery) -> DuplicateCheckResult
```

#### CleanupApplicationService
```python
class CleanupApplicationService:
    def soft_delete_expired_links(self) -> CleanupResult
    def hard_delete_old_links(self) -> CleanupResult
```

### 2.2 유스케이스별 서비스 메서드

#### 공유 링크 생성 (US-011)
```python
def create_share_link(self, command: CreateShareLinkCommand) -> ShareLinkResponse:
    # 1. 레이트 리미팅 확인
    # 2. 원본 카드 존재 확인
    # 3. 공유 링크 생성
    # 4. 메타데이터 생성
    # 5. 캐시 저장
    # 6. 이벤트 발행
```

#### 공유 카드 조회 (US-012)
```python
def get_share_link(self, query: GetShareLinkQuery) -> ShareLinkResponse:
    # 1. 캐시에서 조회
    # 2. 만료 여부 확인
    # 3. 접근 횟수 증가
    # 4. 이벤트 발행
```

### 2.3 트랜잭션 경계 및 일관성 정책

#### 트랜잭션 경계
- **공유 링크 생성**: 단일 트랜잭션 (링크 생성 + 메타데이터)
- **공유 카드 저장**: 단일 트랜잭션 (중복 확인 + 카드 생성)
- **접근 로깅**: 별도 트랜잭션 (성능 고려)

#### 일관성 정책
- **강한 일관성**: 공유 링크 생성, 카드 저장
- **최종 일관성**: 접근 통계, 이벤트 처리

### 2.4 오류 처리 및 예외 전략

#### 도메인 예외
```python
class ShareLinkExpiredException(DomainException):
    code = "SHARE_001"
    
class ShareLinkNotFoundException(DomainException):
    code = "SHARE_002"
    
class RateLimitExceededException(DomainException):
    code = "SHARE_011"
```

#### 복구 전략
- **재시도**: 외부 API 호출 실패
- **회로 차단기**: 연속 실패 시 빠른 실패
- **우아한 성능 저하**: 캐시 실패 시 DB 직접 조회

## 3. 인프라스트럭처 설계

### 3.1 데이터베이스 스키마 상세 설계

```sql
-- 공유 링크 테이블
CREATE TABLE share_links (
    share_token UUID PRIMARY KEY,
    card_id UUID NOT NULL,
    user_id UUID NOT NULL,
    share_url VARCHAR(500) NOT NULL,
    expiration_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP NULL,
    access_count INTEGER DEFAULT 0,
    
    INDEX idx_card_id (card_id),
    INDEX idx_user_id (user_id),
    INDEX idx_expiration_date (expiration_date),
    INDEX idx_deleted_at (deleted_at),
    INDEX idx_created_at (created_at)
);

-- Open Graph 메타데이터 테이블
CREATE TABLE open_graph_metadata (
    share_token UUID PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    image_url VARCHAR(1000),
    site_name VARCHAR(100) NOT NULL DEFAULT 'AIDLC',
    site_description VARCHAR(200) DEFAULT '유튜브 링크 저장 앱',
    updated_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (share_token) REFERENCES share_links(share_token) ON DELETE CASCADE
);

-- 레이트 리미팅 로그 (선택적)
CREATE TABLE rate_limit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    INDEX idx_user_id_created_at (user_id, created_at)
);
```

### 3.2 리포지토리 구현 전략

#### ShareLinkRepository 구현
```python
class PostgreSQLShareLinkRepository(ShareLinkRepositoryPort):
    def save(self, share_link: ShareLink) -> None:
        # PostgreSQL INSERT/UPDATE
        
    def find_by_token(self, token: ShareToken) -> Optional[ShareLink]:
        # 캐시 우선 조회 → DB 조회
        
    def soft_delete_expired(self, before_date: date) -> int:
        # UPDATE deleted_at WHERE expiration_date < ?
        
    def hard_delete_old(self, before_date: date) -> int:
        # DELETE WHERE deleted_at < ?
```

### 3.3 외부 시스템 연동 어댑터

#### Unit 연동 어댑터
```python
class UnitIntegrationAdapter(ExternalServicePort):
    def get_card_info(self, card_id: CardId) -> CardInfo:
        # Unit3 Card Service 호출
        
    def create_card(self, card_data: CardData) -> CardId:
        # Unit3 Card Creation API 호출
        
    def get_shared_category(self, user_id: UserId) -> CategoryId:
        # Unit2 Category Service 호출
```

### 3.4 이벤트 발행/구독 메커니즘

#### Redis Pub/Sub 기반
```python
class RedisEventPublisher(EventPublisherPort):
    def publish(self, event: DomainEvent) -> None:
        channel = f"unit5.{event.event_type}"
        redis_client.publish(channel, event.to_json())
```

#### 이벤트 채널 구조
- `unit5.share_link_created`
- `unit5.share_link_accessed`
- `unit5.shared_card_saved`

## 4. API 인터페이스 설계

### 4.1 REST API 엔드포인트 상세 설계

#### 공유 링크 생성
```
POST /api/cards/{cardId}/share
Authorization: Bearer {token}

Response:
{
  "success": true,
  "data": {
    "shareUrl": "https://app.com/shared/abc123",
    "expiresAt": "2024-01-08T00:00:00Z",
    "shareToken": "abc123"
  }
}
```

#### 공유 카드 조회
```
GET /api/shared/{shareToken}
User-Agent: Mozilla/5.0... (일반 사용자)

Response (JSON):
{
  "success": true,
  "data": {
    "card": {
      "title": "영상 제목",
      "thumbnail": "https://...",
      "summary": "AI 요약...",
      "youtubeUrl": "https://youtube.com/..."
    },
    "isExpired": false
  }
}

User-Agent: kakaotalk-scrap/1.0 (크롤러)

Response (HTML):
<!DOCTYPE html>
<html>
<head>
  <meta property="og:title" content="영상 제목">
  <meta property="og:description" content="AI 요약...">
  <meta property="og:image" content="https://...">
  <meta property="og:url" content="https://app.com/shared/abc123">
  <meta property="og:site_name" content="AIDLC">
</head>
</html>
```

### 4.2 요청/응답 DTO 설계

#### Command DTOs
```python
@dataclass
class CreateShareLinkCommand:
    card_id: str
    user_id: str
    base_url: str

@dataclass  
class SaveSharedCardCommand:
    share_token: str
    user_id: str
    category_id: Optional[str] = None
```

#### Query DTOs
```python
@dataclass
class GetShareLinkQuery:
    share_token: str
    user_agent: str
    ip_address: str
```

### 4.3 HTTP 상태 코드 및 오류 응답

#### 상태 코드 매핑
- `200`: 정상 조회
- `201`: 공유 링크 생성 성공
- `400`: 잘못된 요청 (토큰 형식 오류)
- `404`: 링크 없음 또는 만료
- `409`: 중복 저장 시도
- `429`: 레이트 리미팅 초과

#### 오류 응답 형식
```json
{
  "success": false,
  "error": {
    "code": "SHARE_001",
    "message": "링크가 만료되었습니다",
    "details": {
      "expiredAt": "2024-01-08T00:00:00Z"
    }
  }
}
```

### 4.4 Open Graph 메타데이터 응답

#### 활성 링크
```html
<meta property="og:title" content="{카드 제목}">
<meta property="og:description" content="{요약 첫 2줄}">
<meta property="og:image" content="{유튜브 썸네일}">
<meta property="og:url" content="https://app.com/shared/{token}">
<meta property="og:site_name" content="AIDLC">
<meta property="og:type" content="article">
```

#### 만료/삭제된 링크
```html
<meta property="og:title" content="AIDLC - 유튜브 링크 저장 앱">
<meta property="og:description" content="만료된 공유 링크입니다. AIDLC에서 유튜브 영상을 체계적으로 관리하세요.">
<meta property="og:image" content="https://app.com/assets/default-thumbnail.jpg">
<meta property="og:url" content="https://app.com">
<meta property="og:site_name" content="AIDLC">
```

## 5. 보안 및 성능 설계

### 5.1 인증/인가 처리

#### JWT 토큰 검증
```python
class AuthenticationMiddleware:
    def verify_token(self, token: str) -> Optional[UserId]:
        # JWT 검증 및 UserId 추출
        
    def is_authenticated(self, request) -> bool:
        # Authorization 헤더 확인
```

#### 익명 접근 허용
- 공유 링크 조회: 인증 불필요
- 메타데이터 제공: 인증 불필요
- 카드 저장: 인증 필수

### 5.2 공유 링크 보안 전략

#### UUID 기반 토큰
- UUID v4 사용 (예측 불가능)
- 122비트 엔트로피
- 브루트 포스 공격 방지

#### 만료 시간 엄격 검증
```python
def is_expired(self, current_date: date) -> bool:
    return current_date > self.expiration_date
```

### 5.3 캐싱 전략 및 성능 최적화

#### Redis 캐싱 계층
```python
# 캐시 키 구조
share_link:{token} → ShareLink 객체 (TTL: 1시간)
metadata:{token} → OpenGraphMetadata (TTL: 6시간)
rate_limit:{user_id} → 생성 횟수 (TTL: 1시간)
```

#### 캐시 무효화 전략
- 링크 만료 시: 즉시 삭제
- 메타데이터 변경 시: 즉시 갱신
- 접근 횟수 업데이트: 비동기 처리

### 5.4 레이트 리미팅 및 남용 방지

#### 슬라이딩 윈도우 구현
```python
class RateLimiter:
    def is_allowed(self, user_id: str) -> bool:
        now = datetime.now()
        window_start = now - timedelta(hours=1)
        
        # Redis에서 최근 1시간 생성 횟수 조회
        count = redis.zcount(f"rate:{user_id}", 
                           window_start.timestamp(), 
                           now.timestamp())
        
        return count < 20
```

#### IP 기반 추가 제한
- 익명 사용자: IP당 시간당 100회 조회
- 의심스러운 패턴 감지 시 일시 차단

## 6. 통합 및 배포 설계

### 6.1 다른 Unit과의 통합 인터페이스

#### Unit1 (Authentication) 통합
```python
class AuthenticationIntegration:
    def verify_user(self, token: str) -> Optional[UserInfo]:
        response = requests.get(f"{UNIT1_BASE_URL}/api/profile",
                              headers={"Authorization": f"Bearer {token}"})
        return UserInfo.from_response(response)
```

#### Unit2 (Category) 통합
```python
class CategoryIntegration:
    def get_or_create_shared_category(self, user_id: str) -> str:
        # "공유받은 카드" 카테고리 조회/생성
```

#### Unit3 (Card) 통합
```python
class CardIntegration:
    def get_card(self, card_id: str) -> CardInfo:
        # 원본 카드 정보 조회
        
    def create_card(self, card_data: dict) -> str:
        # 새 카드 생성 (독립 복사본)
```

### 6.2 이벤트 기반 통신

#### 발행 이벤트
- `ShareLinkCreated`: 공유 링크 생성 시
- `SharedCardSaved`: 공유 카드 저장 시
- `ShareLinkAccessed`: 링크 접근 시

#### 구독 이벤트
- `CardUpdated`: 원본 카드 변경 시 메타데이터 갱신
- `UserDeleted`: 사용자 삭제 시 관련 링크 정리

### 6.3 배포 및 운영 고려사항

#### 환경 변수 설정
```env
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://...
RATE_LIMIT_PER_HOUR=20
CACHE_TTL_HOURS=1
CLEANUP_RETENTION_DAYS=30
```

#### 헬스 체크
```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "services": {
            "database": check_database(),
            "redis": check_redis(),
            "external_apis": check_external_services()
        }
    }
```

### 6.4 모니터링 및 로깅

#### 주요 메트릭
- 공유 링크 생성 수 (시간당)
- 공유 링크 조회 수 (시간당)
- 캐시 히트율
- 레이트 리미팅 발생 수
- 만료 링크 접근 수

#### 로그 구조
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "service": "unit5-card-sharing",
  "event": "share_link_created",
  "user_id": "user123",
  "share_token": "abc123",
  "card_id": "card456"
}
```

## 설계 완료 요약

Unit5 Card Sharing의 논리적 설계가 완료되었습니다.

### 핵심 특징
- **헥사고날 아키텍처**: 도메인 중심 설계
- **이벤트 기반**: 느슨한 결합
- **Redis 캐싱**: 고성능 조회
- **레이트 리미팅**: 남용 방지
- **소프트 삭제**: 사용자 경험 향상
- **Open Graph**: 메신저 미리보기 지원

### 성능 최적화
- 캐시 우선 조회
- 비동기 이벤트 처리
- 인덱스 최적화
- 배치 정리 작업

### 보안 강화
- UUID 기반 예측 불가능한 토큰
- 엄격한 만료 시간 검증
- 슬라이딩 윈도우 레이트 리미팅
- IP 기반 추가 보호
