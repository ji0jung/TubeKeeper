# Unit1 Authentication & Profile Management - Implementation Plan

## 개요
Unit1의 도메인 주도 설계에 따른 이벤트 기반 시스템 구현 계획입니다. 논리적 설계를 바탕으로 확장성이 높은 헥사고날 아키텍처로 구현합니다.

## 구현 단계

### 1. 프로젝트 기본 구조 설정
- [x] 1.1 src 디렉터리 생성 및 헥사고날 아키텍처 패키지 구조 생성
- [x] 1.2 의존성 관리 파일 생성 (requirements.txt, pyproject.toml)
- [x] 1.3 환경 설정 파일 구성 (.env, config 모듈)
- [x] 1.4 Docker Compose 개발 환경 설정 (PostgreSQL, Redis)
- [x] 1.5 AWS SES 설정 및 이메일 서비스 구성
- [x] 1.6 기본 유틸리티 및 공통 모듈 구현

### 2. 도메인 레이어 구현
- [x] 2.1 값 객체(Value Objects) 구현
  - [x] Email 값 객체 (검증 로직 포함)
  - [x] Gender 값 객체 (Enum)
  - [x] BirthYear 값 객체 (검증 로직 포함)
  - [x] DeviceInfo 값 객체 (디바이스 핑거프린트 생성)
  - [x] VerificationCodeValue 값 객체 (6자리 코드 생성)
  - [x] Language 값 객체 (언어 설정)
  - [x] UserStatus 값 객체 (사용자 상태)
  - [x] CodePurpose 값 객체 (인증 코드 목적)
- [x] 2.2 엔티티(Entities) 구현
  - [x] User 엔티티 (상태 관리 메서드 포함)
  - [x] Profile 엔티티 (프로필 업데이트 메서드 포함, updated_at 필드 수정 완료)
  - [x] Session 엔티티 (세션 연장/만료 메서드 포함)
  - [x] VerificationCode 엔티티 (코드 검증 메서드 포함)
- [x] 2.3 애그리게이트(Aggregates) 구현
  - [x] UserAggregate (User + Profile 관리)
  - [x] SessionAggregate (독립적 세션 관리)
  - [x] VerificationCodeAggregate (인증 코드 관리)
- [x] 2.4 도메인 이벤트(Domain Events) 구현
  - [x] 사용자 관련 이벤트 (UserRegistered, UserDeactivated 등)
  - [x] 세션 관련 이벤트 (UserLoggedIn, SessionExtended 등)
  - [x] 인증 관련 이벤트 (VerificationCodeGenerated 등)
  - [x] BaseEvent 클래스 구현
- [x] 2.5 도메인 서비스(Domain Services) 구현
  - [x] AuthenticationService (인증 로직)
  - [x] SessionManagementService (세션 관리 로직)
  - [x] UserRegistrationService (사용자 등록 로직)
  - [x] EmailVerificationService (이메일 인증 로직)
- [x] 2.6 정책(Policies) 구현
  - [x] ConcurrentSessionPolicy (동시 세션 제한)
  - [x] VerificationCodePolicy (인증 코드 정책)
  - [x] AccountDeactivationPolicy (계정 비활성화 정책)
- [x] 2.7 도메인 예외(Domain Exceptions) 구현
  - [x] 기본 도메인 예외 클래스
  - [x] 사용자 관련 예외
  - [x] 세션 관련 예외
  - [x] 인증 관련 예외
- [x] 2.8 리포지토리 인터페이스(Repository Interfaces) 구현
  - [x] UserRepository 인터페이스
  - [x] VerificationCodeRepository 인터페이스

### 3. 애플리케이션 레이어 구현
- [x] 3.1 DTO(Data Transfer Objects) 구현
  - [x] 사용자 관련 DTO (authentication_dtos.py)
  - [x] 프로필 관련 DTO (profile_dtos.py)
  - [x] 세션 관련 DTO
  - [x] 인증 관련 DTO
- [x] 3.2 커맨드(Commands) 및 쿼리(Queries) 구현
  - [x] 등록 관련 커맨드
  - [x] 인증 관련 커맨드
  - [x] 프로필 관련 커맨드
  - [x] 조회 관련 쿼리
- [x] 3.3 애플리케이션 서비스(Application Services) 구현
  - [x] UserRegistrationAppService
  - [x] AuthenticationAppService
  - [x] ProfileManagementAppService (ProfileAppService)
  - [x] SessionManagementAppService
- [x] 3.4 이벤트 핸들러(Event Handlers) 구현
  - [x] 사용자 이벤트 핸들러
  - [x] 세션 이벤트 핸들러
  - [x] 인증 이벤트 핸들러
- [x] 3.5 외부 서비스 인터페이스 정의
  - [x] EmailServiceInterface
  - [x] CacheServiceInterface
  - [x] EventPublisherInterface

### 4. 인프라스트럭처 레이어 구현
- [x] 4.1 데이터베이스 모델(ORM Models) 구현
  - [x] UserModel (PostgreSQL 기반)
  - [x] ProfileModel (PostgreSQL 기반)
  - [x] SessionModel (PostgreSQL 기반)
  - [x] VerificationCodeModel (PostgreSQL 기반)
- [x] 4.2 리포지토리 구현(Repository Implementations)
  - [x] PostgreSQLUserRepository
  - [x] PostgreSQLSessionRepository (메모리 기반)
  - [x] PostgreSQLVerificationCodeRepository (Redis 기반)
  - [x] PostgreSQLProfileRepository
- [x] 4.3 외부 서비스 어댑터 구현
  - [x] Console 이메일 어댑터 (개발용)
  - [x] AWS SES 이메일 어댑터 (준비 완료)
- [x] 4.4 이벤트 인프라 구현
  - [x] EventStore (이벤트 저장소)
  - [x] EventPublisher (이벤트 발행자)
  - [x] EventDispatcher (이벤트 디스패처)
- [x] 4.5 설정 관리 구현
  - [x] DatabaseConfig (settings.py)
  - [x] CacheConfig
  - [x] EmailConfig
  - [x] SecurityConfig

### 5. 인터페이스 레이어 구현
- [x] 5.1 API 스키마(Pydantic Schemas) 구현
  - [x] 인증 요청/응답 스키마 (auth_schemas.py)
  - [x] 프로필 요청/응답 스키마
  - [x] 세션 요청/응답 스키마
  - [x] 공통 스키마 (오류 응답 등)
- [x] 5.2 FastAPI 컨트롤러 구현
  - [x] AuthController (회원가입, 로그인, 로그아웃) - auth_controller.py
  - [x] ProfileController (프로필 조회/수정) - profile_controller.py
  - [x] SessionController (세션 관리)
- [x] 5.3 미들웨어 구현
  - [x] AuthenticationMiddleware (JWT 토큰 검증)
  - [x] RateLimitingMiddleware (요청 제한)
  - [x] CORSMiddleware (CORS 설정)
  - [x] LoggingMiddleware (요청/응답 로깅)
- [x] 5.4 의존성 주입 설정
  - [x] 데이터베이스 의존성
  - [x] 서비스 의존성
  - [x] 인증 의존성

### 6. 데이터베이스 마이그레이션
- [x] 6.1 Alembic 설정
- [x] 6.2 초기 테이블 생성 마이그레이션
  - [x] users 테이블
  - [x] profiles 테이블
  - [x] sessions 테이블 (메모리 기반)
  - [x] verification_codes 테이블 (Redis 기반)
- [x] 6.3 인덱스 및 제약조건 추가

### 7. 보안 구현
- [x] 7.1 JWT 토큰 생성/검증 로직 (jwt_utils.py)
- [x] 7.2 비밀번호 해싱 (이메일 인증 코드용)
- [x] 7.3 CSRF 보호
- [x] 7.4 입력 검증 및 sanitization

### 8. 테스트 구현
- [ ] 8.1 도메인 레이어 단위 테스트
  - [ ] 값 객체 테스트
  - [ ] 엔티티 테스트
  - [ ] 애그리게이트 테스트
  - [ ] 도메인 서비스 테스트
  - [ ] 정책 테스트
- [ ] 8.2 애플리케이션 레이어 테스트
  - [ ] 애플리케이션 서비스 테스트
  - [ ] 이벤트 핸들러 테스트
- [ ] 8.3 인프라스트럭처 레이어 테스트
  - [ ] 리포지토리 테스트
  - [ ] 외부 서비스 어댑터 테스트
- [ ] 8.4 통합 테스트
  - [ ] API 엔드포인트 테스트
  - [ ] 데이터베이스 통합 테스트

### 9. 데모 스크립트 및 문서화
- [x] 9.1 로컬 실행 데모 스크립트 작성
  - [x] 회원가입 플로우 데모
  - [x] 로그인/로그아웃 플로우 데모
  - [x] 프로필 관리 데모
  - [x] 세션 관리 데모
- [x] 9.2 API 문서 생성 (FastAPI 자동 문서화)
- [x] 9.3 README.md 작성 (설치 및 실행 가이드)
- [x] 9.4 구현 완료 보고서 작성 (IMPLEMENTATION_REPORT.md)
- [x] 9.5 배포 가이드 작성 (DEPLOYMENT_GUIDE.md)
- [x] 9.6 API 명세서 작성 (API_SPECIFICATION.md)

### 10. AWS 배포 준비
- [x] 10.1 Docker 컨테이너화 (Dockerfile)
- [x] 10.2 환경별 설정 파일 분리 (.env, .env.example)
- [x] 10.3 로깅 설정
- [x] 10.4 모니터링 설정

### 11. AWS CloudFormation 배포 스크립트 생성
- [x] 11.1 네트워크 인프라 (VPC, 서브넷, 보안 그룹)
- [x] 11.2 데이터베이스 인프라 (RDS PostgreSQL)
- [x] 11.3 캐시 인프라 (ElastiCache Redis)
- [x] 11.4 컨테이너 인프라 (ECS Cluster, Task Definition)
- [x] 11.5 로드 밸런서 및 서비스 (ALB, ECS Service)
- [x] 11.6 IAM 역할 및 정책
- [x] 11.7 CloudWatch 로깅 및 모니터링
- [x] 11.8 배포 스크립트 및 CI/CD 파이프라인 (deploy-production-ready.sh)
- [x] 11.9 ECR 리포지토리 템플릿
- [x] 11.10 S3 버킷 템플릿 (프라이빗, 보안 강화)
- [x] 11.11 마스터 스택 템플릿 (통합 배포)
- [x] 11.12 2단계 배포 스크립트 (S3 버킷 먼저 생성)

### 12. 배포 실행 및 검증
- [x] 12.1 CloudFormation 스택 배포
- [x] 12.2 데이터베이스 마이그레이션 실행
- [x] 12.3 애플리케이션 배포 및 헬스 체크
- [x] 12.4 API 엔드포인트 테스트 (모든 API 테스트 완료)
- [x] 12.5 모니터링 및 알람 설정 확인

[Question] 이메일 서비스로 AWS SES를 사용할 예정인데, AWS 계정 설정이나 SES 설정이 필요한가요?
[Answer] 개발 단계에서 AWS SES 사용, sender email: jhrhee@amazon.com

[Question] Redis를 캐시로 사용할 예정인데, 로컬 개발 환경에서 Redis 서버를 실행해야 하나요?
[Answer] Docker Compose를 사용한 로컬 Redis 실행

[Question] JWT 토큰의 비밀 키(secret key)는 어떻게 관리하시겠습니까? 환경 변수로 설정하시겠습니까?
[Answer] 환경 변수 + 개발용 기본값 제공

[Question] 데이터베이스 연결 정보(호스트, 포트, 사용자명, 비밀번호)는 어떻게 설정하시겠습니까?
[Answer] Docker Compose + 환경 변수 조합 

## 구현 우선순위

1. **핵심 도메인 로직** (2단계): 비즈니스 규칙이 포함된 가장 중요한 부분
2. **애플리케이션 서비스** (3단계): 유스케이스 조율 로직
3. **데이터 영속성** (4단계): 데이터 저장 및 조회
4. **API 인터페이스** (5단계): 외부와의 통신
5. **보안 및 테스트** (7-8단계): 품질 보장

## 예상 소요 시간

- 도메인 레이어: 3-4일
- 애플리케이션 레이어: 2-3일  
- 인프라스트럭처 레이어: 3-4일
- 인터페이스 레이어: 2-3일
- 테스트 및 문서화: 2-3일

**총 예상 시간: 12-17일**
