# 유튜브 링크 저장 웹 애플리케이션 개발 계획

## 프로젝트 개요

유튜브 링크를 체계적으로 저장, 조회, 공유할 수 있는 웹 애플리케이션 개발

## 개발 단계별 계획

### Phase 1: 프로젝트 초기 설정 및 요구사항 분석

- [x] 1.1 프로젝트 디렉터리 구조 생성 (aidlc-docs/inception/)
- [x] 1.2 사용자 스토리 작성 (user_stories.md)
- [x] 1.3 사용자 스토리를 독립적 단위로 그룹화
- [x] 1.4 각 단위별 상세 문서 작성 (aidlc-docs/inception/units/)
- [x] 1.5 통합 계약(Integration Contract) 정의
- [ ] 1.6 기능 요구사항 명세서 작성

[Question] 사용자 인증 및 회원가입 기능이 필요한가요? 개인 사용자만을 위한 앱인지, 다중 사용자를 지원하는 앱인지 명확히 해주세요.
[Answer] 이메일로 가입 가능하고, 이메일에 코드를 보낸 것을 입력하는 것으로 인증한다. 다중 사용자를 지원하는 앱이다. 로그인 유지 기간은 마지막 사용 시간으로부터 7일이며, 웹앱 사용 시 유지 기간이 자동으로 연장된다.

[Question] "친구에게 링크 공유" 기능은 단순히 카드 정보를 URL로 공유하는 것인지, 아니면 특정 친구에게만 보이는 권한 관리가 필요한 것인지 설명해주세요.
[Answer] 기본은 특정 친구에게 카드 정보를 단순 URL로 공유 하는 것이고, 회원이 URL를 클릭할 경우 친구가 공유한 카드 카테고리에 저장되는 것으로 해줘.

[Question] AI를 이용한 스크립트 요약 기능에서 사용할 AI 서비스는 어떤 것을 선호하시나요? (예: OpenAI GPT, AWS Bedrock, Google AI 등)
[Answer] AWS bedrock에 claude4.0모델

[Question] 데이터베이스는 어떤 것을 사용하시겠습니까? (예: PostgreSQL, MySQL, MongoDB, SQLite 등)
[Answer] PostgreSQL

[Question] 프론트엔드 기술 스택에 대한 선호사항이 있나요? (예: React, Vue.js, Angular, Vanilla JS 등)
[Answer] React

[Question] 백엔드 기술 스택에 대한 선호사항이 있나요? (예: Node.js, Python Django/FastAPI, Java Spring 등)
[Answer] Python FastAPI

### Phase 2: 기술 스택 및 아키텍처 설계

- [ ] 2.1 기술 스택 결정
- [ ] 2.2 시스템 아키텍처 설계
- [ ] 2.3 데이터베이스 스키마 설계
- [ ] 2.4 API 설계
- [x] 2.5 도메인 모델 설계 - Unit1 (Authentication & Profile Management)
- [x] 2.6 논리적 설계 - Unit1 (Authentication & Profile Management)
- [x] 2.7 도메인 모델 설계 - Unit2 (Category Management)
- [x] 2.8 논리적 설계 - Unit2 (Category Management)
- [x] 2.9 도메인 모델 설계 - Unit3 (Card Creation & Management)
- [x] 2.10 논리적 설계 - Unit3 (Card Creation & Management)
- [x] 2.11 도메인 모델 설계 - Unit4 (Card Search & Display)
- [x] 2.12 논리적 설계 - Unit4 (Card Search & Display)
- [x] 2.13 도메인 모델 설계 - Unit5 (Card Sharing)
- [x] 2.14 논리적 설계 - Unit5 (Card Sharing)
- [x] 2.15 Unit6 (User Experience & UI) 처리 - 프론트엔드 설계로 분리
- [x] 2.16 프론트엔드 아키텍처 및 UI/UX 설계
- [x] 2.17 구현 계획 수립 - Unit1 (Authentication & Profile Management)
- [x] 2.18 구현 계획 수립 - Unit4 (Card Search & Display)

### Phase 3: 개발 환경 구축

- [x] 3.1 프로젝트 초기 설정 - Unit1
- [x] 3.2 개발 환경 구성 - Unit1 (Docker Compose, 의존성 설치)
- [x] 3.3 프로젝트 초기 설정 - Unit4 (헥사고날 아키텍처, 표준 응답 형식)
- [ ] 3.4 필요한 API 키 및 서비스 설정 (YouTube API, AI 서비스 등)

### Phase 4: 백엔드 개발

- [x] 4.1 기본 서버 구조 및 라우팅 설정 - Unit1
- [x] 4.2 데이터베이스 연결 및 모델 생성 - Unit1
- [x] 4.3 Unit4 Domain Layer 구현 (값 객체, 엔티티, 도메인 이벤트)
- [x] 4.4 Unit4 Application Layer 구현 (Use Cases, Application Services, DTOs)
- [x] 4.5 Unit4 Infrastructure Layer 구현 (PostgreSQL, Redis, 이벤트 발행)
- [x] 4.6 Unit4 Presentation Layer 구현 (REST API, 표준 응답 형식)
- [x] 4.7 Unit4 테스트 및 Docker 환경 구성
- [ ] 4.8 YouTube API 연동 기능 개발
- [ ] 4.9 AI 스크립트 요약 기능 개발
- [ ] 4.10 카드 CRUD API 개발
- [ ] 4.11 공유 기능 API 개발

### Phase 5: 프론트엔드 개발

- [ ] 5.1 기본 UI 컴포넌트 개발
- [ ] 5.2 메인 화면 (카드 목록) 개발
- [ ] 5.3 카드 생성 화면 개발
- [ ] 5.4 카드 상세 화면 개발
- [ ] 5.5 검색 및 필터링 기능 개발
- [ ] 5.6 공유 기능 UI 개발

### Phase 6: 통합 및 테스트

- [ ] 6.1 프론트엔드-백엔드 통합
- [ ] 6.2 기능 테스트
- [ ] 6.3 사용자 경험 테스트
- [ ] 6.4 버그 수정 및 최적화

### Phase 7: 배포 및 운영

- [ ] 7.1 배포 환경 설정
- [ ] 7.2 애플리케이션 배포
- [ ] 7.3 모니터링 및 로깅 설정

## 현재 진행 상황

- 현재 단계: Phase 4.2 완료 - Unit1 백엔드 개발 완료 (인증 및 프로필 관리)

## 완료된 작업 요약

### 1.3 사용자 스토리 그룹화 결과:

- **Unit 1**: User Authentication & Profile Management (US-017, US-018, US-019, US-024, US-020, US-022, US-023)
- **Unit 2**: Category Management (US-015, US-016, US-021)
- **Unit 3**: Card Creation & Management (US-001, US-002, US-003, US-004, US-005, US-006)
- **Unit 4**: Card Search & Display (US-007, US-008, US-009, US-010)
- **Unit 5**: Card Sharing (US-011, US-012)
- **Unit 6**: User Experience & UI (US-013, US-014)

### 1.4 단위별 문서 작성 완료:

- unit1_authentication.md
- unit2_category_management.md
- unit3_card_creation.md
- unit4_card_search.md
- unit5_card_sharing.md
- unit6_user_experience.md

### 1.5 통합 계약 정의 완료:

- integration_contract.md (각 단위별 API 엔드포인트 및 메소드 정의)

### 2.5 도메인 모델 설계 완료:

- **Unit 1 (Authentication & Profile Management)**: 사용자 인증 및 프로필 관리 도메인 모델 설계 완료
- **Unit 2 (Category Management)**: 카테고리 관리 도메인 모델 설계 완료
  - CategoryAggregate, Category 엔티티
  - CategoryName, CategoryType, HierarchyLevel, CategoryPath 값 객체
  - 4개 도메인 서비스, 7개 도메인 이벤트
  - 3계층 계층 구조, 시스템 카테고리 관리
  - PostgreSQL 데이터 모델 설계
- **Unit 3 (Card Creation & Management)**: 카드 생성 및 관리 도메인 모델 설계 완료
  - CardAggregate, Card 엔티티, VideoMetadata 엔티티
  - ContentUrl, VideoTitle, Thumbnail, Script, Summary, Tags, Memo, CardStatus 값 객체
  - 즐겨찾기 기능 (IsFavorite, FavoritedAt)
  - 4개 도메인 서비스, 8개 도메인 이벤트
  - PostgreSQL 데이터 모델 설계

### 2.6 논리적 설계 완료:

- **Unit 1 (Authentication & Profile Management)**: 헥사고날 아키텍처 기반 논리적 설계 완료
- **Unit 2 (Category Management)**: 헥사고날 아키텍처 기반 논리적 설계 완료
- **Unit 3 (Card Creation & Management)**: 헥사고날 아키텍처 기반 논리적 설계 완료
  - 이벤트 기반 아키텍처 (Redis + SQS 하이브리드)
  - 커서 기반 페이지네이션 (무한 스크롤)
  - 다중 플랫폼 지원 (YouTube, Instagram, 웹 링크)
  - 즐겨찾기 기능 (별 아이콘 토글, 즐겨찾기 목록)
  - 비동기 메타데이터 수집 및 AI 요약 생성
  - PostgreSQL 최적화 (커서 기반 인덱스)

### 주요 추가 요구사항 반영:

- **즐겨찾기 기능**: 별 아이콘 클릭으로 즐겨찾기 추가/해제, 즐겨찾기 목록 조회
- **커서 기반 페이지네이션**: 오프셋 대신 created_at/favorited_at 기준 커서 사용
- **다중 플랫폼 확장성**: YouTube 외 Instagram 릴스/스토리, Threads, 일반 웹 링크 지원 고려
- **하이브리드 메시징**: 메타데이터 수집(Redis), AI 요약(SQS) 분리
- **비용 최적화**: Redis 캐싱 제외, CDN + 브라우저 캐싱만 사용
- **로그 보관**: 3개월 (환경변수 설정 가능)

---

**다음 단계**: Phase 3 개발 환경 구축 준비 완료
