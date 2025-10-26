# Unit2: Category Management 구현 계획

## 개요
카테고리 생성, 수정, 삭제 기능을 담당하는 Unit2의 프로덕션 레벨 구현 계획입니다.

## 구현 단계별 계획

### 1단계: 프로젝트 구조 및 환경 설정
- [x] 1.1 src 디렉터리 구조 생성
- [x] 1.2 Docker 환경 설정 (PostgreSQL, Redis)
- [x] 1.3 Python 의존성 설정 (requirements.txt)
- [x] 1.4 환경 변수 설정 (.env)
- [x] 1.5 데이터베이스 마이그레이션 스크립트 생성

### 2단계: 도메인 계층 구현
- [x] 2.1 값 객체 구현 (CategoryName, CategoryType, HierarchyLevel, CategoryPath)
- [x] 2.2 도메인 이벤트 구현 (CategoryCreated, CategoryDeleted 등)
- [x] 2.3 Category 엔티티 구현
- [x] 2.4 CategoryAggregate 구현
- [x] 2.5 도메인 서비스 구현 (CategoryDeletionService, CategoryHierarchyService 등)
- [x] 2.6 도메인 예외 클래스 구현

### 3단계: 인프라스트럭처 계층 구현
- [x] 3.1 데이터베이스 모델 구현 (SQLAlchemy)
- [x] 3.2 CategoryRepository 구현
- [x] 3.3 Redis 캐시 서비스 구현
- [x] 3.4 이벤트 발행자 구현
- [x] 3.5 외부 서비스 인터페이스 구현 (CardCountService)

### 4단계: 애플리케이션 계층 구현
- [x] 4.1 커맨드/쿼리 객체 구현
- [x] 4.2 DTO 클래스 구현
- [x] 4.3 CategoryApplicationService 구현
- [x] 4.4 이벤트 핸들러 구현
- [x] 4.5 예외 처리 및 오류 응답 구현

### 5단계: API 계층 구현
- [x] 5.1 FastAPI 라우터 구현
- [x] 5.2 요청/응답 모델 구현 (Pydantic)
- [x] 5.3 인증 미들웨어 통합
- [x] 5.4 API 문서화 (OpenAPI)
- [x] 5.5 CORS 및 보안 설정

### 6단계: Unit2 독립 로컬 Docker 테스트 (JWT 직접 검증)
- [x] 6.1 JWT 토큰 직접 검증 구현 (로컬용)
- [x] 6.2 Docker Compose 설정 완료 (PostgreSQL, Redis만)
- [x] 6.3 데이터베이스 연결 테스트
- [x] 6.4 Redis 연결 테스트
- [x] 6.5 API 엔드포인트 기능 테스트
- [x] 6.6 카테고리 CRUD 통합 테스트
- [x] 6.7 카테고리 삭제 시나리오 테스트 (카드 이동 없이)
- [x] 6.8 시스템 카테고리 자동 생성 테스트

### 7단계: 단위 테스트 및 통합 테스트
- [ ] 7.1 도메인 객체 단위 테스트
- [ ] 7.2 도메인 서비스 단위 테스트
- [ ] 7.3 애플리케이션 서비스 단위 테스트
- [ ] 7.4 리포지토리 통합 테스트
- [ ] 7.5 API 엔드포인트 통합 테스트
- [ ] 7.6 이벤트 발행/처리 테스트

### 8단계: Unit3 통합 로컬 테스트 (카드 이동 기능)
- [ ] 8.1 Unit3 Docker와 연동 설정
- [ ] 8.2 카드 이동 API 통신 구현
- [ ] 8.3 카테고리 삭제 시 카드 이동 테스트
- [ ] 8.4 Unit2-Unit3 통합 시나리오 테스트
- [ ] 8.5 이벤트 기반 통신 테스트

### 9단계: Unit1 인증 서비스 통합 로컬 테스트
- [ ] 9.1 Unit1 인증 서비스 호출 구현
- [ ] 9.2 JWT 직접 검증에서 Unit1 호출로 전환
- [ ] 9.3 Unit1-Unit2-Unit3 통합 로컬 테스트
- [ ] 9.4 인증 토큰 검증 통합 테스트
- [ ] 9.5 전체 시스템 로컬 검증

### 10단계: 성능 최적화 및 모니터링
- [ ] 10.1 데이터베이스 인덱스 최적화
- [ ] 10.2 Redis 캐싱 전략 구현
- [ ] 10.3 로깅 시스템 구현
- [ ] 10.4 메트릭 수집 설정
- [ ] 10.5 성능 테스트 및 튜닝

### 11단계: 배포 준비 및 배포 테스트
- [ ] 11.1 프로덕션 환경 설정
- [ ] 11.2 CI/CD 파이프라인 설정
- [ ] 11.3 헬스체크 엔드포인트 구현
- [ ] 11.4 배포 스크립트 작성
- [ ] 11.5 배포 환경에서 통합 테스트
- [ ] 11.6 롤백 계획 수립

## 질문 사항

[Question] Unit1과의 통합을 위해 인증 토큰 검증 방식을 어떻게 구현할까요? JWT 토큰을 직접 검증할지, Unit1의 인증 서비스를 호출할지 결정이 필요합니다.
[Answer] 단계별 통합 방식으로 진행합니다. 1) Unit2 독립 테스트 시에는 JWT 토큰 직접 검증, 2) Unit3 통합 후에는 Unit1 인증 서비스 호출로 전환하여 최종 통합 테스트를 수행합니다.

[Question] 카테고리 삭제 시 카드 이동을 위해 Unit3(Card Management)와 어떻게 통신할까요? 직접 API 호출, 이벤트 기반 통신, 또는 공유 데이터베이스 접근 중 어떤 방식을 선호하시나요?
[Answer] 이벤트 기반 통신을 사용합니다. Unit2에서 카테고리 삭제 이벤트를 발행하면 Unit3에서 해당 이벤트를 처리하여 카드를 이동시키는 방식으로 구현합니다.

[Question] Redis 캐시의 TTL(Time To Live) 설정은 어떻게 할까요? 카테고리 목록은 자주 변경되지 않으므로 긴 TTL을 설정할 수 있지만, 실시간성과의 균형을 고려해야 합니다.
[Answer] 카테고리 목록은 30분(1800초) TTL로 설정하고, 카테고리 변경 시 해당 캐시를 즉시 무효화하는 방식으로 구현합니다.

[Question] 카테고리 계층 구조의 최대 깊이를 3으로 제한하는 검증을 어느 계층에서 수행할까요? 도메인 계층에서 비즈니스 규칙으로 처리할지, 애플리케이션 계층에서 검증할지 결정이 필요합니다.
[Answer] 도메인 계층에서 비즈니스 규칙으로 처리합니다. CategoryAggregate에서 계층 깊이를 검증하여 도메인 무결성을 보장합니다.

[Question] 대용량 카테고리 삭제 작업(많은 카드가 있는 카테고리)의 비동기 처리를 위해 어떤 메시지 큐를 사용할까요? AWS SQS, Redis Pub/Sub, 또는 Celery 중 선호하는 방식이 있나요?
[Answer] Redis Pub/Sub을 사용합니다. 로컬 개발 환경에서 간단히 설정할 수 있고, 이후 AWS SQS로 전환하기 쉬운 구조로 구현합니다.

## 기술 스택
- **Backend**: Python 3.11, FastAPI
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **ORM**: SQLAlchemy 2.0
- **Migration**: Alembic
- **Testing**: pytest, pytest-asyncio
- **Container**: Docker, Docker Compose
- **Documentation**: OpenAPI/Swagger

## 예상 구현 시간
- 총 예상 시간: 7-9일
- Unit2 독립 구현 및 테스트: 3-4일
- Unit3 통합 테스트: 1-2일  
- Unit1 인증 통합 테스트: 1일
- 성능 최적화 및 배포: 2일

---
**검토 및 승인 요청**: 위 구현 계획을 검토해주시고, 질문 사항에 대한 답변과 함께 승인해주시면 단계별 구현을 시작하겠습니다.
