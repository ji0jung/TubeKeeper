# Unit5: Card Sharing - 도메인 모델

## 개요
Unit5는 카드를 다른 사용자와 공유하고 공유받은 카드를 처리하는 기능을 담당하는 독립적인 단위입니다. 도메인 주도 설계(DDD)를 사용하여 전술적 구성 요소들을 설계했습니다.

## 1. 도메인 분석 및 이해

### 1.1 사용자 스토리 분석

#### US-011: 카드 링크 공유
- **목적**: 저장한 카드를 친구에게 링크로 공유
- **핵심 기능**: 
  - 고유한 공유 링크 생성
  - 클립보드 복사 기능
  - 7일간 유효한 링크
  - 유효기간 안내
  - **메신저 링크 미리보기 지원** (썸네일, 제목, 요약, 앱 홍보)

#### US-012: 공유 카드 조회 및 자동 저장
- **목적**: 공유받은 링크를 통해 카드 정보 확인 및 저장
- **핵심 기능**:
  - 인증 없는 카드 정보 조회
  - 원본 유튜브 영상 이동
  - 로그인 회원 자동 저장 ("공유받은 카드" 카테고리)
  - 중복 저장 방지
  - 만료 링크 처리
  - **Open Graph 메타데이터 제공**

### 1.2 핵심 비즈니스 규칙

#### 공유 링크 생성 (US-011)
- **링크 유일성**: 각 공유 요청마다 고유한 UUID 기반 링크 생성
- **유효기간**: 생성일로부터 정확히 7일간 유효
- **접근 권한**: 링크를 아는 누구나 접근 가능 (인증 불필요)
- **링크 형태**: `/shared/{uuid}` 형태의 UUID 기반 URL
- **메타데이터 생성**: 공유 링크 생성 시 Open Graph 메타데이터 준비

#### 공유 카드 조회 (US-012)
- **만료 검증**: 접근 시점에 `created_at + 7일` 비교로 실시간 검증
- **익명 접근**: 로그인 없이도 카드 정보 조회 가능
- **원본 연결**: 원본 유튜브 영상으로 직접 이동 가능
- **만료 처리**: 만료된 링크 접근 시 적절한 안내 메시지 표시
- **메타데이터 응답**: 메신저 크롤러 요청 시 Open Graph 태그 제공

#### 메신저 링크 미리보기 (추가)
- **Open Graph 지원**: og:title, og:description, og:image, og:url 태그 제공
- **썸네일 표시**: 원본 카드의 유튜브 썸네일 이미지 사용
- **제목 표시**: 원본 카드의 제목 표시
- **요약 표시**: AI 생성 요약의 일부 (첫 1-2줄) 표시
- **앱 홍보**: 사이트명과 홍보 문구 포함
- **만료 처리**: 만료된 링크도 기본 메타데이터 제공 (만료 안내)

#### 자동 저장 (US-012)
- **조건부 저장**: 로그인된 회원만 자동 저장
- **카테고리 지정**: "공유받은 카드" 시스템 카테고리에 저장
- **중복 방지**: YouTube URL 기준으로 중복 확인
- **독립성**: 원본과 완전히 독립된 새 카드로 생성

### 1.3 도메인 전문가 언어 (Ubiquitous Language)

#### 핵심 용어 정의
- **Share Link**: 카드를 공유하기 위한 고유한 URL
- **Share Token**: 공유 링크의 고유 식별자 (UUID)
- **Expiration**: 공유 링크의 만료 시점 (생성 + 7일)
- **Anonymous Access**: 인증 없는 공유 카드 조회
- **Auto Save**: 로그인 회원의 공유 카드 자동 저장
- **Shared Cards Category**: 공유받은 카드들이 저장되는 시스템 카테고리
- **Duplicate Prevention**: YouTube URL 기준 중복 저장 방지
- **Independent Copy**: 원본과 독립된 카드 복사본 생성
- **Open Graph Metadata**: 메신저 링크 미리보기용 메타데이터
- **Link Preview**: 메신저에서 표시되는 링크 미리보기
- **Thumbnail**: 카드의 유튜브 썸네일 이미지
- **Summary Excerpt**: 요약의 일부분 (미리보기용)
- **App Branding**: 앱 홍보 문구 및 사이트명

### 1.4 도메인 경계 및 컨텍스트 매핑

#### 도메인 경계
- **내부**: 공유 링크 생성, 공유 카드 조회, 자동 저장 로직, Open Graph 메타데이터 생성
- **외부 의존성**:
  - Unit1 (Authentication): 사용자 인증 상태 확인
  - Unit2 (Category): "공유받은 카드" 카테고리 관리
  - Unit3 (Card): 원본 카드 정보 조회, 새 카드 생성

## 2. 애그리게이트 설계

### 2.1 애그리게이트 식별 및 경계 정의

#### ShareLinkAggregate
**애그리게이트 루트**: ShareLink 엔티티
**식별자**: ShareToken (UUID)
**책임**: 공유 링크 생명주기 관리, 만료 검증, 메타데이터 제공

**경계 내부:**
- ShareLink (애그리게이트 루트)
- OpenGraphMetadata (엔티티)
- ShareToken, ExpirationDate, ShareUrl (값 객체)

**경계 외부 (참조만):**
- CardId (Unit3에서 관리)
- UserId (Unit1에서 관리)

### 2.2 애그리게이트 루트 선정

#### ShareLink (애그리게이트 루트)
**선정 이유:**
- 공유 링크의 생명주기를 완전히 제어
- 만료 검증 등 핵심 비즈니스 규칙 적용
- 외부에서 직접 접근하는 진입점
- 트랜잭션 경계의 자연스러운 단위

### 2.3 불변성 규칙 정의

#### ShareLink 불변성
1. **토큰 유일성**: ShareToken은 시스템 전체에서 유일해야 함
2. **만료 일관성**: ExpirationDate는 생성 시점 + 7일로 고정
3. **카드 참조 무결성**: CardId는 항상 유효한 카드를 참조해야 함
4. **메타데이터 완전성**: OpenGraphMetadata는 카드 정보와 일치해야 함
5. **상태 일관성**: 만료된 링크는 조회만 가능하고 저장 불가

#### 비즈니스 불변성
- **7일 만료 규칙**: 모든 공유 링크는 생성 후 정확히 7일 후 만료
- **익명 접근 보장**: 유효한 링크는 인증 없이 접근 가능
- **중복 방지**: 동일 YouTube URL은 사용자당 하나만 저장

### 2.4 애그리게이트 간 참조 관계 설계

#### 외부 참조 (ID만 보관)
- **CardId**: Unit3의 Card 애그리게이트 참조
- **UserId**: Unit1의 User 애그리게이트 참조 (공유 생성자)

## 3. 엔티티 및 값 객체 설계

### 3.1 엔티티 설계

#### ShareLink (애그리게이트 루트)
```
속성:
- ShareToken: ShareToken (식별자, UUID)
- CardId: CardId (외부 참조)
- UserId: UserId (외부 참조, 공유 생성자)
- ShareUrl: ShareUrl (값 객체)
- ExpirationDate: ExpirationDate (값 객체)
- CreatedAt: DateTime
- AccessCount: Integer (조회 횟수, 통계용)

행위:
- Create(cardId, userId): 새 공유 링크 생성
- IsExpired(): 만료 여부 확인
- IncrementAccess(): 접근 횟수 증가
- GetMetadata(): Open Graph 메타데이터 반환
```

#### OpenGraphMetadata (엔티티)
```
속성:
- ShareToken: ShareToken (부모 참조)
- Title: String (카드 제목)
- Description: String (요약 일부)
- ImageUrl: String (썸네일 URL)
- SiteName: String (앱명)
- SiteDescription: String (앱 홍보 문구)
- UpdatedAt: DateTime

행위:
- UpdateFromCard(card): 카드 정보로 메타데이터 갱신
- ToOpenGraphTags(): HTML 메타 태그 생성
```

### 3.2 값 객체 설계

#### ShareToken (식별자)
```
속성:
- Value: UUID

규칙:
- UUID v4 형식
- 시스템 전체 유일성
- 불변성

행위:
- Generate(): 새 토큰 생성
- ToString(): 문자열 변환
```

#### ShareUrl (값 객체)
```
속성:
- BaseUrl: String (도메인)
- Token: ShareToken
- FullUrl: String (완전한 URL)

규칙:
- /shared/{token} 형태
- HTTPS 필수
- 불변성

행위:
- Build(baseUrl, token): URL 생성
- IsValid(): 유효성 검증
```

#### ExpirationDate (값 객체)
```
속성:
- Value: DateTime

규칙:
- 생성 시점 + 7일
- UTC 기준
- 불변성

행위:
- CreateFromNow(): 현재 시점 + 7일
- IsExpired(currentTime): 만료 여부 확인
- DaysRemaining(): 남은 일수 계산
```

### 3.3 식별자 전략

#### ShareToken 생성 전략
- **UUID v4 사용**: 충돌 가능성 최소화
- **생성 시점**: 공유 링크 생성 요청 시
- **유일성 보장**: 데이터베이스 제약조건으로 이중 보장

### 3.4 생명주기 관리 규칙

#### ShareLink 생명주기
1. **생성**: 사용자 공유 요청 시 생성
2. **활성**: 7일간 접근 가능 상태
3. **만료**: 7일 후 자동 만료 (소프트 만료)
4. **정리**: 만료 후 일정 기간 후 물리 삭제 (배치 작업)

#### OpenGraphMetadata 생명주기
- **생성**: ShareLink 생성과 동시에 생성
- **갱신**: 원본 카드 정보 변경 시 갱신 (이벤트 기반)
- **삭제**: ShareLink 삭제 시 함께 삭제

## 4. 도메인 서비스 설계

### 4.1 도메인 서비스 필요성 분석

#### ShareLinkCreationService
**필요성**: 공유 링크 생성 시 외부 시스템과의 협력이 필요
- Unit3에서 원본 카드 정보 조회
- Open Graph 메타데이터 생성
- 중복 토큰 검증

#### CardDuplicationCheckService  
**필요성**: 자동 저장 시 중복 확인 로직이 복잡
- YouTube URL 기준 중복 검증
- 사용자별 카드 존재 여부 확인
- Unit3 Card 애그리게이트와 협력

#### SharedCardSaveService
**필요성**: 공유 카드 저장 시 여러 Unit과 협력 필요
- Unit2에서 "공유받은 카드" 카테고리 확인/생성
- Unit3에서 새 카드 생성
- 중복 방지 로직 적용

### 4.2 도메인 서비스 인터페이스 정의

#### ShareLinkCreationService
```
인터페이스:
- CreateShareLink(cardId: CardId, userId: UserId): ShareLink

책임:
- 원본 카드 정보 조회 및 검증
- 고유한 ShareToken 생성
- Open Graph 메타데이터 생성
- ShareLink 애그리게이트 생성

외부 의존성:
- CardRepository (Unit3)
- ShareLinkRepository
```

#### CardDuplicationCheckService
```
인터페이스:
- IsDuplicate(userId: UserId, youtubeUrl: YouTubeUrl): Boolean
- FindExistingCard(userId: UserId, youtubeUrl: YouTubeUrl): CardId?

책임:
- YouTube URL 기준 중복 검증
- 사용자별 카드 존재 여부 확인
- 정규화된 URL 비교

외부 의존성:
- CardRepository (Unit3)
```

#### SharedCardSaveService
```
인터페이스:
- SaveSharedCard(shareToken: ShareToken, userId: UserId): SaveResult

책임:
- 공유 링크 유효성 검증
- 중복 저장 방지
- "공유받은 카드" 카테고리 확인/생성
- 독립적인 새 카드 생성

외부 의존성:
- ShareLinkRepository
- CardRepository (Unit3)
- CategoryRepository (Unit2)
- CardDuplicationCheckService
```

### 4.3 외부 시스템 연동 포인트 식별

#### Unit1 (Authentication) 연동
- **연동 포인트**: 사용자 인증 상태 확인
- **방식**: HTTP API 호출 또는 JWT 토큰 검증
- **데이터**: UserId, 인증 상태

#### Unit2 (Category) 연동  
- **연동 포인트**: "공유받은 카드" 카테고리 관리
- **방식**: 도메인 이벤트 또는 직접 API 호출
- **데이터**: CategoryId, 카테고리 생성/조회

#### Unit3 (Card) 연동
- **연동 포인트**: 원본 카드 조회, 새 카드 생성, 중복 확인
- **방식**: 도메인 서비스 간 협력
- **데이터**: Card 정보, YouTube URL, 메타데이터

## 5. 도메인 이벤트 설계

### 5.1 도메인 이벤트 식별

#### ShareLinkCreated
**발생 시점**: 새로운 공유 링크가 생성될 때
**목적**: 다른 시스템에 공유 링크 생성 알림

#### ShareLinkAccessed  
**발생 시점**: 공유 링크에 접근할 때
**목적**: 접근 통계 수집, 사용 패턴 분석

#### ShareLinkExpired
**발생 시점**: 공유 링크가 만료될 때 (접근 시점 검증)
**목적**: 만료 통계, 정리 작업 트리거

#### SharedCardSaved
**발생 시점**: 공유받은 카드가 사용자 계정에 저장될 때  
**목적**: 공유 성과 추적, 사용자 활동 기록

#### SharedCardDuplicateAttempted
**발생 시점**: 이미 저장된 카드를 다시 저장하려 할 때
**목적**: 중복 시도 통계, 사용자 경험 개선

### 5.2 이벤트 페이로드 설계

#### ShareLinkCreated
```json
{
  "eventId": "UUID",
  "eventType": "ShareLinkCreated",
  "timestamp": "2024-01-01T00:00:00Z",
  "aggregateId": "ShareToken",
  "payload": {
    "shareToken": "UUID",
    "cardId": "UUID", 
    "userId": "UUID",
    "shareUrl": "https://app.com/shared/uuid",
    "expirationDate": "2024-01-08T00:00:00Z"
  }
}
```

#### ShareLinkAccessed
```json
{
  "eventId": "UUID",
  "eventType": "ShareLinkAccessed", 
  "timestamp": "2024-01-01T00:00:00Z",
  "aggregateId": "ShareToken",
  "payload": {
    "shareToken": "UUID",
    "accessorUserId": "UUID?",
    "isAuthenticated": "Boolean",
    "userAgent": "String",
    "ipAddress": "String"
  }
}
```

#### SharedCardSaved
```json
{
  "eventId": "UUID",
  "eventType": "SharedCardSaved",
  "timestamp": "2024-01-01T00:00:00Z", 
  "aggregateId": "ShareToken",
  "payload": {
    "shareToken": "UUID",
    "originalCardId": "UUID",
    "newCardId": "UUID",
    "savedByUserId": "UUID",
    "categoryId": "UUID"
  }
}
```

### 5.3 이벤트 발행 시점 정의

#### ShareLinkCreated
- **발행 시점**: ShareLink.Create() 메서드 완료 후
- **발행 주체**: ShareLinkCreationService
- **트랜잭션**: 동일 트랜잭션 내에서 발행

#### ShareLinkAccessed
- **발행 시점**: ShareLink.IncrementAccess() 메서드 호출 시
- **발행 주체**: ShareLink 애그리게이트
- **트랜잭션**: 별도 트랜잭션 (성능 고려)

#### SharedCardSaved  
- **발행 시점**: SharedCardSaveService.SaveSharedCard() 완료 후
- **발행 주체**: SharedCardSaveService
- **트랜잭션**: 동일 트랜잭션 내에서 발행

### 5.4 이벤트 처리 정책 수립

#### 이벤트 저장소
- **저장 방식**: Event Store 패턴 사용
- **저장소**: PostgreSQL events 테이블
- **보관 기간**: 1년 (분석 및 감사용)

#### 이벤트 전파
- **메시징**: Redis Pub/Sub 또는 AWS SQS
- **재시도**: 지수 백오프 방식
- **실패 처리**: Dead Letter Queue

#### 이벤트 구독자
- **Analytics Service**: 모든 이벤트 구독 (통계 분석)
- **Notification Service**: ShareLinkCreated 구독 (알림)
- **Cleanup Service**: ShareLinkExpired 구독 (정리 작업)

## 6. 리포지토리 설계

### 6.1 리포지토리 인터페이스 정의

#### ShareLinkRepository
```
인터페이스:
- Save(shareLink: ShareLink): void
- FindByToken(token: ShareToken): ShareLink?
- FindByCardId(cardId: CardId): List<ShareLink>
- FindExpiredLinks(beforeDate: DateTime): List<ShareLink>
- Delete(token: ShareToken): void
- ExistsToken(token: ShareToken): Boolean

책임:
- ShareLink 애그리게이트 영속성 관리
- 토큰 기반 조회
- 만료된 링크 조회 (정리 작업용)
- 중복 토큰 검증
```

#### OpenGraphMetadataRepository
```
인터페이스:
- Save(metadata: OpenGraphMetadata): void
- FindByShareToken(token: ShareToken): OpenGraphMetadata?
- Update(metadata: OpenGraphMetadata): void
- Delete(token: ShareToken): void

책임:
- Open Graph 메타데이터 영속성 관리
- 공유 링크별 메타데이터 조회
- 메타데이터 갱신 (카드 정보 변경 시)
```

### 6.2 조회 메서드 설계

#### 기본 조회 메서드
- **FindByToken**: 공유 링크 접근 시 사용 (가장 빈번한 조회)
- **FindByCardId**: 특정 카드의 공유 링크 목록 조회
- **ExistsToken**: 토큰 중복 검증 (생성 시)

#### 관리용 조회 메서드  
- **FindExpiredLinks**: 배치 정리 작업용
- **FindByUserId**: 사용자별 공유 링크 관리 (향후 확장)
- **FindRecentLinks**: 최근 생성된 링크 조회 (통계용)

#### 성능 최적화 조회
- **FindActiveByCardId**: 유효한 공유 링크만 조회
- **CountByUserId**: 사용자별 공유 링크 수 조회
- **FindPopularLinks**: 접근 횟수 기준 인기 링크

### 6.3 영속성 전략 수립

#### 데이터베이스 설계
```sql
-- 공유 링크 테이블
CREATE TABLE share_links (
    share_token UUID PRIMARY KEY,
    card_id UUID NOT NULL,
    user_id UUID NOT NULL,
    share_url VARCHAR(500) NOT NULL,
    expiration_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    access_count INTEGER DEFAULT 0,
    
    INDEX idx_card_id (card_id),
    INDEX idx_user_id (user_id),
    INDEX idx_expiration_date (expiration_date),
    INDEX idx_created_at (created_at)
);

-- Open Graph 메타데이터 테이블
CREATE TABLE open_graph_metadata (
    share_token UUID PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    image_url VARCHAR(1000),
    site_name VARCHAR(100) NOT NULL,
    site_description VARCHAR(200),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    FOREIGN KEY (share_token) REFERENCES share_links(share_token) ON DELETE CASCADE
);
```

#### 인덱스 전략
- **share_token**: 기본키, 가장 빈번한 조회
- **card_id**: 카드별 공유 링크 조회
- **expiration_date**: 만료된 링크 배치 정리
- **created_at**: 최근 링크 조회, 통계 분석

#### 캐싱 전략
- **Redis 캐싱**: 활성 공유 링크 (TTL: 1시간)
- **캐시 키**: `share_link:{token}`
- **캐시 무효화**: 링크 만료 시, 접근 횟수 업데이트 시

## 7. 정책 및 명세 설계

### 7.1 비즈니스 정책 식별

#### ShareLinkExpirationPolicy (개선됨)
**정책**: 공유 링크는 생성일로부터 7일 후 자정에 만료
```
규칙:
- 만료 시간 = 생성일 + 7일 후 00:00:00 UTC
- 예: 2024-01-01 15:30 생성 → 2024-01-08 00:00:00 만료
- 접근 시점에 현재 날짜와 만료 날짜 비교 (DATE 함수 사용)
- 배치 정리: 매일 자정 1회 실행으로 충분
- 사용자 표시: "7일간 유효" (직관적)
```

**개선 이유:**
- 배치 작업 최소화 (1일 1회)
- 구현 단순화 (시간 계산 불필요)
- 사용자 친화적 (일 단위 이해 쉬움)

#### DuplicatePreventionPolicy  
**정책**: 동일한 YouTube URL은 사용자당 하나만 저장
```
규칙:
- YouTube URL 정규화 후 비교
- 쿼리 파라미터 제거 후 비교
- 사용자별 중복 확인
- 중복 시도 시 기존 카드 정보 반환
```

#### AnonymousAccessPolicy
**정책**: 유효한 공유 링크는 인증 없이 접근 가능
```
규칙:
- 토큰만으로 접근 허용
- 만료되지 않은 링크만 접근 가능
- 메타데이터는 항상 제공 (만료된 링크도)
- 접근 로그 기록 (통계용)
```

#### AutoSavePolicy
**정책**: 로그인된 회원의 공유 카드 자동 저장
```
규칙:
- 인증된 사용자만 자동 저장
- "공유받은 카드" 카테고리에 저장
- 중복 확인 후 저장
- 원본과 독립적인 복사본 생성
```

### 7.2 명세 패턴 적용

#### ShareLinkValidSpecification
```
목적: 공유 링크의 유효성 검증
조건:
- 토큰이 존재함
- 만료되지 않음 (현재 날짜 <= 만료 날짜)
- 참조하는 카드가 존재함

구현:
- IsSatisfiedBy(shareLink: ShareLink): Boolean
- GetFailureReason(): String
```

#### ExpiredLinkSpecification (개선됨)
```
목적: 만료된 링크 식별
조건:
- 현재 날짜 > 만료 날짜 (DATE 비교)
- 생성 후 7일 경과

구현:
- IsSatisfiedBy(shareLink: ShareLink): Boolean
- IsExpiredOnDate(checkDate: Date): Boolean
```

### 7.3 유효성 검증 규칙 정의

#### ExpirationDate 검증 (개선됨)
```
규칙:
- UTC 기준 Date (시간 정보 00:00:00)
- 생성일보다 미래
- 생성일 + 7일과 정확히 일치
- null 불허

구현 예시:
- 생성: 2024-01-01 15:30:45
- 만료: 2024-01-08 00:00:00
- 검증: DATE(NOW()) > DATE('2024-01-08')

오류 코드:
- SHARE_004: Invalid expiration date
```

## 8. 통합 및 검증

### 8.1 다른 Unit과의 통합 포인트 확인

#### Unit1 (Authentication) 통합
- **통합 포인트**: 사용자 인증 상태 확인
- **API**: `GET /api/profile` (토큰 검증)
- **데이터 흐름**: JWT 토큰 → UserId 추출
- **오류 처리**: 인증 실패 시 익명 사용자로 처리

#### Unit2 (Category) 통합
- **통합 포인트**: "공유받은 카드" 카테고리 관리
- **API**: `GET /api/categories`, `POST /api/categories`
- **데이터 흐름**: 카테고리 존재 확인 → 없으면 생성
- **시스템 카테고리**: `name="공유받은 카드", type="SYSTEM"`

#### Unit3 (Card) 통합
- **통합 포인트**: 원본 카드 조회, 새 카드 생성, 중복 확인
- **API**: `GET /api/cards/:id`, `POST /api/cards`
- **데이터 흐름**: 
  - 공유 링크 생성: CardId → Card 정보 조회
  - 자동 저장: Card 정보 → 새 Card 생성
  - 중복 확인: YouTube URL → 기존 Card 검색

### 8.2 Integration Contract 업데이트 완료

#### 기존 API 확인
- Unit5 API가 이미 integration_contract.md에 정의됨
- 설계한 도메인 모델과 일치함
- 추가 변경 불필요

### 8.3 오류 코드 추가 완료

#### 새로 추가된 오류 코드
```
SHARE_003: Invalid share token format
SHARE_004: Invalid expiration date  
SHARE_005: Invalid share URL format
SHARE_006: Invalid metadata format
SHARE_007: Share link creation failed
SHARE_008: Card not shareable
SHARE_009: Share link access denied
SHARE_010: Metadata generation failed
```

### 8.4 설계 일관성 검증

#### 다른 Unit과의 일관성 확인
✅ **Unit1**: UserId 참조 방식 일치  
✅ **Unit2**: 시스템 카테고리 패턴 일치  
✅ **Unit3**: CardId 참조, YouTube URL 처리 방식 일치  
✅ **Unit4**: 중복 저장 방지 로직 일치

#### 아키텍처 패턴 일관성
✅ **애그리게이트 설계**: 단일 루트, 명확한 경계  
✅ **값 객체 활용**: 도메인 개념 캡슐화  
✅ **도메인 서비스**: 복잡한 비즈니스 로직 분리  
✅ **이벤트 기반**: 다른 Unit과 동일한 이벤트 패턴  
✅ **리포지토리**: 표준 인터페이스 패턴

#### 데이터베이스 설계 일관성
✅ **UUID 식별자**: 다른 Unit과 동일  
✅ **타임스탬프**: created_at, updated_at 패턴 일치  
✅ **인덱스 전략**: 조회 패턴 기반 최적화  
✅ **외래키 제약**: 참조 무결성 보장

## 설계 완료 요약

Unit5 Card Sharing 도메인 모델 설계가 완료되었습니다.

### 핵심 구성 요소
- **1개 애그리게이트**: ShareLinkAggregate
- **2개 엔티티**: ShareLink, OpenGraphMetadata  
- **3개 값 객체**: ShareToken, ShareUrl, ExpirationDate
- **3개 도메인 서비스**: ShareLinkCreationService, CardDuplicationCheckService, SharedCardSaveService
- **5개 도메인 이벤트**: ShareLinkCreated, ShareLinkAccessed, ShareLinkExpired, SharedCardSaved, SharedCardDuplicateAttempted
- **2개 리포지토리**: ShareLinkRepository, OpenGraphMetadataRepository
- **4개 정책**: ExpirationPolicy, DuplicatePreventionPolicy, AnonymousAccessPolicy, AutoSavePolicy

### 주요 특징
- **메신저 링크 미리보기 지원** (Open Graph 메타데이터)
- **일 단위 만료 정책** (배치 작업 최소화)
- **익명 접근 지원** (인증 없는 공유 카드 조회)
- **자동 저장 기능** (로그인 회원 대상)
- **중복 방지** (YouTube URL 기준)
- **독립적 복사본** (원본과 분리된 새 카드)
