# Unit3: Card Creation & Management - 도메인 모델

## 개요
Unit3는 유튜브 링크를 기반으로 카드를 생성하고 편집하는 기능을 담당하는 독립적인 단위입니다. 도메인 주도 설계(DDD)를 사용하여 전술적 구성 요소들을 설계했습니다.

## 도메인 전문가 언어 (Ubiquitous Language)

### 핵심 용어
- **Card**: 유튜브 영상 정보를 저장하는 기본 단위
- **YouTube URL**: 유튜브 영상의 고유 식별자
- **Metadata Extraction**: 유튜브 API를 통한 영상 정보 수집
- **Thumbnail**: 영상 썸네일 이미지
- **Card Status**: 카드의 현재 처리 상태
- **Duplicate Check**: 동일 URL 카드 존재 여부 확인
- **Category Assignment**: 카드를 특정 카테고리에 할당
- **Favorite**: 중요한 카드 표시 기능

## 애그리게이트 설계

### CardAggregate
**애그리게이트 루트**: Card 엔티티
**식별자**: CardId (UUID)
**책임**: 카드 생명주기 관리, 비즈니스 규칙 적용, 상태 전이 제어

**경계 내부:**
- Card (애그리게이트 루트)
- VideoMetadata (엔티티)
- YouTubeUrl, VideoTitle, Thumbnail, Tags, Memo, CardStatus (값 객체)

**경계 외부 (참조만):**
- UserId (Unit1에서 관리)
- CategoryId (Unit2에서 관리)

**불변성 규칙:**
1. **URL 유일성**: 동일한 YouTubeUrl을 가진 Card는 시스템에 하나만 존재
2. **상태 일관성**: CardStatus와 VideoMetadata 상태가 일치해야 함
3. **카테고리 필수**: CategoryId는 항상 유효한 값이어야 함
4. **메타데이터 완전성**: COMPLETED 상태일 때 VideoMetadata가 완전해야 함

## 엔티티 설계

### Card (애그리게이트 루트)
```
속성:
- CardId: UUID (식별자)
- UserId: UUID (외부 참조)
- CategoryId: UUID (외부 참조)
- YouTubeUrl: YouTubeUrl (값 객체)
- VideoMetadata: VideoMetadata (엔티티)
- Memo: Memo (값 객체)
- Tags: Tags (값 객체)
- Status: CardStatus (값 객체)
- IsFavorite: bool (즐겨찾기 여부)
- FavoritedAt: DateTime (즐겨찾기 설정 시간, 선택적)
- IsPublic: bool (공개 여부, 기본값: false)
- CreatedAt: DateTime
- UpdatedAt: DateTime

행위:
- Create(): 새 카드 생성
- UpdateMetadata(): 메타데이터 업데이트
- UpdateMemo(): 메모 수정
- UpdateTags(): 태그 수정
- ChangeCategory(): 카테고리 변경
- ToggleFavorite(): 즐겨찾기 토글
- TogglePublic(): 공개 설정 토글
- UpdateMetadata(): 메타데이터 업데이트 후 완료 상태로 변경
```

### VideoMetadata (엔티티)
```
속성:
- VideoTitle: VideoTitle (값 객체)
- Thumbnail: Thumbnail (값 객체)
- Thumbnail: Thumbnail (값 객체)
- Duration: int (초)
- PublishedAt: DateTime

행위:
- UpdateFromYouTube(): YouTube API 데이터로 업데이트
```

## 값 객체 설계

### YouTubeUrl
```
속성:
- Value: string

제약사항:
- YouTube URL 형식 검증
- 표준 형식으로 정규화

메서드:
- IsValid(): boolean
- Normalize(): YouTubeUrl
- GetVideoId(): string
```

### VideoTitle
```
속성:
- Value: string

제약사항:
- 최대 200자
- 빈 문자열 불허

메서드:
- Truncate(length): VideoTitle
```

### Thumbnail
```
속성:
- S3Url: string (S3 저장 URL)
- YouTubeUrl: string (원본 YouTube URL 또는 기본 썸네일 URL)
- Source: ThumbnailSource (S3 | YOUTUBE | DEFAULT)

메서드:
- GetDisplayUrl(): string (표시용 URL 반환)
- IsDefault(): bool (기본 썸네일 여부 확인)

기본 썸네일:
- 480x360 회색 SVG 이미지
- "비디오 없음" 텍스트 포함
- data:image/svg+xml 형식
``` (환경변수 기반 URL 반환)
- IsS3Available(): boolean
```

### Script
```
속성:
- Content: string
- Language: string
### Tags
```
속성:
- Items: List<string>

제약사항:
- 최대 20개
- 각 태그 최대 50자

메서드:
- Add(tag): void
- Remove(tag): void
- Contains(tag): boolean
```

### Memo
```
속성:
- Content: string

제약사항:
- 최대 2,000자

메서드:
- IsEmpty(): boolean
- Update(content): void
```

### CardStatus
```
값:
- CREATING: 카드 생성 중
- METADATA_EXTRACTED: 메타데이터 추출 완료
- SUMMARY_GENERATING: 요약 생성 중
- COMPLETED: 완료
- FAILED: 실패

상태 전이:
- CREATING → METADATA_EXTRACTED → SUMMARY_GENERATING → COMPLETED
- CREATING → FAILED (메타데이터 추출 실패)
- SUMMARY_GENERATING → COMPLETED (요약 없이)
```

## 도메인 서비스 설계

### YouTubeMetadataExtractor
```
책임: YouTube API 호출, 메타데이터 파싱, 오류 처리

메서드:
- ExtractMetadata(YouTubeUrl): VideoMetadata

예외:
- InvalidYouTubeUrlException: 잘못된 URL
- YouTubeApiException: YouTube API 오류
- YouTubeServerException: YouTube 서버 불안정
```

### AISummaryGenerator
```
책임: AWS Bedrock Claude 호출, 요약 생성, 재시도 로직

메서드:
- GenerateSummaryAsync(Script): Task<Summary>
- ValidateScriptLength(Script): boolean

### CardDuplicationChecker
```
책임: 동일 URL 카드 존재 여부 확인

메서드:
- CheckDuplicate(YouTubeUrl, UserId): boolean
- GetExistingCard(YouTubeUrl, UserId): Card?

성능:
- PostgreSQL 인덱스 활용
- 사용자별 중복 검사
```

### ThumbnailProcessor
```
책임: S3 업로드, URL 생성, 환경변수 기반 소스 선택, 기본 썸네일 제공

메서드:
- ProcessThumbnail(YouTubeUrl): Thumbnail
- UploadToS3(imageData): string
- GetDisplayUrl(Thumbnail): string
- GetDefaultThumbnail(): string (기본 썸네일 URL 반환)

설정:
- THUMBNAIL_SOURCE 환경변수 (S3 | YOUTUBE)
- DEFAULT_THUMBNAIL_URL: 480x360 회색 SVG 이미지

폴백 처리:
- YouTube URL 다운로드 실패 시 기본 썸네일 사용
- S3 업로드 실패 시 기본 썸네일 사용
- 모든 예외 상황에서 기본 썸네일 보장
```

## 도메인 이벤트 설계

### 카드 생성 관련 이벤트
```
CardCreationRequested:
- CardId, UserId, YouTubeUrl, CategoryId
- 발생: 카드 생성 요청 시

CardCreated:
- CardId, UserId, CategoryId, VideoTitle
- 발생: 카드 생성 완료 시
```

### 메타데이터 수집 관련 이벤트
```
YouTubeMetadataExtractionStarted:
- CardId, YouTubeUrl
- 발생: 메타데이터 추출 시작

YouTubeMetadataExtracted:
- CardId, VideoMetadata
- 발생: 메타데이터 추출 완료

YouTubeMetadataExtractionFailed:
- CardId, ErrorType, ErrorMessage
- 발생: 메타데이터 추출 실패
```

### AI 요약 생성 관련 이벤트
```
SummaryGenerationStarted:
- CardId, ScriptLength
- 발생: 요약 생성 시작 (비동기)

SummaryGenerated:
- CardId, Summary
- 발생: 요약 생성 완료

SummaryGenerationFailed:
- CardId, RetryCount, ErrorMessage
- 발생: 요약 생성 실패
```

### 카드 수정/삭제 관련 이벤트
```
CardUpdated:
- CardId, UpdatedFields
- 발생: 메모, 태그, 카테고리 수정

CardDeleted:
- CardId, UserId
- 발생: 카드 삭제
```

## 정책(Policy) 설계

### CardCreationPolicy
```
프로세스:
1. 중복 검사 수행
2. 메타데이터 추출 (동기)
3. 카드 생성
4. 비동기 요약 생성 시작

규칙:
- 카테고리 기본값: 사용자 마지막 선택 카테고리
- 실패 시 적절한 오류 메시지 제공
```

### MetadataExtractionPolicy
```
처리 방식:
- YouTube API 1회 호출
- 실패 시 오류 유형별 메시지 제공

오류 처리:
- 잘못된 URL: "URL에 문제가 있습니다"
- YouTube 서버 오류: "YouTube 서버가 불안정합니다"
- 내부 오류: 1회 재시도 → "서버 장애, 잠시 후 재시도"
```

### SummaryGenerationPolicy
```
처리 방식:
- 비동기 처리, 카드 먼저 생성
- 스크립트 길이 검증 (100,000자 제한)
- 2회 재시도 후 실패 시 요약 없이 완료

상태 표시:
- "요약 생성중" → "요약 완료" or "요약 실패"
```

### ErrorHandlingPolicy
```
원칙:
- 사용자 친화적 메시지 제공
- 복구 가능한 오류는 재시도 옵션 제공
- 로그 기록 및 모니터링
- 부분 실패 허용 (요약 없는 카드 생성)
```

## 리포지토리 설계

### CardRepository 인터페이스
```
메서드:
- Save(Card): void
- FindById(CardId): Card?
- FindByYouTubeUrl(YouTubeUrl, UserId): Card?
- FindByUserId(UserId, pagination): List<Card>
- Delete(CardId): void
- ExistsByYouTubeUrl(YouTubeUrl, UserId): boolean
```

### PostgreSQL 데이터 모델
```sql
CREATE TABLE cards (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id),
    category_id UUID NOT NULL REFERENCES categories(id),
    youtube_url VARCHAR(500) NOT NULL,
    video_title VARCHAR(200),
    thumbnail_s3_url VARCHAR(500),
    thumbnail_youtube_url VARCHAR(500),
    script_content TEXT,
    script_language VARCHAR(10),
    has_script BOOLEAN DEFAULT false,
    summary_content TEXT,
    summary_status VARCHAR(20) DEFAULT 'PENDING',
    summary_retry_count INTEGER DEFAULT 0,
    memo TEXT,
    tags JSONB,
    status VARCHAR(20) NOT NULL,
    duration INTEGER,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 인덱스
CREATE UNIQUE INDEX idx_cards_user_youtube_url ON cards(user_id, youtube_url);
CREATE INDEX idx_cards_user_created ON cards(user_id, created_at DESC);
CREATE INDEX idx_cards_category ON cards(category_id);
CREATE INDEX idx_cards_tags ON cards USING GIN(tags);
```

## 외부 서비스 인터페이스

### IYouTubeApiService
```
메서드:
- GetVideoMetadata(YouTubeUrl): VideoMetadataDto
- GetVideoThumbnail(YouTubeUrl): ThumbnailDto
- GetVideoScript(YouTubeUrl): ScriptDto?

구현:
- YouTube Data API v3 사용
- API 키 기반 인증
- 할당량 관리
```

### IAIService
```
메서드:
- GenerateSummaryAsync(script: string): Task<string>
- ValidateScriptLength(script: string): boolean

구현:
- AWS Bedrock Claude 4.0 사용
- 비동기 처리
- 토큰 제한 관리
```

### ICategoryService
```
메서드:
- ValidateCategoryExists(CategoryId, UserId): boolean
- GetUserLastSelectedCategory(UserId): CategoryId?

통합:
- Unit2 Category Management와 연동
- REST API 호출 또는 직접 DB 접근
```

## 예외 처리 설계

### 도메인 예외 계층
```
CardDomainException (기본 클래스)
├── DuplicateCardException
├── InvalidYouTubeUrlException
├── YouTubeApiException
├── CategoryNotFoundException
├── ScriptTooLongException
└── SummaryGenerationException
```

### 오류 코드 매핑
```
CARD_004: Duplicate card exists
CARD_005: Script too long for summary
CARD_006: Summary generation failed
CARD_007: Thumbnail processing failed
CARD_008: Card creation in progress
CARD_009: Invalid card status transition
```

### 예외 처리 전략
- 도메인 예외 → HTTP 상태 코드 매핑
- 사용자 친화적 오류 메시지
- 로깅 및 모니터링
- 재시도 가능한 오류 구분

## 비즈니스 규칙 요약

### 핵심 제약사항
1. **URL 유일성**: 사용자당 동일한 YouTube URL로는 하나의 카드만 생성 가능
2. **카테고리 필수**: 모든 카드는 반드시 하나의 카테고리에 속해야 함
3. **스크립트 길이 제한**: 최대 100,000자까지 AI 요약 생성 가능
4. **요약 재시도 제한**: 최대 2회까지 재시도 후 실패 시 요약 없이 카드 생성

### 처리 방식
1. **YouTube API**: 동기 처리로 메타데이터 추출
2. **AI 요약**: 비동기 처리로 요약 생성
3. **썸네일**: S3 저장 + 환경변수 기반 소스 선택
4. **오류 처리**: 상황별 적절한 메시지 제공

### 상태 관리
- 카드 상태를 통한 생명주기 관리
- 부분 실패 허용 (요약 없는 카드 생성)
- 사용자에게 진행 상황 표시

## 통합 지점

### Unit1 (Authentication)과의 통합
- UserId를 통한 사용자 식별
- 인증 토큰 검증

### Unit2 (Category Management)와의 통합
- CategoryId를 통한 카테고리 참조
- 카테고리 존재 여부 검증
- 마지막 선택 카테고리 조회

### 외부 서비스와의 통합
- YouTube Data API v3
- AWS Bedrock Claude 4.0
- AWS S3 (썸네일 저장)

이 도메인 모델은 Unit3 Card Creation & Management의 모든 비즈니스 요구사항을 충족하며, DDD의 전술적 패턴을 적절히 적용하여 설계되었습니다.
