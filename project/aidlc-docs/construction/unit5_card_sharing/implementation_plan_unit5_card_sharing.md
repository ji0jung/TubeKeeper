# Unit5: Card Sharing - 구현 계획

## 개요
Unit5 Card Sharing의 프로덕션 레벨 구현 계획입니다. 도메인 주도 설계와 헥사고날 아키텍처를 기반으로 확장성이 높은 이벤트 기반 시스템을 구현합니다.

## 구현 단계

### 1단계: 프로젝트 구조 및 기본 설정
- [x] 1.1 프로젝트 디렉터리 구조 생성 (헥사고날 아키텍처)
- [x] 1.2 의존성 설정 (requirements.txt, pyproject.toml)
- [x] 1.3 환경 설정 파일 작성 (.env, settings.py)
- [x] 1.4 Docker 설정 (Dockerfile, docker-compose.yml) - 포트 8005 사용
- [x] 1.5 데이터베이스 마이그레이션 스크립트 작성

### 2단계: Domain Layer 구현
- [x] 2.1 값 객체(Value Objects) 구현
  - [x] ShareToken (UUID 기반 공유 토큰)
  - [x] ShareUrl, ExpirationDate, ShareStatus
  - [x] MetadataTitle, MetadataDescription, MetadataImage
- [x] 2.2 엔티티(Entities) 구현
  - [x] ShareLink 엔티티 (애그리게이트 루트)
  - [x] SharedCardMetadata 엔티티
- [x] 2.3 애그리게이트(Aggregate) 구현
  - [x] ShareLinkAggregate (비즈니스 규칙 및 불변성 보장)
- [x] 2.4 도메인 이벤트(Domain Events) 구현
  - [x] ShareLinkCreated, ShareLinkAccessed, SharedCardSaved 등
- [x] 2.5 도메인 서비스(Domain Services) 구현
  - [x] ShareLinkExpirationChecker
  - [x] DuplicateCardChecker
  - [x] MetadataGenerator (인터페이스)
- [x] 2.6 리포지토리 인터페이스 정의
  - [x] ShareLinkRepository 추상 클래스

### 3단계: Application Layer 구현
- [x] 3.1 Command/Query 객체 구현
  - [x] CreateShareLinkCommand, AccessShareLinkQuery
  - [x] SaveSharedCardCommand
- [x] 3.2 Use Case 구현
  - [x] CreateShareLinkUseCase (공유 링크 생성)
  - [x] GetSharedCardUseCase (공유 카드 조회)
  - [x] SaveSharedCardUseCase (공유 카드 저장)
- [x] 3.3 Application Service 구현
  - [x] ShareLinkApplicationService (유스케이스 조정)
- [x] 3.4 DTO 클래스 구현
  - [x] CreateShareLinkDto, SharedCardDto, SaveSharedCardDto
- [ ] 3.5 이벤트 핸들러 구현
  - [ ] ShareLinkAccessHandler
  - [ ] SharedCardSaveHandler

### 4단계: Infrastructure Layer 구현
- [x] 4.1 PostgreSQL 리포지토리 구현
  - [x] PostgreSQLShareLinkRepository (ShareLinkRepository 구현)
  - [x] 데이터베이스 연결 및 세션 관리
- [x] 4.2 캐싱 시스템 구현
  - [x] RedisShareLinkCache (공유 링크 캐싱)
  - [x] 만료 시간 자동 처리 (Redis TTL)
- [ ] 4.3 메시징 시스템 구현
  - [ ] RedisEventPublisher (공유 이벤트 발행)
  - [ ] 이벤트 핸들러 등록 및 관리
- [ ] 4.4 외부 서비스 통합
  - [ ] CardService 클라이언트 (Unit3 연동)
  - [ ] CategoryService 클라이언트 (Unit2 연동)
  - [ ] AuthenticationService 클라이언트 (Unit1 연동)

### 5단계: Presentation Layer 구현
- [x] 5.1 REST API 컨트롤러 구현
  - [x] ShareController (공유 링크 생성/조회 엔드포인트)
  - [x] 표준 응답 형식 준수 (`{success, data, message}`)
  - [x] 요청/응답 DTO 정의
- [x] 5.2 미들웨어 구현
  - [x] AuthenticationMiddleware (JWT 토큰 검증)
  - [x] ErrorHandlingMiddleware (표준 오류 응답 형식)
  - [x] LoggingMiddleware (요청/응답 로깅)
  - [x] RateLimitMiddleware (레이트 리미팅)
- [x] 5.3 Open Graph 메타데이터 처리
  - [x] MetadataController (크롤러 요청 처리)
  - [x] User-Agent 기반 응답 분기 (JSON vs HTML)
  - [x] HTML 템플릿 생성 (Open Graph 태그 포함)
- [ ] 5.4 API 문서화
  - [ ] OpenAPI/Swagger 스펙 작성
  - [ ] 표준 응답 형식 문서화

### 6단계: 테스트 구현
- [x] 6.1 단위 테스트 작성
  - [x] Domain Layer 테스트 (값 객체, 엔티티, 애그리게이트)
  - [x] Application Layer 테스트 (유스케이스)
  - [x] Infrastructure Layer 테스트 (리포지토리, 캐시)
- [x] 6.2 통합 테스트 작성
  - [x] API 엔드포인트 테스트 (표준 응답 형식 검증)
  - [x] 데이터베이스 통합 테스트
  - [x] Redis 캐싱 테스트
  - [x] 레이트 리미팅 테스트
- [x] 6.3 이벤트 기반 테스트 작성
  - [x] 공유 링크 생성/접근 이벤트 테스트
  - [x] 메시징 시스템 테스트
- [x] 6.4 Open Graph 메타데이터 테스트
  - [x] 크롤러 요청 시뮬레이션 테스트 (User-Agent 기반)
  - [x] 메타데이터 생성 정확성 테스트
  - [x] HTML 응답 vs JSON 응답 분기 테스트
- [x] 6.5 오류 처리 테스트
  - [x] 만료된 링크 접근 테스트 (SHARE_001)
  - [x] 존재하지 않는 링크 테스트 (SHARE_002)
  - [x] 잘못된 토큰 형식 테스트 (SHARE_003)
  - [x] 레이트 리미팅 테스트 (SHARE_011)
- [x] 6.6 JWT 토큰 기반 인증 테스트
  - [x] Unit3 방식과 동일한 JWT 토큰 생성
  - [x] 인증 필요 API 테스트
  - [x] 인증 실패 시나리오 테스트

### 7단계: 로컬 Docker 테스트 (Unit5 단독)
- [x] 7.1 Docker Compose 환경 구성 (Unit5 전용)
  - [x] PostgreSQL, Redis 설정 (포트 5435, 6381)
  - [x] Unit5 애플리케이션 컨테이너 설정 (포트 8005)
- [x] 7.2 Unit5 단독 통합 테스트
  - [x] 전체 플로우 테스트 (공유 링크 생성 → 조회 → 저장)
  - [x] 만료 링크 처리 테스트
  - [x] Open Graph 메타데이터 테스트
- [x] 7.3 모니터링 및 로깅 설정
  - [x] 애플리케이션 로그 설정
  - [x] 헬스 체크 엔드포인트 (`/health`)
  - [x] 서비스 정보 엔드포인트 (`/`)
- [x] 7.4 테스트 데이터 관리
  - [x] 테스트 시작 전 기존 데이터 정리
  - [x] 테스트 성공 시 생성된 데이터 자동 삭제
  - [x] 테스트 실패 시 디버깅용 데이터 보존
- [x] 7.5 자동화 스크립트
  - [x] Docker 테스트 실행 스크립트 (`docker_test.sh`)
  - [x] 데이터 정리 기능 (`TestDataManager`)
  - [x] 포트 충돌 방지 (Unit2:8002, Unit3:8001, Unit4:8004, Unit5:8005)

### 8단계: Unit3 연동 로컬 테스트
- [ ] 8.1 Unit3 + Unit5 통합 Docker Compose 구성
  - [ ] Unit3 카드 관리 서비스 연동
  - [ ] 공유 PostgreSQL 데이터베이스 설정
  - [ ] 서비스 간 네트워크 설정
- [ ] 8.2 Unit3-Unit5 통합 테스트
  - [ ] 카드 생성 후 공유 링크 생성 테스트
  - [ ] 공유 카드 조회 및 저장 테스트
  - [ ] 중복 저장 방지 테스트
- [ ] 8.3 통합 시나리오 테스트
  - [ ] 카드 생성 → 공유 → 조회 → 저장 전체 플로우
  - [ ] Unit3 서비스 장애 시 Unit5 동작 테스트
  - [ ] 동시성 테스트 (여러 사용자, 여러 공유)

### 9단계: 배포 준비
- [ ] 9.1 프로덕션 환경 설정
  - [ ] 환경별 설정 파일 분리
  - [ ] 시크릿 관리 (AWS Secrets Manager)
- [ ] 9.2 CI/CD 파이프라인 구성
  - [ ] GitHub Actions 워크플로우
  - [ ] 자동 테스트 및 빌드
- [ ] 9.3 AWS 인프라 설정
  - [ ] ECS/Fargate 배포 설정
  - [ ] RDS PostgreSQL 설정
  - [ ] ElastiCache Redis 설정

### 10단계: 배포 및 검증
- [ ] 10.1 스테이징 환경 배포
  - [ ] 스테이징 환경에서 전체 기능 테스트
  - [ ] 외부 서비스 연동 테스트
- [ ] 10.2 프로덕션 배포
  - [ ] 블루-그린 배포 또는 롤링 배포
  - [ ] 배포 후 검증 테스트
- [ ] 10.3 모니터링 및 알림 설정
  - [ ] CloudWatch 알람 설정
  - [ ] 로그 모니터링 설정

## 질문 사항 및 답변

[Question] 공유 링크 생성 시 레이트 리미팅을 어떻게 설정할까요? 사용자당 시간당 몇 개의 링크 생성을 허용할지 결정이 필요합니다.
[Answer] 사용자당 시간당 20개 제한 적용
**이유**: 남용 방지 및 서버 리소스 보호. 정상 사용자에게 충분한 여유를 제공하면서도 남용을 효과적으로 차단.

[Question] 만료된 공유 링크의 물리적 삭제 주기를 어떻게 설정할까요? 배치 작업으로 처리할지, 접근 시점에 처리할지 결정이 필요합니다.
[Answer] 접근 시점에 검증 + 매일 새벽 2시 배치 정리
**이유**: 실시간 정확성과 성능의 균형. 접근 시점 검증으로 정확성 보장, 배치로 DB 정리하여 성능 유지.

[Question] Open Graph 메타데이터에서 앱 홍보 문구는 어떻게 설정할까요? 고정 문구를 사용할지, 설정 가능하게 할지 결정이 필요합니다.
[Answer] 고정 문구 사용: "YouTube Keeper - AI로 정리하는 나만의 영상 컬렉션"
**이유**: 구현 단순성과 일관된 브랜딩. 설정 기능은 복잡도 대비 효과가 낮음.

[Question] 공유 카드 저장 시 "공유받은 카드" 카테고리가 없는 경우 자동 생성할까요, 아니면 오류를 반환할까요?
[Answer] 자동 생성
**이유**: 사용자 경험 향상. 공유 기능이 원활하게 동작하도록 필요한 카테고리를 자동으로 준비.

[Question] 공유 링크 접근 통계를 수집할까요? (접근 횟수, 접근 시간, 접근자 정보 등)
[Answer] 기본 통계만 수집 (접근 횟수, 접근 시간)
**이유**: 개인정보 보호를 위해 IP나 사용자 식별 정보는 수집하지 않고, 서비스 개선을 위한 최소한의 통계만 수집. 

## 기술 설정 및 정책

### API 응답 형식 (표준 준수)
**성공 응답**:
```json
{
  "success": true,
  "data": { ... },
  "message": "Success message"
}
```

**오류 응답**:
```json
{
  "success": false,
  "error": {
    "code": "SHARE_XXX",
    "message": "Error description",
    "details": { ... }
  }
}
```

### API 엔드포인트 (표준 준수 + 요구사항 반영)
```
POST /api/cards/:id/share
- Response: { success: true, data: { shareUrl, shareToken, expiresAt }, message }

GET /api/shared/:shareId  
- Response: { success: true, data: { card: {...}, isExpired, expiresAt }, message }
- 크롤러 요청 시: HTML with Open Graph meta tags

POST /api/shared/:shareId/save
- Response: { success: true, data: { newCard?, alreadyExists? }, message }
```

### Redis 캐싱 정책
- **캐시 키**: `share_link:{share_token}`
- **TTL**: 7일 (공유 링크 만료 시간과 동일)
- **캐시 데이터**: 카드 기본 정보 + 메타데이터
- **캐시 미스**: PostgreSQL에서 조회 후 캐시 저장

### 공유 링크 생성 정책
- **토큰 형식**: UUID4 (36자리)
- **URL 형식**: `/shared/{token}`
- **만료 시간**: 생성일로부터 정확히 7일
- **중복 처리**: 동일 카드 여러 번 공유 시 새 링크 생성

### Open Graph 메타데이터 정책
- **og:title**: 카드 제목
- **og:description**: AI 요약의 첫 2줄 (최대 160자)
- **og:image**: 카드 썸네일 이미지
- **og:url**: 공유 링크 URL
- **og:site_name**: "YouTube Keeper"
- **og:type**: "article"
- **홍보 문구**: "YouTube Keeper - AI로 정리하는 나만의 영상 컬렉션"

### 레이트 리미팅 정책
- **공유 링크 생성**: 사용자당 시간당 20개
- **공유 링크 접근**: IP당 분당 60회
- **Redis 기반 슬라이딩 윈도우 방식**

### 만료 처리 정책
- **실시간 검증**: 접근 시점에 `created_at + 7일` 비교
- **배치 정리**: 매일 새벽 2시, 만료된 링크 물리 삭제
- **캐시 만료**: Redis TTL로 자동 처리

## 예상 소요 시간

- 1-2단계: 2-3일 (프로젝트 설정 및 도메인 레이어)
- 3-4단계: 3-4일 (애플리케이션 및 인프라 레이어)
- 5단계: 2-3일 (프레젠테이션 레이어 + Open Graph)
- 6단계: 2-3일 (테스트 + 표준 응답 형식 검증)
- 7단계: 1-2일 (Unit5 단독 Docker 테스트)
- 8단계: 1-2일 (Unit3 연동 테스트)
- 9단계: 2-3일 (배포 준비)
- 10단계: 1-2일 (배포 및 검증)

**총 예상 소요 시간: 14-22일**

## 주요 구현 특징

### 표준 준수
- **응답 형식**: `{success, data, message}` 표준 준수
- **오류 코드**: 기존 SHARE_001~010 + 신규 SHARE_011~013 추가
- **인증**: JWT Bearer 토큰 기반 (Unit1 연동)

### 요구사항 반영
- **메신저 미리보기**: Open Graph 메타데이터 지원
- **User-Agent 감지**: 크롤러 vs 일반 사용자 구분
- **자동 저장**: 로그인 사용자의 "공유받은 카드" 카테고리 자동 저장
- **중복 방지**: YouTube URL 기준 중복 검사
- **만료 처리**: 7일 자동 만료 + 실시간 검증

### 성능 최적화
- **Redis 캐싱**: 공유 링크 조회 성능 향상
- **레이트 리미팅**: 남용 방지 (시간당 20개)
- **배치 정리**: 만료된 링크 자동 정리

### Unit3 연동
- **카드 정보 조회**: Unit3 API 호출로 원본 카드 정보 획득
- **카드 생성**: Unit3 API 호출로 새 카드 생성 (독립적 복사본)
- **권한 검증**: Unit3을 통한 카드 접근 권한 확인

---

**검토 및 승인 요청**: 위 구현 계획을 검토해주시고, 질문 사항에 대한 답변이 적절한지 확인해주세요. 특히 다음 사항들을 확인해주세요:

1. **표준 응답 형식 준수**: `{success, data, message}` 형식이 모든 API에 적용되었는지
2. **오류 코드 추가**: SHARE_011~013 오류 코드가 적절한지
3. **Open Graph 구현**: 메신저 미리보기 요구사항이 충족되는지
4. **Unit3 연동 방식**: 카드 조회/생성 API 호출 방식이 적절한지
5. **레이트 리미팅 정책**: 시간당 20개 제한이 적절한지

승인 후 단계별로 구현을 진행하겠습니다.
