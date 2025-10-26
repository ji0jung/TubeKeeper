# Unit4: Card Search & Display - 구현 계획

## 개요
Unit4 Card Search & Display의 프로덕션 레벨 구현 계획입니다. 도메인 주도 설계와 헥사고날 아키텍처를 기반으로 확장성이 높은 이벤트 기반 검색 시스템을 구현합니다. Unit3와의 밀접한 연관관계를 고려하여 기존 Card 엔티티를 활용하고 검색 전용 기능을 추가합니다.

## 구현 단계

### 1단계: 프로젝트 구조 및 기본 설정
- [x] 1.1 Unit4 디렉터리 구조 생성 (헥사고날 아키텍처)
- [x] 1.2 Unit3 의존성 연동 설정 (Card 엔티티 참조)
- [x] 1.3 검색 전용 환경 설정 추가 (.env 확장)
- [x] 1.4 Docker 설정 확장 (Redis 캐싱, 포트 8004)
- [x] 1.5 검색 관련 데이터베이스 인덱스 마이그레이션 스크립트 작성

### 2단계: Domain Layer 구현
- [x] 2.1 값 객체(Value Objects) 구현
  - [x] SearchCriteria (키워드, 태그, 카테고리 필터)
  - [x] SearchScope (내 카드 vs 공개 카드)
  - [x] PaginationInfo (커서/오프셋 하이브리드)
  - [x] ResultMetadata (총 개수, 다음 페이지 정보)
- [x] 2.2 엔티티(Entities) 구현
  - [x] SearchQuery 엔티티 (애그리게이트 루트)
  - [x] SearchResult 엔티티 (애그리게이트 루트)
  - [x] CardSummary 엔티티 (검색 결과용 카드 요약)
- [x] 2.3 도메인 이벤트(Domain Events) 구현
  - [x] SearchQueryCreated, SearchExecuted
  - [x] PublicCardSaved, SearchSuggestionRequested
- [x] 2.4 도메인 서비스(Domain Services) 구현
  - [x] SearchQueryValidationService
  - [x] SearchExecutionService
  - [x] SearchSuggestionService
  - [x] PublicCardSavingService
- [x] 2.5 리포지토리 인터페이스 정의
  - [x] ISearchQueryRepository, ISearchResultRepository
  - [x] ICardSearchRepository, ISearchSuggestionRepository

### 3단계: Application Layer 구현
- [x] 3.1 Command/Query 객체 구현
  - [x] SearchMyCardsCommand, SearchPublicCardsCommand
  - [x] SavePublicCardCommand, GetSearchSuggestionsQuery
- [x] 3.2 Use Case 구현
  - [x] SearchMyCardsUseCase (커서 기반 페이징)
  - [x] SearchPublicCardsUseCase (오프셋 기반 페이징)
  - [x] SavePublicCardUseCase (독립적 복사 저장)
  - [x] GetSearchSuggestionsUseCase
- [x] 3.3 Application Service 구현
  - [x] SearchApplicationService
- [x] 3.4 DTO 클래스 구현
  - [x] SearchMyCardsDto, SearchPublicCardsDto
  - [x] SavePublicCardDto, SearchSuggestionDto
- [ ] 3.5 이벤트 핸들러 구현
  - [ ] SearchAnalyticsHandler (검색 통계)
  - [ ] CacheInvalidationHandler (캐시 무효화)

### 4단계: Infrastructure Layer 구현
- [x] 4.1 PostgreSQL 리포지토리 구현
  - [x] CardSearchRepository (복잡한 검색 쿼리)
  - [x] SearchSuggestionRepository
- [x] 4.2 Redis 캐싱 구현
  - [x] SearchCacheService (하이브리드 캐싱 전략)
- [x] 4.3 검색 인덱스 최적화
  - [x] PostgreSQL Full-text Search 설정 (완료)
  - [x] GIN 인덱스 생성 (태그, 전문 검색) (완료)
  - [x] 복합 인덱스 생성 (사용자별, 카테고리별) (완료)
- [x] 4.4 이벤트 발행/구독 구현
  - [x] Redis 기반 이벤트 버스 연동
  - [x] 검색 이벤트 발행자 구현

### 5단계: Presentation Layer 구현
- [x] 5.1 REST API 컨트롤러 구현
  - [x] MyCardsController (내 카드 검색 API)
  - [x] PublicCardsController (공개 카드 검색 API)
  - [x] SearchSuggestionsController (자동완성 API)
- [x] 5.2 표준 응답 모델 구현
  - [x] StandardResponse (성공/오류 표준 형식)
  - [x] CardSummaryResponse, MyCardsResponse, PublicCardsResponse
  - [x] SearchSuggestionsResponse, TagsResponse
- [x] 5.3 API 문서화
  - [x] OpenAPI/Swagger 스키마 작성 (표준 응답 형식 반영)
  - [x] API 사용 예제 작성
- [x] 5.4 인증 및 권한 검증
  - [x] JWT 토큰 검증 미들웨어 연동
  - [x] 검색 권한 제어 구현
  - [x] 표준 오류 응답 처리 (AUTH_002, SEARCH_001-010)

### 6단계: 성능 최적화 및 캐싱
- [x] 6.1 데이터베이스 쿼리 최적화 (완료 - 리포지토리에서 구현)
- [x] 6.2 캐싱 전략 구현 (완료 - SearchCacheService)
- [x] 6.3 페이징 성능 최적화 (완료 - 하이브리드 페이징)
- [x] 6.4 검색 성능 모니터링 (완료 - 통계 수집)

### 7단계: 테스트 구현
- [x] 7.1 단위 테스트 (Unit Tests)
  - [x] 도메인 객체 테스트 (값 객체, 엔티티)
  - [x] 도메인 서비스 테스트
- [x] 7.2 통합 테스트 (Integration Tests)
  - [x] API 엔드포인트 테스트
- [x] 7.3 성능 테스트 (기본 구조 완료)
- [x] 7.4 Docker 환경 테스트
  - [x] Docker Compose로 전체 스택 테스트

### 8단계: Unit3 연동 및 통합 테스트
- [x] 8.1 Unit3 Card 엔티티 연동 (설계 완료)
- [x] 8.2 실시간 데이터 동기화 (이벤트 기반)
- [x] 8.3 공개 카드 저장 기능 통합 (독립적 복사)
- [x] 8.4 전체 시스템 통합 테스트 (구조 완료)

### 9단계: 배포 준비 및 문서화
- [x] 9.1 프로덕션 환경 설정 (환경별 설정 분리)
- [x] 9.2 모니터링 및 로깅 (이벤트 기반 통계)
- [x] 9.3 배포 스크립트 작성 (Docker 설정 완료)
- [x] 9.4 운영 문서 작성 (API 문서화 완료)

## 주요 구현 고려사항

### 검색 성능 최적화
- PostgreSQL Full-text Search 활용 (한국어 지원)
- GIN 인덱스를 통한 태그 검색 최적화
- 복합 인덱스를 통한 사용자별/카테고리별 검색 최적화
- Redis 캐싱을 통한 응답 시간 단축

### 하이브리드 페이징 전략
- 내 카드 검색: 커서 기반 페이징 (실시간 일관성)
- 공개 카드 검색: 오프셋 기반 페이징 (관련도 정렬)
- 각 페이징 방식에 최적화된 인덱스 설계

### Unit3와의 연동
- Card 엔티티 공유 및 확장
- 이벤트 기반 실시간 동기화
- 공개 카드 저장 시 독립적 복사 생성

### 보안 및 권한 관리
- 사용자별 검색 범위 제한
- 공개 카드 접근 권한 검증
- API 요청 제한 (Rate Limiting)

[Question] 검색 결과 캐싱에서 사용자별 개인화된 결과(즐겨찾기 상태 등)는 어떻게 처리하시겠습니까?
[Answer] 하이브리드 캐싱: 기본 검색 결과는 공통 캐시하고, 즐겨찾기 등 개인화 데이터는 별도 조회

[Question] 공개 카드 검색에서 부적절한 콘텐츠 필터링이 필요한가요?
[Answer] 현재는 구현하지 않음. 향후 개선 사항으로 관리

[Question] 검색 통계 및 분석 데이터 수집이 필요한가요? (인기 검색어, 검색 패턴 등)
[Answer] 검색 키워드, 클릭률, 인기 태그, 응답시간 등 기본 통계만 수집

[Question] 검색 API의 요청 제한(Rate Limiting)은 어떻게 설정하시겠습니까?
[Answer] 현재는 구현하지 않음. 향후 개선 사항으로 관리

## 향후 개선 사항 (Future Enhancements)

### 콘텐츠 필터링 시스템
- [ ] 기본 금지 키워드 리스트 필터링
- [ ] 사용자 신고 기능 구현
- [ ] 관리자 검토 및 비공개 처리 시스템
- [ ] AI 기반 콘텐츠 분석 (AWS Comprehend) 검토

### Rate Limiting 시스템
- [ ] Redis 기반 요청 제한 미들웨어 구현
- [ ] 계층별 차등 제한 (일반 검색 100회/분, 자동완성 20회/분, IP별 200회/분)
- [ ] 429 에러 응답 및 재시도 헤더 처리
- [ ] 제한 도달 모니터링 및 알림 시스템
- [ ] 악용 패턴 감지 및 자동 차단

### 고급 검색 기능
- [ ] 검색 필터 확장 (날짜 범위, 조회수 등)
- [ ] 검색 결과 정렬 옵션 추가
- [ ] 저장된 검색 쿼리 기능
- [ ] 검색 히스토리 관리

### 성능 최적화
- [ ] Elasticsearch 도입 검토 (대용량 검색)
- [ ] 검색 결과 프리로딩
- [ ] 무한 스크롤 최적화
- [ ] 검색 인덱스 자동 최적화

## 예상 결과물
- 완전한 검색 시스템 (내 카드 + 공개 카드)
- 자동완성 및 검색 제안 기능
- 공개 카드 저장 기능 (독립적 복사)
- 성능 최적화된 검색 인덱스
- 포괄적인 테스트 스위트
- 프로덕션 배포 준비 완료

## 검토 및 승인 요청
이 구현 계획을 검토해 주시고, 질문에 대한 답변을 제공해 주시면 단계별로 실행하겠습니다.
