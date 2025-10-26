# Unit1: Authentication & Profile Management - Logical Design

## 1. 아키텍처 레이어 설계

### 1.1 헥사고날 아키텍처 레이어 구조

```
src/
├── domain/                     # 도메인 레이어 (핵심 비즈니스 로직)
│   ├── aggregates/            # 애그리게이트
│   ├── entities/              # 엔티티
│   ├── value_objects/         # 값 객체
│   ├── events/                # 도메인 이벤트
│   ├── services/              # 도메인 서비스
│   ├── policies/              # 정책
│   ├── repositories/          # 리포지토리 인터페이스
│   └── exceptions/            # 도메인 예외
├── application/               # 애플리케이션 레이어 (유스케이스)
│   ├── services/              # 애플리케이션 서비스
│   ├── commands/              # 커맨드 객체
│   ├── queries/               # 쿼리 객체
│   ├── dtos/                  # 데이터 전송 객체
│   ├── handlers/              # 이벤트 핸들러
│   └── interfaces/            # 외부 서비스 인터페이스
├── infrastructure/            # 인프라스트럭처 레이어 (기술적 구현)
│   ├── persistence/           # 데이터 영속성
│   │   ├── repositories/      # 리포지토리 구현
│   │   ├── models/            # ORM 모델
│   │   └── migrations/        # 데이터베이스 마이그레이션
│   ├── external/              # 외부 서비스 어댑터
│   │   ├── email/             # 이메일 서비스
│   │   └── cache/             # 캐시 서비스
│   ├── events/                # 이벤트 인프라
│   └── config/                # 설정 관리
└── interfaces/                # 인터페이스 레이어 (API)
    ├── api/                   # REST API
    │   ├── controllers/       # 컨트롤러
    │   ├── middlewares/       # 미들웨어
    │   ├── schemas/           # 요청/응답 스키마
    │   └── dependencies/      # 의존성 주입
    └── cli/                   # CLI 인터페이스 (관리용)
```

### 1.2 도메인 레이어 패키지 구조

```
domain/
├── __init__.py
├── aggregates/
│   ├── __init__.py
│   ├── user_aggregate.py      # User 애그리게이트
│   ├── session_aggregate.py   # Session 애그리게이트
│   └── verification_code_aggregate.py  # VerificationCode 애그리게이트
├── entities/
│   ├── __init__.py
│   ├── user.py               # User 엔티티
│   ├── profile.py            # Profile 엔티티
│   ├── session.py            # Session 엔티티
│   └── verification_code.py  # VerificationCode 엔티티
├── value_objects/
│   ├── __init__.py
│   ├── email.py              # Email 값 객체
│   ├── gender.py             # Gender 값 객체
│   ├── birth_year.py         # BirthYear 값 객체
│   ├── device_info.py        # DeviceInfo 값 객체
│   └── verification_code_value.py  # VerificationCode 값 객체
├── events/
│   ├── __init__.py
│   ├── user_events.py        # 사용자 관련 이벤트
│   ├── session_events.py     # 세션 관련 이벤트
│   └── verification_events.py # 인증 관련 이벤트
├── services/
│   ├── __init__.py
│   ├── authentication_service.py      # 인증 서비스
│   ├── email_verification_service.py  # 이메일 인증 서비스
│   ├── session_management_service.py  # 세션 관리 서비스
│   ├── user_registration_service.py   # 사용자 등록 서비스
│   └── user_deactivation_service.py   # 사용자 비활성화 서비스
├── policies/
│   ├── __init__.py
│   ├── verification_code_policy.py    # 인증 코드 정책
│   ├── session_expiration_policy.py   # 세션 만료 정책
│   ├── duplicate_registration_policy.py # 중복 가입 방지 정책
│   ├── account_deactivation_policy.py # 계정 비활성화 정책
│   ├── concurrent_session_policy.py   # 동시 세션 정책
│   └── security_policy.py             # 보안 정책
├── repositories/
│   ├── __init__.py
│   ├── user_repository.py            # User 리포지토리 인터페이스
│   ├── session_repository.py         # Session 리포지토리 인터페이스
│   ├── verification_code_repository.py # VerificationCode 리포지토리 인터페이스
│   └── profile_repository.py         # Profile 리포지토리 인터페이스
└── exceptions/
    ├── __init__.py
    ├── domain_exceptions.py          # 기본 도메인 예외
    ├── user_exceptions.py            # 사용자 관련 예외
    ├── session_exceptions.py         # 세션 관련 예외
    └── verification_exceptions.py    # 인증 관련 예외
```

### 1.3 애플리케이션 레이어 패키지 구조

```
application/
├── __init__.py
├── services/
│   ├── __init__.py
│   ├── user_registration_app_service.py    # 사용자 등록 애플리케이션 서비스
│   ├── authentication_app_service.py       # 인증 애플리케이션 서비스
│   ├── profile_management_app_service.py   # 프로필 관리 애플리케이션 서비스
│   ├── session_management_app_service.py   # 세션 관리 애플리케이션 서비스
│   └── user_deactivation_app_service.py    # 사용자 비활성화 애플리케이션 서비스
├── commands/
│   ├── __init__.py
│   ├── registration_commands.py            # 등록 관련 커맨드
│   ├── authentication_commands.py          # 인증 관련 커맨드
│   ├── profile_commands.py                 # 프로필 관련 커맨드
│   └── session_commands.py                 # 세션 관련 커맨드
├── queries/
│   ├── __init__.py
│   ├── user_queries.py                     # 사용자 조회 쿼리
│   ├── profile_queries.py                  # 프로필 조회 쿼리
│   └── session_queries.py                  # 세션 조회 쿼리
├── dtos/
│   ├── __init__.py
│   ├── user_dtos.py                        # 사용자 DTO
│   ├── profile_dtos.py                     # 프로필 DTO
│   ├── session_dtos.py                     # 세션 DTO
│   └── authentication_dtos.py              # 인증 DTO
├── handlers/
│   ├── __init__.py
│   ├── user_event_handlers.py              # 사용자 이벤트 핸들러
│   ├── session_event_handlers.py           # 세션 이벤트 핸들러
│   └── verification_event_handlers.py      # 인증 이벤트 핸들러
└── interfaces/
    ├── __init__.py
    ├── email_service_interface.py          # 이메일 서비스 인터페이스
    ├── cache_service_interface.py          # 캐시 서비스 인터페이스
    └── event_publisher_interface.py        # 이벤트 발행 인터페이스
```

### 1.4 인프라스트럭처 레이어 패키지 구조

```
infrastructure/
├── __init__.py
├── persistence/
│   ├── __init__.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── postgresql_user_repository.py       # PostgreSQL User 리포지토리
│   │   ├── postgresql_session_repository.py    # PostgreSQL Session 리포지토리
│   │   ├── postgresql_verification_code_repository.py # PostgreSQL VerificationCode 리포지토리
│   │   └── postgresql_profile_repository.py    # PostgreSQL Profile 리포지토리
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user_model.py                       # User ORM 모델
│   │   ├── profile_model.py                    # Profile ORM 모델
│   │   ├── session_model.py                    # Session ORM 모델
│   │   └── verification_code_model.py          # VerificationCode ORM 모델
│   └── migrations/
│       ├── __init__.py
│       └── versions/                           # Alembic 마이그레이션 파일들
├── external/
│   ├── __init__.py
│   ├── email/
│   │   ├── __init__.py
│   │   ├── aws_ses_adapter.py                  # AWS SES 어댑터
│   │   └── email_templates.py                  # 이메일 템플릿
│   └── cache/
│       ├── __init__.py
│       ├── redis_cache_adapter.py              # Redis 캐시 어댑터
│       └── cache_keys.py                       # 캐시 키 관리
├── events/
│   ├── __init__.py
│   ├── event_store.py                          # 이벤트 스토어
│   ├── event_publisher.py                      # 이벤트 발행자
│   └── event_dispatcher.py                     # 이벤트 디스패처
└── config/
    ├── __init__.py
    ├── database_config.py                      # 데이터베이스 설정
    ├── cache_config.py                         # 캐시 설정
    ├── email_config.py                         # 이메일 설정
    └── security_config.py                      # 보안 설정
```

### 1.5 인터페이스 레이어 패키지 구조

```
interfaces/
├── __init__.py
├── api/
│   ├── __init__.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── auth_controller.py                  # 인증 컨트롤러
│   │   ├── profile_controller.py               # 프로필 컨트롤러
│   │   └── session_controller.py               # 세션 컨트롤러
│   ├── middlewares/
│   │   ├── __init__.py
│   │   ├── authentication_middleware.py        # 인증 미들웨어
│   │   ├── rate_limiting_middleware.py         # 레이트 리미팅 미들웨어
│   │   ├── cors_middleware.py                  # CORS 미들웨어
│   │   └── logging_middleware.py               # 로깅 미들웨어
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth_schemas.py                     # 인증 요청/응답 스키마
│   │   ├── profile_schemas.py                  # 프로필 요청/응답 스키마
│   │   ├── session_schemas.py                  # 세션 요청/응답 스키마
│   │   └── common_schemas.py                   # 공통 스키마
│   └── dependencies/
│       ├── __init__.py
│       ├── auth_dependencies.py                # 인증 의존성
│       ├── database_dependencies.py            # 데이터베이스 의존성
│       └── service_dependencies.py             # 서비스 의존성
└── cli/
    ├── __init__.py
    ├── user_management.py                      # 사용자 관리 CLI
    └── system_maintenance.py                   # 시스템 유지보수 CLI
```

## 아키텍처 설계 원칙

### 의존성 규칙
- **도메인 레이어**: 다른 레이어에 의존하지 않음 (순수 비즈니스 로직)
- **애플리케이션 레이어**: 도메인 레이어에만 의존
- **인프라스트럭처 레이어**: 도메인과 애플리케이션 레이어의 인터페이스 구현
- **인터페이스 레이어**: 애플리케이션 레이어를 통해 도메인에 접근

### 관심사 분리
- **도메인**: 비즈니스 규칙과 정책
- **애플리케이션**: 유스케이스 조율
- **인프라스트럭처**: 기술적 구현 세부사항
- **인터페이스**: 외부와의 통신

### 테스트 가능성
- 각 레이어별 독립적 테스트 가능
- 인터페이스를 통한 목(Mock) 객체 활용
- 도메인 로직의 단위 테스트 용이성

## 2. 도메인 레이어 논리적 설계

### 2.1 애그리게이트 클래스 구조 설계

#### User Aggregate
```python
# domain/aggregates/user_aggregate.py
class UserAggregate:
    """사용자 애그리게이트 - User와 Profile을 함께 관리"""
    
    def __init__(self, user: User, profile: Profile):
        self._user = user
        self._profile = profile
        self._domain_events: List[DomainEvent] = []
    
    @classmethod
    def create_new_user(cls, email: Email, gender: Optional[Gender], 
                       birth_year: Optional[BirthYear]) -> 'UserAggregate'
    
    @classmethod
    def from_existing(cls, user: User, profile: Profile) -> 'UserAggregate'
    
    def activate(self) -> None
    def deactivate(self) -> None
    def update_profile(self, gender: Optional[Gender], birth_year: Optional[BirthYear]) -> None
    def change_language(self, language: Language) -> None
    def can_login(self) -> bool
```

#### Session Aggregate
```python
# domain/aggregates/session_aggregate.py
class SessionAggregate:
    """세션 애그리게이트 - 독립적 세션 관리"""
    
    @classmethod
    def create_new_session(cls, user_id: UUID, device_info: DeviceInfo) -> 'SessionAggregate'
    
    @classmethod
    def from_existing(cls, session: Session) -> 'SessionAggregate'
    
    def extend(self) -> None
    def expire(self) -> None
    def is_expired(self) -> bool
    def is_same_device(self, device_info: DeviceInfo) -> bool
```

#### VerificationCode Aggregate
```python
# domain/aggregates/verification_code_aggregate.py
class VerificationCodeAggregate:
    """인증 코드 애그리게이트"""
    
    @classmethod
    def generate_new_code(cls, email: Email, purpose: CodePurpose) -> 'VerificationCodeAggregate'
    
    def verify(self, input_code: str) -> bool
    def mark_as_used(self) -> None
    def is_valid(self) -> bool
```

### 2.2 엔티티 클래스 구조 및 메서드 시그니처 설계

#### User Entity
```python
# domain/entities/user.py
@dataclass
class User:
    user_id: UUID
    email: Email
    status: UserStatus
    created_at: datetime
    last_active_at: datetime
    deactivated_at: Optional[datetime] = None
    
    @classmethod
    def create(cls, email: Email) -> 'User'
    
    def activate(self) -> None
    def deactivate(self) -> None
    def update_last_activity(self) -> None
    def can_login(self) -> bool
```

#### Profile Entity
```python
# domain/entities/profile.py
@dataclass
class Profile:
    profile_id: UUID
    user_id: UUID
    gender: Optional[Gender]
    birth_year: Optional[BirthYear]
    language: Language
    updated_at: datetime
    
    @classmethod
    def create(cls, user_id: UUID, gender: Optional[Gender] = None, 
               birth_year: Optional[BirthYear] = None) -> 'Profile'
    
    def update_gender(self, gender: Gender) -> None
    def update_birth_year(self, birth_year: BirthYear) -> None
    def update_language(self, language: Language) -> None
```

#### Session Entity
```python
# domain/entities/session.py
@dataclass
class Session:
    session_id: UUID
    user_id: UUID
    device_info: DeviceInfo
    created_at: datetime
    expires_at: datetime
    last_accessed_at: datetime
    is_active: bool = True
    
    @classmethod
    def create(cls, user_id: UUID, device_info: DeviceInfo) -> 'Session'
    
    def extend(self) -> None
    def expire(self) -> None
    def is_expired(self) -> bool
    def is_same_device(self, device_info: DeviceInfo) -> bool
```

### 2.3 값 객체 클래스 구조 및 검증 로직 설계

#### Email 값 객체
```python
# domain/value_objects/email.py
@dataclass(frozen=True)
class Email:
    value: str
    
    def __post_init__(self):
        if not self._is_valid_format(self.value):
            raise InvalidEmailFormatException(f"Invalid email format: {self.value}")
    
    @staticmethod
    def _is_valid_format(email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
```

#### DeviceInfo 값 객체 (개선된 버전)
```python
# domain/value_objects/device_info.py
import hashlib

@dataclass(frozen=True)
class DeviceInfo:
    """디바이스 정보 값 객체 - 고유 식별 가능"""
    
    user_agent: str
    ip_address: str
    device_fingerprint: str
    
    @classmethod
    def create(cls, user_agent: str, ip_address: str, 
               screen_resolution: str, timezone: str, language: str) -> 'DeviceInfo':
        """디바이스 핑거프린트 생성으로 고유 식별"""
        fingerprint_data = f"{user_agent}|{screen_resolution}|{timezone}|{language}"
        device_fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:16]
        
        return cls(user_agent, ip_address, device_fingerprint)
    
    def is_same_device(self, other: 'DeviceInfo') -> bool:
        """동일 디바이스 여부 확인"""
        return self.device_fingerprint == other.device_fingerprint
```

#### VerificationCodeValue 값 객체
```python
# domain/value_objects/verification_code_value.py
@dataclass(frozen=True)
class VerificationCodeValue:
    value: str
    
    @classmethod
    def generate(cls) -> 'VerificationCodeValue':
        """6자리 랜덤 코드 생성"""
        code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        return cls(code)
    
    def __post_init__(self):
        if not (len(self.value) == 6 and self.value.isdigit()):
            raise InvalidVerificationCodeException("Code must be 6 digits")
```

### 2.4 도메인 이벤트 클래스 구조 설계

#### 기본 도메인 이벤트
```python
# domain/events/__init__.py
class DomainEvent(ABC):
    def __init__(self):
        self.event_id = uuid4()
        self.occurred_at = datetime.utcnow()
        self.event_version = 1
```

#### 사용자 관련 이벤트
```python
# domain/events/user_events.py
@dataclass
class UserRegistrationRequested(DomainEvent):
    email: Email
    gender: Optional[Gender]
    birth_year: Optional[BirthYear]

@dataclass
class UserRegistered(DomainEvent):
    user_id: UUID
    email: Email
    profile_id: UUID

@dataclass
class UserDeactivated(DomainEvent):
    user_id: UUID
    deactivated_at: datetime
    retention_until: datetime

@dataclass
class ProfileUpdated(DomainEvent):
    user_id: UUID
    profile_id: UUID
    changed_fields: dict
```

#### 세션 관련 이벤트
```python
# domain/events/session_events.py
@dataclass
class UserLoggedIn(DomainEvent):
    user_id: UUID
    session_id: UUID
    device_info: DeviceInfo

@dataclass
class SessionExtended(DomainEvent):
    user_id: UUID
    session_id: UUID
    new_expiry_time: datetime

@dataclass
class MaxSessionLimitReached(DomainEvent):
    user_id: UUID
    new_session_id: UUID
    terminated_session_id: UUID
    device_info: DeviceInfo
```

### 2.5 도메인 서비스 인터페이스 및 구현 설계

#### AuthenticationService
```python
# domain/services/authentication_service.py
class AuthenticationService:
    """인증 서비스"""
    
    def __init__(self, verification_code_repo: VerificationCodeRepository):
        self._verification_code_repo = verification_code_repo
    
    def validate_verification_code(self, email: Email, code: str, 
                                 purpose: CodePurpose) -> bool:
        """인증 코드 검증"""
        
    def authenticate_user(self, email: Email, code: str) -> bool:
        """사용자 인증 수행"""
        
    def handle_authentication_failure(self, email: Email, reason: str) -> None:
        """인증 실패 처리"""
```

#### SessionManagementService
```python
# domain/services/session_management_service.py
class SessionManagementService:
    """세션 관리 서비스"""
    
    def __init__(self, session_repo: SessionRepository, 
                 concurrent_session_policy: ConcurrentSessionPolicy):
        self._session_repo = session_repo
        self._policy = concurrent_session_policy
    
    def create_session(self, user_id: UUID, device_info: DeviceInfo) -> SessionAggregate:
        """새 세션 생성 (동시 로그인 제한 적용)"""
        
    def extend_session(self, session_id: UUID) -> None:
        """세션 연장"""
        
    def terminate_oldest_session(self, user_id: UUID) -> None:
        """가장 오래된 세션 종료"""
        
    def cleanup_expired_sessions(self) -> int:
        """만료된 세션 정리"""
```

### 2.6 정책 클래스 구조 및 검증 로직 설계

#### ConcurrentSessionPolicy (개선된 버전)
```python
# domain/policies/concurrent_session_policy.py
class ConcurrentSessionPolicy:
    """동시 세션 정책 - 디바이스 기반 식별"""
    
    MAX_SESSIONS = 3
    
    def __init__(self, session_repo: SessionRepository):
        self._session_repo = session_repo
    
    def can_create_new_session(self, user_id: UUID, device_info: DeviceInfo) -> bool:
        """새 세션 생성 가능 여부 확인"""
        active_sessions = self._session_repo.find_active_sessions_by_user_id(user_id)
        
        # 동일 디바이스에서 로그인 시 기존 세션 갱신
        for session in active_sessions:
            if session.device_info.is_same_device(device_info):
                return True  # 기존 세션 갱신으로 처리
        
        # 새 디바이스에서 로그인 시 3개 제한 확인
        return len(active_sessions) < self.MAX_SESSIONS
    
    def find_session_to_terminate(self, user_id: UUID) -> Optional[UUID]:
        """종료할 세션 찾기 (가장 오래된 세션)"""
        sessions = self._session_repo.find_active_sessions_by_user_id(user_id)
        if not sessions:
            return None
        
        # 만료 시간이 가장 가까운 세션 선택
        oldest_session = min(sessions, key=lambda s: s.expires_at)
        return oldest_session.session_id
```

#### VerificationCodePolicy
```python
# domain/policies/verification_code_policy.py
class VerificationCodePolicy:
    """인증 코드 정책"""
    
    EXPIRY_MINUTES = 15
    CODE_LENGTH = 6
    
    def is_code_expired(self, created_at: datetime) -> bool:
        """코드 만료 여부 확인"""
        return datetime.utcnow() > created_at + timedelta(minutes=self.EXPIRY_MINUTES)
    
    def can_generate_new_code(self, email: Email, purpose: CodePurpose) -> bool:
        """새 코드 생성 가능 여부 (1분 간격 제한)"""
        # 구현 로직
        pass
```

### 2.7 도메인 예외 클래스 계층 구조 설계

#### 기본 도메인 예외
```python
# domain/exceptions/domain_exceptions.py
class DomainException(Exception):
    """도메인 예외 기본 클래스"""
    pass

class BusinessRuleViolationException(DomainException):
    """비즈니스 규칙 위반 예외"""
    pass

class InvalidValueObjectException(DomainException):
    """값 객체 유효성 예외"""
    pass
```

#### 구체적 도메인 예외들
```python
# domain/exceptions/user_exceptions.py
class UserNotFoundException(DomainException):
    pass

class DuplicateEmailException(BusinessRuleViolationException):
    pass

class UserDeactivatedException(BusinessRuleViolationException):
    pass

# domain/exceptions/session_exceptions.py
class SessionNotFoundException(DomainException):
    pass

class SessionExpiredException(BusinessRuleViolationException):
    pass

class MaxSessionLimitExceededException(BusinessRuleViolationException):
    pass

# domain/exceptions/verification_exceptions.py
class InvalidVerificationCodeException(InvalidValueObjectException):
    pass

class VerificationCodeExpiredException(BusinessRuleViolationException):
    pass
```

## 3. 애플리케이션 레이어 논리적 설계

### 3.1 애플리케이션 서비스 클래스 구조 설계

#### UserRegistrationApplicationService
```python
# application/services/user_registration_app_service.py
class UserRegistrationApplicationService:
    def __init__(self, user_repo: UserRepository, verification_code_repo: VerificationCodeRepository,
                 email_service: EmailServiceInterface, event_publisher: EventPublisherInterface):
        # 의존성 주입
    
    @transactional
    def request_registration(self, command: RequestRegistrationCommand) -> RequestRegistrationResult:
        """회원가입 요청 - 이메일 중복 확인 및 인증 코드 발송"""
        
    @transactional
    def complete_registration(self, command: CompleteRegistrationCommand) -> CompleteRegistrationResult:
        """회원가입 완료 - 인증 코드 검증 및 User+Profile 생성"""
```

#### AuthenticationApplicationService
```python
# application/services/authentication_app_service.py
class AuthenticationApplicationService:
    @transactional
    def request_login(self, command: RequestLoginCommand) -> RequestLoginResult:
        """로그인 요청 - 사용자 확인 및 인증 코드 발송"""
        
    @transactional
    def complete_login(self, command: CompleteLoginCommand) -> CompleteLoginResult:
        """로그인 완료 - 인증 코드 검증 및 세션 생성"""
        
    def logout(self, command: LogoutCommand) -> LogoutResult:
        """로그아웃 - 세션 무효화 및 캐시 삭제"""
```

### 3.2 커맨드/쿼리 객체 설계 (CQRS 패턴)

#### 커맨드 객체
```python
# application/commands/
@dataclass
class RequestRegistrationCommand:
    email: str
    gender: Optional[str] = None
    birth_year: Optional[int] = None

@dataclass
class CompleteLoginCommand:
    email: str
    verification_code: str
    user_agent: str
    ip_address: str
    screen_resolution: str
    timezone: str
    language: str

@dataclass
class UpdateProfileCommand:
    user_id: str
    gender: Optional[str] = None
    birth_year: Optional[int] = None
```

#### 쿼리 객체
```python
# application/queries/
@dataclass
class GetProfileQuery:
    user_id: str

@dataclass
class GetActiveSessionsQuery:
    user_id: str
```

### 3.3 DTO (Data Transfer Object) 설계

```python
# application/dtos/
@dataclass
class UserDto:
    user_id: str
    email: str
    status: str
    created_at: datetime

@dataclass
class LoginResult:
    success: bool
    token: Optional[str] = None
    expires_at: Optional[datetime] = None
    user: Optional[UserDto] = None

@dataclass
class ProfileDto:
    profile_id: str
    user_id: str
    gender: Optional[str]
    birth_year: Optional[int]
    language: str
```

### 3.4 애플리케이션 이벤트 핸들러 설계

```python
# application/handlers/user_event_handlers.py
class UserEventHandlers:
    @event_handler(UserRegistrationRequested)
    async def handle_user_registration_requested(self, event: UserRegistrationRequested):
        """사용자 등록 요청 시 인증 이메일 발송"""
        
    @event_handler(UserDeactivated)
    async def handle_user_deactivated(self, event: UserDeactivated):
        """사용자 비활성화 시 캐시 정리"""

# application/handlers/session_event_handlers.py
class SessionEventHandlers:
    @event_handler(UserLoggedIn)
    async def handle_user_logged_in(self, event: UserLoggedIn):
        """로그인 시 캐시 업데이트"""
        
    @event_handler(MaxSessionLimitReached)
    async def handle_max_session_limit_reached(self, event: MaxSessionLimitReached):
        """세션 제한 도달 시 기존 세션 종료"""
```

### 3.5 트랜잭션 경계 및 관리 전략 설계

```python
# application/decorators/transactional.py
def transactional(func):
    """트랜잭션 데코레이터"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with get_db_session() as session:
            try:
                result = await func(*args, **kwargs)
                await session.commit()
                return result
            except Exception:
                await session.rollback()
                raise
    return wrapper

# 트랜잭션 경계 원칙:
# - 단일 애그리게이트 수정: 단일 트랜잭션
# - 다중 애그리게이트: 최소화, 이벤트 기반 최종 일관성 활용
```

### 3.6 보안 및 권한 검증 로직 설계

#### 권한 검증 데코레이터
```python
# application/decorators/authorization.py
def require_authentication(func):
    """인증 필수 데코레이터 - JWT 토큰 검증"""
    
def require_user_ownership(func):
    """사용자 소유권 확인 데코레이터 - 본인 데이터만 접근 허용"""
    @wraps(func)
    async def wrapper(self, command, current_user_id: str, *args, **kwargs):
        if command.user_id != current_user_id:
            raise UnauthorizedAccessException("Access denied: not resource owner")
        return await func(self, command, *args, **kwargs)
    return wrapper
```

#### 입력 검증 및 새니타이징
```python
# application/validators/input_validators.py
class InputValidator:
    @staticmethod
    def validate_email(email: str) -> Email:
        """이메일 검증 및 값 객체 변환"""
        
    @staticmethod
    def sanitize_user_agent(user_agent: str) -> str:
        """User-Agent 새니타이징 - XSS, 로그 인젝션 방지"""
        # HTML 태그 제거, 개행문자 제거, 길이 제한, 특수문자 필터링
        
    @staticmethod
    def validate_verification_code(code: str) -> str:
        """인증 코드 검증 - 6자리 숫자만 허용"""
```

#### 보안 서비스
```python
# application/services/security_service.py
class SecurityService:
    def validate_jwt_token(self, token: str) -> Optional[dict]:
        """JWT 토큰 검증"""
        
    def check_rate_limit(self, email: str, action: str) -> bool:
        """레이트 리미팅 확인 - 브루트포스 공격 방지"""
        
    def log_security_event(self, event_type: str, details: dict):
        """보안 이벤트 로깅 - 감사 추적"""
```

## 4. 인프라스트럭처 레이어 논리적 설계

### 4.1 PostgreSQL 리포지토리 구현 설계

#### PostgreSQL User Repository
```python
# infrastructure/persistence/repositories/postgresql_user_repository.py
class PostgreSQLUserRepository(UserRepository):
    """PostgreSQL 기반 User 리포지토리 구현"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, user_aggregate: UserAggregate) -> UserAggregate:
        """User + Profile 트랜잭션으로 저장"""
        user_model = UserModel.from_entity(user_aggregate.user)
        profile_model = ProfileModel.from_entity(user_aggregate.profile)
        
        self._session.add(user_model)
        self._session.add(profile_model)
        await self._session.flush()
        
        return user_aggregate
    
    async def find_by_id(self, user_id: UUID) -> Optional[UserAggregate]:
        """ID로 사용자 조회 (User + Profile JOIN)"""
        
    async def find_by_email(self, email: Email) -> Optional[UserAggregate]:
        """이메일로 사용자 조회"""
        
    async def exists_by_email(self, email: Email) -> bool:
        """이메일 중복 확인"""
```

#### PostgreSQL Session Repository
```python
# infrastructure/persistence/repositories/postgresql_session_repository.py
class PostgreSQLSessionRepository(SessionRepository):
    
    async def save(self, session_aggregate: SessionAggregate) -> SessionAggregate:
        """세션 저장"""
        
    async def find_active_sessions_by_user_id(self, user_id: UUID) -> List[SessionAggregate]:
        """사용자의 활성 세션 조회"""
        
    async def count_active_sessions_by_user_id(self, user_id: UUID) -> int:
        """사용자의 활성 세션 수 조회"""
        
    async def find_oldest_session_by_user_id(self, user_id: UUID) -> Optional[SessionAggregate]:
        """가장 오래된 세션 조회 (만료 시간 기준)"""
        
    async def delete_expired_sessions(self) -> int:
        """만료된 세션 일괄 삭제"""
```

### 4.2 PostgreSQL 테이블 설계 및 인덱스 전략

#### 테이블 스키마 설계
```sql
-- Users 테이블
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_active_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deactivated_at TIMESTAMP WITH TIME ZONE NULL
);

-- Profiles 테이블
CREATE TABLE profiles (
    profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    gender VARCHAR(20) NULL,
    birth_year INTEGER NULL,
    language VARCHAR(10) NOT NULL DEFAULT 'KOREAN',
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Sessions 테이블
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    device_info JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_accessed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

-- Verification Codes 테이블
CREATE TABLE verification_codes (
    code_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    code VARCHAR(6) NOT NULL,
    purpose VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE NULL
);
```

#### 인덱스 전략
```sql
-- Users 테이블 인덱스
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_deactivated_at ON users(deactivated_at) WHERE deactivated_at IS NOT NULL;

-- Sessions 테이블 인덱스 (동시 로그인 제한 및 성능 최적화)
CREATE INDEX idx_sessions_user_active ON sessions(user_id, is_active) WHERE is_active = true;
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at) WHERE is_active = true;
CREATE INDEX idx_sessions_user_created ON sessions(user_id, created_at) WHERE is_active = true;

-- Verification Codes 테이블 인덱스
CREATE INDEX idx_verification_codes_lookup ON verification_codes(email, purpose, is_used);
CREATE INDEX idx_verification_codes_expires ON verification_codes(expires_at) WHERE is_used = false;

-- Profiles 테이블 인덱스
CREATE UNIQUE INDEX idx_profiles_user_id ON profiles(user_id);
```

### 4.3 AWS SES 이메일 서비스 어댑터 설계

```python
# infrastructure/external/email/aws_ses_adapter.py
class AWSSESAdapter(EmailServiceInterface):
    """AWS SES 이메일 서비스 어댑터"""
    
    def __init__(self, ses_client, template_service: EmailTemplateService):
        self._ses_client = ses_client
        self._template_service = template_service
    
    async def send_verification_code(self, email: Email, code: str, purpose: CodePurpose) -> bool:
        """인증 코드 이메일 발송"""
        try:
            template = self._template_service.get_verification_template(purpose)
            html_content = template.render(code=code, email=email.value)
            
            response = await self._ses_client.send_email(
                Source='noreply@yourdomain.com',
                Destination={'ToAddresses': [email.value]},
                Message={
                    'Subject': {'Data': template.subject},
                    'Body': {'Html': {'Data': html_content}}
                }
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    async def send_welcome_email(self, email: Email, user_name: str) -> bool:
        """환영 이메일 발송"""

# infrastructure/external/email/email_templates.py
class EmailTemplateService:
    """이메일 템플릿 서비스"""
    
    def get_verification_template(self, purpose: CodePurpose) -> EmailTemplate:
        if purpose == CodePurpose.REGISTRATION:
            return RegistrationVerificationTemplate()
        elif purpose == CodePurpose.LOGIN:
            return LoginVerificationTemplate()
            
class RegistrationVerificationTemplate:
    subject = "회원가입 인증 코드"
    
    def render(self, code: str, email: str) -> str:
        return f"""
        <h2>회원가입 인증 코드</h2>
        <p>안녕하세요! 회원가입을 완료하려면 아래 인증 코드를 입력해주세요.</p>
        <h3 style="color: #007bff;">{code}</h3>
        <p>이 코드는 15분 후 만료됩니다.</p>
        """
```

### 4.4 이벤트 스토어 구현 설계

```python
# infrastructure/events/event_store.py
class PostgreSQLEventStore:
    """PostgreSQL 기반 이벤트 스토어"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save_events(self, aggregate_id: UUID, events: List[DomainEvent], 
                         expected_version: int) -> None:
        """도메인 이벤트 저장"""
        for i, event in enumerate(events):
            event_model = EventModel(
                event_id=event.event_id,
                aggregate_id=aggregate_id,
                event_type=event.__class__.__name__,
                event_data=json.dumps(asdict(event)),
                event_version=expected_version + i + 1,
                occurred_at=event.occurred_at
            )
            self._session.add(event_model)
    
    async def get_events(self, aggregate_id: UUID, from_version: int = 0) -> List[DomainEvent]:
        """애그리게이트의 이벤트 조회"""

# infrastructure/events/event_publisher.py
class AsyncEventPublisher(EventPublisherInterface):
    """비동기 이벤트 발행자"""
    
    def __init__(self, redis_client):
        self._redis_client = redis_client
        self._handlers = {}
    
    async def publish(self, event: DomainEvent) -> None:
        """이벤트 발행 (Redis Pub/Sub)"""
        event_data = {
            'event_type': event.__class__.__name__,
            'event_data': asdict(event),
            'occurred_at': event.occurred_at.isoformat()
        }
        
        await self._redis_client.publish(
            f"events.{event.__class__.__name__}",
            json.dumps(event_data)
        )
```

### 4.5 Redis 캐싱 전략 및 구현 설계

```python
# infrastructure/external/cache/redis_cache_adapter.py
class RedisCacheAdapter(CacheServiceInterface):
    """Redis 캐시 어댑터"""
    
    def __init__(self, redis_client):
        self._redis = redis_client
    
    # 1순위: 사용자 세션 캐싱
    async def cache_session(self, session_id: UUID, session_data: dict, ttl_seconds: int = 604800):
        """세션 캐싱 (TTL: 7일)"""
        key = f"session:{session_id}"
        await self._redis.setex(key, ttl_seconds, json.dumps(session_data))
    
    async def get_session(self, session_id: UUID) -> Optional[dict]:
        """세션 조회"""
        key = f"session:{session_id}"
        data = await self._redis.get(key)
        return json.loads(data) if data else None
    
    async def invalidate_session(self, session_id: UUID) -> None:
        """세션 캐시 무효화"""
        key = f"session:{session_id}"
        await self._redis.delete(key)
    
    # 2순위: 사용자 기본 정보 캐싱
    async def cache_user_info(self, user_id: UUID, user_data: dict, ttl_seconds: int = 3600):
        """사용자 기본 정보 캐싱 (TTL: 1시간)"""
        key = f"user:{user_id}"
        await self._redis.setex(key, ttl_seconds, json.dumps(user_data))
    
    # 3순위: 인증 코드 캐싱
    async def cache_verification_code(self, email: str, purpose: str, code_data: dict, ttl_seconds: int = 900):
        """인증 코드 캐싱 (TTL: 15분)"""
        key = f"verification:{email}:{purpose}"
        await self._redis.setex(key, ttl_seconds, json.dumps(code_data))

# infrastructure/external/cache/cache_keys.py
class CacheKeys:
    """캐시 키 관리"""
    
    @staticmethod
    def session_key(session_id: UUID) -> str:
        return f"session:{session_id}"
    
    @staticmethod
    def user_key(user_id: UUID) -> str:
        return f"user:{user_id}"
    
    @staticmethod
    def verification_key(email: str, purpose: str) -> str:
        return f"verification:{email}:{purpose}"
    
    @staticmethod
    def rate_limit_key(email: str, action: str) -> str:
        return f"rate_limit:{email}:{action}"
```

### 4.6 외부 서비스 통합 어댑터 설계

#### 설정 관리
```python
# infrastructure/config/database_config.py
class DatabaseConfig:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.pool_size = int(os.getenv("DB_POOL_SIZE", "10"))
        self.max_overflow = int(os.getenv("DB_MAX_OVERFLOW", "20"))
        self.pool_timeout = int(os.getenv("DB_POOL_TIMEOUT", "30"))

# infrastructure/config/cache_config.py
class CacheConfig:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL")
        self.redis_password = os.getenv("REDIS_PASSWORD")
        self.connection_pool_size = int(os.getenv("REDIS_POOL_SIZE", "10"))

# infrastructure/config/email_config.py
class EmailConfig:
    def __init__(self):
        self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.sender_email = os.getenv("SENDER_EMAIL")
```

#### ORM 모델 설계
```python
# infrastructure/persistence/models/user_model.py
class UserModel(Base):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), nullable=False, unique=True)
    status = Column(String(20), nullable=False, default="ACTIVE")
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    last_active_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    deactivated_at = Column(DateTime(timezone=True), nullable=True)
    
    # 관계
    profile = relationship("ProfileModel", back_populates="user", uselist=False)
    sessions = relationship("SessionModel", back_populates="user")
    
    @classmethod
    def from_entity(cls, user: User) -> 'UserModel':
        """엔티티에서 ORM 모델로 변환"""
        
    def to_entity(self) -> User:
        """ORM 모델에서 엔티티로 변환"""

# infrastructure/persistence/models/session_model.py
class SessionModel(Base):
    __tablename__ = "sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    device_info = Column(JSON, nullable=False)  # JSONB 컬럼
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    is_active = Column(Boolean, nullable=False, default=True)
    
    # 관계
    user = relationship("UserModel", back_populates="sessions")
```

## 5. 인터페이스 레이어 논리적 설계

### 5.1 FastAPI 컨트롤러 설계

#### 인증 컨트롤러
```python
# interfaces/api/controllers/auth_controller.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer

router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()

class AuthController:
    def __init__(self, 
                 registration_service: UserRegistrationApplicationService,
                 auth_service: AuthenticationApplicationService):
        self._registration_service = registration_service
        self._auth_service = auth_service

@router.post("/register", response_model=RegisterResponse)
async def request_registration(
    request: RegisterRequest,
    controller: AuthController = Depends()
):
    """회원가입 요청"""
    command = RequestRegistrationCommand(
        email=request.email,
        gender=request.gender,
        birth_year=request.birth_year
    )
    result = await controller._registration_service.request_registration(command)
    return RegisterResponse.from_result(result)

@router.post("/register/verify", response_model=RegisterVerifyResponse)
async def complete_registration(
    request: RegisterVerifyRequest,
    controller: AuthController = Depends()
):
    """회원가입 완료"""
    command = CompleteRegistrationCommand(
        email=request.email,
        verification_code=request.verification_code
    )
    result = await controller._registration_service.complete_registration(command)
    return RegisterVerifyResponse.from_result(result)

@router.post("/login", response_model=LoginResponse)
async def request_login(
    request: LoginRequest,
    user_agent: str = Header(...),
    x_forwarded_for: str = Header(None),
    controller: AuthController = Depends()
):
    """로그인 요청"""
    command = RequestLoginCommand(
        email=request.email,
        user_agent=user_agent,
        ip_address=x_forwarded_for or "unknown",
        screen_resolution=request.screen_resolution,
        timezone=request.timezone,
        language=request.language
    )
    result = await controller._auth_service.request_login(command)
    return LoginResponse.from_result(result)

@router.post("/login/verify", response_model=LoginVerifyResponse)
async def complete_login(
    request: LoginVerifyRequest,
    user_agent: str = Header(...),
    x_forwarded_for: str = Header(None),
    controller: AuthController = Depends()
):
    """로그인 완료"""
    command = CompleteLoginCommand(
        email=request.email,
        verification_code=request.verification_code,
        user_agent=user_agent,
        ip_address=x_forwarded_for or "unknown",
        screen_resolution=request.screen_resolution,
        timezone=request.timezone,
        language=request.language
    )
    result = await controller._auth_service.complete_login(command)
    return LoginVerifyResponse.from_result(result)

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: dict = Depends(get_current_user),
    controller: AuthController = Depends()
):
    """로그아웃"""
    command = LogoutCommand(session_id=current_user["session_id"])
    result = await controller._auth_service.logout(command)
    return LogoutResponse.from_result(result)
```

#### 프로필 컨트롤러
```python
# interfaces/api/controllers/profile_controller.py
@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user: dict = Depends(get_current_user),
    controller: ProfileController = Depends()
):
    """프로필 조회"""
    query = GetProfileQuery(user_id=current_user["user_id"])
    profile = await controller._profile_service.get_profile(query)
    return ProfileResponse.from_dto(profile)

@router.put("/profile", response_model=ProfileUpdateResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
    controller: ProfileController = Depends()
):
    """프로필 수정"""
    command = UpdateProfileCommand(
        user_id=current_user["user_id"],
        gender=request.gender,
        birth_year=request.birth_year
    )
    result = await controller._profile_service.update_profile(command)
    return ProfileUpdateResponse.from_result(result)
```

### 5.2 요청/응답 Pydantic 모델 설계

#### 인증 스키마
```python
# interfaces/api/schemas/auth_schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class RegisterRequest(BaseModel):
    email: EmailStr
    gender: Optional[str] = Field(None, regex="^(MALE|FEMALE|NOT_SPECIFIED)$")
    birth_year: Optional[int] = Field(None, ge=1900, le=2024)

class RegisterResponse(BaseModel):
    success: bool
    message: str
    request_id: Optional[str] = None
    
    @classmethod
    def from_result(cls, result) -> 'RegisterResponse':
        return cls(
            success=result.success,
            message=result.message,
            request_id=result.request_id
        )

class LoginRequest(BaseModel):
    email: EmailStr
    screen_resolution: str = Field(..., regex="^\\d+x\\d+$")
    timezone: str = Field(..., max_length=50)
    language: str = Field(..., regex="^(ko|en)$")

class LoginVerifyRequest(BaseModel):
    email: EmailStr
    verification_code: str = Field(..., regex="^\\d{6}$")
    screen_resolution: str = Field(..., regex="^\\d+x\\d+$")
    timezone: str = Field(..., max_length=50)
    language: str = Field(..., regex="^(ko|en)$")

class LoginVerifyResponse(BaseModel):
    success: bool
    token: Optional[str] = None
    expires_at: Optional[datetime] = None
    user: Optional[dict] = None
    message: Optional[str] = None
```

#### 프로필 스키마
```python
# interfaces/api/schemas/profile_schemas.py
class ProfileResponse(BaseModel):
    profile_id: str
    user_id: str
    gender: Optional[str]
    birth_year: Optional[int]
    language: str
    updated_at: datetime
    
    @classmethod
    def from_dto(cls, dto: ProfileDto) -> 'ProfileResponse':
        return cls(
            profile_id=dto.profile_id,
            user_id=dto.user_id,
            gender=dto.gender,
            birth_year=dto.birth_year,
            language=dto.language,
            updated_at=dto.updated_at
        )

class ProfileUpdateRequest(BaseModel):
    gender: Optional[str] = Field(None, regex="^(MALE|FEMALE|NOT_SPECIFIED)$")
    birth_year: Optional[int] = Field(None, ge=1900, le=2024)
```

#### 공통 스키마
```python
# interfaces/api/schemas/common_schemas.py
class ErrorResponse(BaseModel):
    success: bool = False
    error: dict
    
    @classmethod
    def from_exception(cls, exc: Exception) -> 'ErrorResponse':
        return cls(
            error={
                "code": exc.__class__.__name__,
                "message": str(exc),
                "details": getattr(exc, 'details', {})
            }
        )

class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[dict] = None
```

### 5.3 API 문서화 구조 설계 (OpenAPI/Swagger)

```python
# interfaces/api/main.py
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="Authentication & Profile Management API",
    description="Unit1 인증 및 프로필 관리 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Authentication API",
        version="1.0.0",
        description="사용자 인증 및 프로필 관리 API 문서",
        routes=app.routes,
    )
    
    # 보안 스키마 추가
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# API 라우터 등록
app.include_router(auth_router)
app.include_router(profile_router)
```

### 5.4 JWT 인증/인가 미들웨어 설계

```python
# interfaces/api/middlewares/authentication_middleware.py
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime

security = HTTPBearer()

class JWTAuthenticationMiddleware:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
    
    def create_access_token(self, user_id: str, session_id: str, expires_delta: timedelta) -> str:
        """JWT 토큰 생성"""
        expire = datetime.utcnow() + expires_delta
        payload = {
            "user_id": user_id,
            "session_id": session_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> dict:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_middleware: JWTAuthenticationMiddleware = Depends(),
    cache_service: CacheServiceInterface = Depends()
) -> dict:
    """현재 사용자 정보 조회"""
    # 1. JWT 토큰 검증
    payload = jwt_middleware.verify_token(credentials.credentials)
    
    # 2. 세션 유효성 확인 (캐시에서)
    session_data = await cache_service.get_session(payload["session_id"])
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found or expired"
        )
    
    return {
        "user_id": payload["user_id"],
        "session_id": payload["session_id"],
        "session_data": session_data
    }
```

### 5.5 예외 처리 및 오류 응답 설계

```python
# interfaces/api/middlewares/exception_middleware.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

async def domain_exception_handler(request: Request, exc: DomainException):
    """도메인 예외 처리"""
    logger.warning(f"Domain exception: {exc}")
    
    status_code = 400
    if isinstance(exc, UserNotFoundException):
        status_code = 404
    elif isinstance(exc, UnauthorizedAccessException):
        status_code = 403
    elif isinstance(exc, SessionExpiredException):
        status_code = 401
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": exc.__class__.__name__,
                "message": str(exc)
            }
        }
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """입력 검증 예외 처리"""
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "details": exc.errors()
            }
        }
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 예외 처리"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail
            }
        }
    )

# 예외 핸들러 등록
app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
```

### 5.6 API 버전 관리 전략 설계

```python
# interfaces/api/versioning.py
from fastapi import APIRouter

# 버전별 라우터 생성
v1_router = APIRouter(prefix="/api/v1")
v2_router = APIRouter(prefix="/api/v2")

# V1 API (현재 버전)
v1_auth_router = APIRouter(prefix="/auth", tags=["v1-authentication"])
v1_profile_router = APIRouter(prefix="/profile", tags=["v1-profile"])

# V2 API (향후 버전)
v2_auth_router = APIRouter(prefix="/auth", tags=["v2-authentication"])

# 버전별 라우터 등록
v1_router.include_router(v1_auth_router)
v1_router.include_router(v1_profile_router)
v2_router.include_router(v2_auth_router)

app.include_router(v1_router)
app.include_router(v2_router)

# 기본 버전 (v1으로 리다이렉트)
app.include_router(v1_auth_router, prefix="/api/auth")
app.include_router(v1_profile_router, prefix="/api/profile")
```

#### 미들웨어 추가 설계
```python
# interfaces/api/middlewares/rate_limiting_middleware.py
class RateLimitingMiddleware:
    """레이트 리미팅 미들웨어"""
    
    def __init__(self, redis_client, default_limit: int = 100):
        self.redis_client = redis_client
        self.default_limit = default_limit
    
    async def __call__(self, request: Request, call_next):
        # IP 기반 레이트 리미팅
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        current = await self.redis_client.get(key)
        if current and int(current) >= self.default_limit:
            return JSONResponse(
                status_code=429,
                content={"error": "Rate limit exceeded"}
            )
        
        # 요청 카운트 증가
        await self.redis_client.incr(key)
        await self.redis_client.expire(key, 3600)  # 1시간
        
        response = await call_next(request)
        return response

# interfaces/api/middlewares/cors_middleware.py
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "https://yourdomain.com"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
```

## 6. 데이터 모델링 및 영속성 설계

### 6.1 PostgreSQL 테이블 스키마 설계

#### 완전한 테이블 정의
```sql
-- Users 테이블 (핵심 인증 정보)
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'DEACTIVATED', 'PENDING_DELETION')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_active_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    deactivated_at TIMESTAMP WITH TIME ZONE NULL,
    version INTEGER NOT NULL DEFAULT 1  -- 낙관적 잠금용
);

-- Profiles 테이블 (개인정보)
CREATE TABLE profiles (
    profile_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    gender VARCHAR(20) NULL CHECK (gender IN ('MALE', 'FEMALE', 'NOT_SPECIFIED')),
    birth_year INTEGER NULL CHECK (birth_year >= 1900 AND birth_year <= EXTRACT(YEAR FROM NOW())),
    language VARCHAR(10) NOT NULL DEFAULT 'KOREAN' CHECK (language IN ('KOREAN', 'ENGLISH')),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    version INTEGER NOT NULL DEFAULT 1,
    UNIQUE(user_id)
);

-- Sessions 테이블 (세션 관리)
CREATE TABLE sessions (
    session_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    device_info JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_accessed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    version INTEGER NOT NULL DEFAULT 1
);

-- Verification Codes 테이블 (인증 코드)
CREATE TABLE verification_codes (
    code_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    code VARCHAR(6) NOT NULL,
    purpose VARCHAR(20) NOT NULL CHECK (purpose IN ('REGISTRATION', 'LOGIN')),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    used_at TIMESTAMP WITH TIME ZONE NULL,
    attempt_count INTEGER NOT NULL DEFAULT 0
);

-- Events 테이블 (이벤트 스토어)
CREATE TABLE events (
    event_id UUID PRIMARY KEY,
    aggregate_id UUID NOT NULL,
    aggregate_type VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    event_version INTEGER NOT NULL,
    occurred_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

#### 인덱스 최적화 전략
```sql
-- Users 테이블 인덱스
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_deactivated_at ON users(deactivated_at) WHERE deactivated_at IS NOT NULL;
CREATE INDEX idx_users_last_active ON users(last_active_at) WHERE status = 'ACTIVE';

-- Sessions 테이블 인덱스 (동시 로그인 제한 최적화)
CREATE INDEX idx_sessions_user_active ON sessions(user_id, is_active, expires_at) WHERE is_active = true;
CREATE INDEX idx_sessions_expires_cleanup ON sessions(expires_at) WHERE is_active = true;
CREATE INDEX idx_sessions_device_fingerprint ON sessions USING GIN ((device_info->>'device_fingerprint'));

-- Verification Codes 테이블 인덱스
CREATE INDEX idx_verification_codes_lookup ON verification_codes(email, purpose, is_used, expires_at);
CREATE INDEX idx_verification_codes_cleanup ON verification_codes(expires_at) WHERE is_used = false;

-- Profiles 테이블 인덱스
CREATE UNIQUE INDEX idx_profiles_user_id ON profiles(user_id);

-- Events 테이블 인덱스 (이벤트 스토어)
CREATE INDEX idx_events_aggregate ON events(aggregate_id, event_version);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_events_occurred_at ON events(occurred_at);
```

### 6.2 SQLAlchemy ORM 모델 설계

#### Base 모델 및 공통 필드
```python
# infrastructure/persistence/models/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, func
from datetime import datetime

Base = declarative_base()

class TimestampMixin:
    """타임스탬프 공통 필드"""
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())

class VersionMixin:
    """낙관적 잠금용 버전 필드"""
    version = Column(Integer, nullable=False, default=1)
```

#### User 모델
```python
# infrastructure/persistence/models/user_model.py
from sqlalchemy import Column, String, DateTime, UUID, Enum as SQLEnum
from sqlalchemy.orm import relationship
from uuid import uuid4

class UserModel(Base, TimestampMixin, VersionMixin):
    __tablename__ = "users"
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), nullable=False, unique=True, index=True)
    status = Column(SQLEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    last_active_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    deactivated_at = Column(DateTime(timezone=True), nullable=True)
    
    # 관계 정의
    profile = relationship("ProfileModel", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions = relationship("SessionModel", back_populates="user", cascade="all, delete-orphan")
    
    @classmethod
    def from_entity(cls, user: User) -> 'UserModel':
        """엔티티에서 ORM 모델로 변환"""
        return cls(
            user_id=user.user_id,
            email=user.email.value,
            status=user.status,
            last_active_at=user.last_active_at,
            deactivated_at=user.deactivated_at,
            created_at=user.created_at
        )
    
    def to_entity(self) -> User:
        """ORM 모델에서 엔티티로 변환"""
        return User(
            user_id=self.user_id,
            email=Email(self.email),
            status=self.status,
            created_at=self.created_at,
            last_active_at=self.last_active_at,
            deactivated_at=self.deactivated_at
        )
    
    def update_from_entity(self, user: User) -> None:
        """엔티티 데이터로 모델 업데이트"""
        self.email = user.email.value
        self.status = user.status
        self.last_active_at = user.last_active_at
        self.deactivated_at = user.deactivated_at
        self.version += 1
```

#### Session 모델
```python
# infrastructure/persistence/models/session_model.py
from sqlalchemy import Column, UUID, ForeignKey, JSON, Boolean, DateTime
from sqlalchemy.orm import relationship

class SessionModel(Base, TimestampMixin, VersionMixin):
    __tablename__ = "sessions"
    
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    device_info = Column(JSON, nullable=False)  # JSONB 저장
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    is_active = Column(Boolean, nullable=False, default=True)
    
    # 관계
    user = relationship("UserModel", back_populates="sessions")
    
    @classmethod
    def from_entity(cls, session: Session) -> 'SessionModel':
        """엔티티에서 ORM 모델로 변환"""
        return cls(
            session_id=session.session_id,
            user_id=session.user_id,
            device_info={
                "user_agent": session.device_info.user_agent,
                "ip_address": session.device_info.ip_address,
                "device_fingerprint": session.device_info.device_fingerprint
            },
            expires_at=session.expires_at,
            last_accessed_at=session.last_accessed_at,
            is_active=session.is_active,
            created_at=session.created_at
        )
    
    def to_entity(self) -> Session:
        """ORM 모델에서 엔티티로 변환"""
        device_info = DeviceInfo(
            user_agent=self.device_info["user_agent"],
            ip_address=self.device_info["ip_address"],
            device_fingerprint=self.device_info["device_fingerprint"]
        )
        
        return Session(
            session_id=self.session_id,
            user_id=self.user_id,
            device_info=device_info,
            created_at=self.created_at,
            expires_at=self.expires_at,
            last_accessed_at=self.last_accessed_at,
            is_active=self.is_active
        )
```

### 6.3 데이터 일관성 및 트랜잭션 전략 설계

#### 트랜잭션 격리 수준 설정
```python
# infrastructure/persistence/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
            isolation_level="READ_COMMITTED"  # 기본 격리 수준
        )
        
        self.async_session = sessionmaker(
            self.engine, 
            class_=AsyncSession, 
            expire_on_commit=False
        )
    
    async def get_session(self) -> AsyncSession:
        """데이터베이스 세션 생성"""
        async with self.async_session() as session:
            yield session
```

#### 낙관적 잠금 구현
```python
# infrastructure/persistence/repositories/base_repository.py
from sqlalchemy.exc import StaleDataError
from sqlalchemy.orm.exc import StaleDataError as ORMStaleDataError

class BaseRepository:
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save_with_optimistic_lock(self, model) -> None:
        """낙관적 잠금으로 저장"""
        try:
            await self._session.merge(model)
            await self._session.flush()
        except (StaleDataError, ORMStaleDataError):
            raise ConcurrencyException("Data was modified by another transaction")
    
    async def update_with_version_check(self, model, expected_version: int) -> None:
        """버전 체크로 업데이트"""
        if model.version != expected_version:
            raise ConcurrencyException(f"Expected version {expected_version}, got {model.version}")
        
        model.version += 1
        await self.save_with_optimistic_lock(model)
```

#### 트랜잭션 경계 관리
```python
# infrastructure/persistence/unit_of_work.py
class UnitOfWork:
    """작업 단위 패턴"""
    
    def __init__(self, session: AsyncSession):
        self._session = session
        self._repositories = {}
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
    
    async def commit(self):
        """트랜잭션 커밋"""
        await self._session.commit()
    
    async def rollback(self):
        """트랜잭션 롤백"""
        await self._session.rollback()
    
    def get_repository(self, repo_class):
        """리포지토리 인스턴스 반환"""
        if repo_class not in self._repositories:
            self._repositories[repo_class] = repo_class(self._session)
        return self._repositories[repo_class]
```

### 6.4 데이터 마이그레이션 전략 설계 (Alembic)

#### Alembic 설정
```python
# infrastructure/persistence/migrations/alembic.ini
[alembic]
script_location = migrations
sqlalchemy.url = postgresql+asyncpg://user:pass@localhost/db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic
```

#### 마이그레이션 스크립트 예시
```python
# infrastructure/persistence/migrations/versions/001_initial_schema.py
"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Users 테이블 생성
    op.create_table('users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_active_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deactivated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email')
    )
    
    # 인덱스 생성
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_status', 'users', ['status'])

def downgrade():
    op.drop_table('users')
```

### 6.5 백업 및 복구 전략 설계

#### 자동 백업 스크립트
```python
# infrastructure/persistence/backup/backup_manager.py
import asyncio
import subprocess
from datetime import datetime, timedelta

class BackupManager:
    def __init__(self, db_config: DatabaseConfig):
        self.db_config = db_config
    
    async def create_backup(self, backup_type: str = "daily") -> str:
        """데이터베이스 백업 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_{backup_type}_{timestamp}.sql"
        
        cmd = [
            "pg_dump",
            "--host", self.db_config.host,
            "--port", str(self.db_config.port),
            "--username", self.db_config.username,
            "--dbname", self.db_config.database,
            "--file", backup_file,
            "--verbose",
            "--no-password"
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return backup_file
        else:
            raise BackupException(f"Backup failed: {stderr.decode()}")
    
    async def restore_backup(self, backup_file: str) -> bool:
        """백업에서 복구"""
        cmd = [
            "psql",
            "--host", self.db_config.host,
            "--port", str(self.db_config.port),
            "--username", self.db_config.username,
            "--dbname", self.db_config.database,
            "--file", backup_file
        ]
        
        process = await asyncio.create_subprocess_exec(*cmd)
        return_code = await process.wait()
        
        return return_code == 0
    
    async def cleanup_old_backups(self, retention_days: int = 30):
        """오래된 백업 파일 정리"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        # 백업 파일 정리 로직
```

#### 연결 풀 및 성능 최적화
```python
# infrastructure/persistence/connection_pool.py
class ConnectionPoolManager:
    """연결 풀 관리"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = None
    
    async def initialize(self):
        """연결 풀 초기화"""
        self.engine = create_async_engine(
            self.config.database_url,
            pool_size=self.config.pool_size,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=3600,  # 1시간마다 연결 재생성
            pool_pre_ping=True,  # 연결 유효성 사전 확인
            echo=self.config.echo_sql
        )
    
    async def get_connection(self):
        """연결 반환"""
        return self.engine.connect()
    
    async def close(self):
        """연결 풀 종료"""
        if self.engine:
            await self.engine.dispose()
```

## 7. 보안 및 인증 설계

### 7.1 JWT 토큰 구조 및 클레임 설계

#### JWT 토큰 구조 (요구사항 준수)
```python
# infrastructure/security/jwt_manager.py
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional

class JWTManager:
    """JWT 토큰 관리 - 7일 제한 준수"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expire = timedelta(days=7)  # 7일 고정 (요구사항)
    
    def create_access_token(self, user_id: str, session_id: str) -> str:
        """액세스 토큰 생성 (Refresh Token 없음)"""
        now = datetime.utcnow()
        expire = now + self.token_expire  # 7일 후 만료
        
        payload = {
            # 표준 클레임
            "iss": "auth-service",
            "sub": user_id,
            "aud": "api-service",
            "exp": expire,
            "iat": now,
            "jti": session_id,
            
            # 커스텀 클레임
            "user_id": user_id,
            "session_id": session_id,
            "scope": ["read", "write"]
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict:
        """토큰 검증"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                audience="api-service",
                issuer="auth-service"
            )
            return payload
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException("Token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidTokenException(f"Invalid token: {str(e)}")
```

### 7.2 세션 관리 및 토큰 갱신 전략 설계 (요구사항 준수)

#### 세션 기반 토큰 관리
```python
# application/services/session_security_service.py
class SessionSecurityService:
    """세션 보안 관리 서비스 - 7일 제한 준수"""
    
    def __init__(self, 
                 jwt_manager: JWTManager,
                 cache_service: CacheServiceInterface,
                 session_repo: SessionRepository):
        self._jwt_manager = jwt_manager
        self._cache_service = cache_service
        self._session_repo = session_repo
    
    async def create_secure_session(self, user_id: str, device_info: DeviceInfo) -> Dict:
        """보안 세션 생성"""
        # 1. 세션 엔티티 생성 (7일 만료)
        session = Session.create(user_id, device_info)
        
        # 2. JWT 토큰 생성 (7일 만료, Refresh Token 없음)
        access_token = self._jwt_manager.create_access_token(
            user_id=str(user_id),
            session_id=str(session.session_id)
        )
        
        # 3. 세션 데이터 캐시 저장
        session_data = {
            "user_id": str(user_id),
            "session_id": str(session.session_id),
            "device_fingerprint": device_info.device_fingerprint,
            "expires_at": session.expires_at.isoformat(),
            "is_active": True
        }
        
        await self._cache_service.cache_session(
            session.session_id, 
            session_data, 
            ttl_seconds=604800  # 7일
        )
        
        # 4. 데이터베이스에 세션 저장
        await self._session_repo.save(SessionAggregate.from_existing(session))
        
        return {
            "access_token": access_token,
            "expires_at": session.expires_at,
            "session_id": str(session.session_id)
        }
    
    async def extend_session_on_activity(self, session_id: str) -> Dict:
        """웹앱 활동 시 세션 연장 (요구사항: 자동 연장)"""
        # 1. 세션 조회
        session_aggregate = await self._session_repo.find_by_id(session_id)
        if not session_aggregate or session_aggregate.is_expired():
            raise SessionExpiredException("Session not found or expired")
        
        # 2. 세션 연장 (7일로 재설정)
        session_aggregate.extend()
        
        # 3. 새 토큰 생성 (7일 유효)
        new_access_token = self._jwt_manager.create_access_token(
            user_id=str(session_aggregate.session.user_id),
            session_id=str(session_aggregate.session.session_id)
        )
        
        # 4. 캐시 업데이트
        session_data = {
            "user_id": str(session_aggregate.session.user_id),
            "session_id": str(session_aggregate.session.session_id),
            "device_fingerprint": session_aggregate.session.device_info.device_fingerprint,
            "expires_at": session_aggregate.session.expires_at.isoformat(),
            "is_active": True
        }
        
        await self._cache_service.cache_session(
            session_aggregate.session.session_id,
            session_data,
            ttl_seconds=604800  # 7일로 재설정
        )
        
        # 5. 데이터베이스 업데이트
        await self._session_repo.save(session_aggregate)
        
        return {
            "access_token": new_access_token,
            "expires_at": session_aggregate.session.expires_at
        }
    
    async def validate_session(self, access_token: str) -> Dict:
        """세션 유효성 검증"""
        # 1. JWT 토큰 검증
        payload = self._jwt_manager.verify_token(access_token)
        
        # 2. 캐시에서 세션 확인
        session_data = await self._cache_service.get_session(payload["session_id"])
        if session_data and session_data["is_active"]:
            # 만료 시간 확인
            expires_at = datetime.fromisoformat(session_data["expires_at"])
            if datetime.utcnow() < expires_at:
                return session_data
        
        # 3. 캐시 미스 또는 만료 시 데이터베이스 확인
        session_aggregate = await self._session_repo.find_by_id(payload["session_id"])
        if not session_aggregate or session_aggregate.is_expired():
            raise SessionExpiredException("Session expired - 7 day limit reached")
        
        # 4. 캐시 재저장
        session_data = {
            "user_id": str(session_aggregate.session.user_id),
            "session_id": str(session_aggregate.session.session_id),
            "device_fingerprint": session_aggregate.session.device_info.device_fingerprint,
            "expires_at": session_aggregate.session.expires_at.isoformat(),
            "is_active": session_aggregate.session.is_active
        }
        
        await self._cache_service.cache_session(
            session_aggregate.session.session_id,
            session_data,
            ttl_seconds=int((session_aggregate.session.expires_at - datetime.utcnow()).total_seconds())
        )
        
        return session_data
```

### 7.3 비밀번호 없는 인증 플로우 설계

#### 이메일 기반 인증 플로우 (수정됨)
```python
# application/services/passwordless_auth_service.py
class PasswordlessAuthService:
    """비밀번호 없는 인증 서비스"""
    
    async def complete_login(self, email: str, code: str, device_info: DeviceInfo) -> Dict:
        """로그인 완료 - 코드 검증 및 세션 생성"""
        # 인증 코드 검증 로직... (동일)
        
        # 세션 생성 (7일 제한)
        session_data = await self._session_security_service.create_secure_session(
            user.user.user_id,
            device_info
        )
        
        return {
            "success": True,
            "access_token": session_data["access_token"],
            # refresh_token 제거!
            "expires_at": session_data["expires_at"],
            "user": {
                "user_id": str(user.user.user_id),
                "email": user.user.email.value,
                "status": user.user.status.value
            }
        }
```

### 7.4 API 보안 헤더 및 CORS 설정 설계

#### 자동 세션 연장 미들웨어
```python
# interfaces/api/middlewares/session_extension_middleware.py
class SessionExtensionMiddleware(BaseHTTPMiddleware):
    """웹앱 활동 시 자동 세션 연장 미들웨어"""
    
    def __init__(self, app, session_security_service: SessionSecurityService):
        super().__init__(app)
        self.session_security_service = session_security_service
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 인증된 요청에 대해서만 세션 연장
        if hasattr(request.state, "current_user"):
            session_id = request.state.current_user.get("session_id")
            if session_id:
                try:
                    # 세션 연장 및 새 토큰 발급
                    extended_session = await self.session_security_service.extend_session_on_activity(session_id)
                    
                    # 새 토큰을 응답 헤더에 추가
                    response.headers["X-New-Token"] = extended_session["access_token"]
                    response.headers["X-Token-Expires"] = extended_session["expires_at"].isoformat()
                    
                except SessionExpiredException:
                    # 세션이 이미 만료된 경우 (7일 초과)
                    response.headers["X-Session-Expired"] = "true"
                
        return response

# JWT 인증 의존성 (수정됨)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session_security_service: SessionSecurityService = Depends()
) -> dict:
    """현재 사용자 정보 조회 (7일 제한 적용)"""
    try:
        # 세션 유효성 검증 (7일 제한 확인)
        session_data = await session_security_service.validate_session(credentials.credentials)
        
        return {
            "user_id": session_data["user_id"],
            "session_id": session_data["session_id"],
            "session_data": session_data
        }
    except (TokenExpiredException, SessionExpiredException):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired - please login again"
        )
```

### 7.5 레이트 리미팅 및 DDoS 방어 설계

#### 요구사항 준수 레이트 리미터
```python
# infrastructure/security/rate_limiter.py
class RateLimiter:
    """Redis 기반 레이트 리미터"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.limits = {
            "login_request": {"count": 5, "window": 300},      # 5회/5분
            "login_verify": {"count": 10, "window": 300},      # 10회/5분
            "registration": {"count": 3, "window": 3600},      # 3회/1시간
            "session_extend": {"count": 100, "window": 3600},  # 세션 연장 제한
            "api_call": {"count": 1000, "window": 3600}       # 1000회/1시간
        }
    
    # 기존 로직 동일...
```

### 7.6 감사 로깅 및 보안 모니터링 설계

#### 7일 제한 모니터링
```python
# infrastructure/security/security_logger.py
class SecurityEventType(Enum):
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    SESSION_EXTENDED = "SESSION_EXTENDED"      # 새 이벤트
    SESSION_EXPIRED_7DAY = "SESSION_EXPIRED_7DAY"  # 7일 만료
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"

class SecurityLogger:
    async def log_session_extension(self, user_id: str, session_id: str, device_info: DeviceInfo):
        """세션 연장 로깅"""
        await self.log_event(
            "SESSION_EXTENDED",
            {
                "user_id": user_id,
                "session_id": session_id,
                "device_fingerprint": device_info.device_fingerprint,
                "extended_to": (datetime.utcnow() + timedelta(days=7)).isoformat()
            }
        )
    
    async def log_seven_day_expiry(self, user_id: str, session_id: str):
        """7일 만료 로깅"""
        await self.log_event(
            "SESSION_EXPIRED_7DAY",
            {
                "user_id": user_id,
                "session_id": session_id,
                "reason": "7_day_inactivity_limit"
            },
            severity="INFO"
        )
```

## 8. 이벤트 기반 아키텍처 설계

### 8.1 도메인 이벤트 발행 메커니즘 설계

#### 애그리게이트에서 이벤트 발행
```python
# domain/aggregates/user_aggregate.py
class UserAggregate:
    def __init__(self, user: User, profile: Profile):
        self._user = user
        self._profile = profile
        self._domain_events: List[DomainEvent] = []
    
    def _raise_event(self, event: DomainEvent):
        """도메인 이벤트 추가"""
        self._domain_events.append(event)
    
    def deactivate(self):
        """사용자 비활성화"""
        self._user.deactivate()
        self._raise_event(UserDeactivated(
            user_id=self._user.user_id,
            deactivated_at=self._user.deactivated_at,
            retention_until=self._user.deactivated_at + timedelta(days=365)
        ))
    
    def get_domain_events(self) -> List[DomainEvent]:
        return self._domain_events.copy()
    
    def clear_domain_events(self):
        self._domain_events.clear()
```

### 8.2 이벤트 스토어 스키마 설계

#### PostgreSQL 이벤트 스토어 (영구 보관)
```python
# infrastructure/events/postgresql_event_store.py
class PostgreSQLEventStore:
    """PostgreSQL 기반 이벤트 스토어 - 영구 보관용"""
    
    async def save_events(self, aggregate_id: UUID, events: List[DomainEvent]) -> None:
        """도메인 이벤트 영구 저장"""
        for event in events:
            event_model = EventModel(
                event_id=event.event_id,
                aggregate_id=aggregate_id,
                event_type=event.__class__.__name__,
                event_data=asdict(event),
                occurred_at=event.occurred_at
            )
            self._session.add(event_model)
        await self._session.flush()
    
    async def get_events(self, aggregate_id: UUID) -> List[DomainEvent]:
        """애그리게이트의 이벤트 조회"""
        # 감사, 디버깅, 데이터 복구용
        pass

# Events 테이블
class EventModel(Base):
    __tablename__ = "events"
    
    event_id = Column(UUID(as_uuid=True), primary_key=True)
    aggregate_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    event_data = Column(JSON, nullable=False)
    occurred_at = Column(DateTime(timezone=True), nullable=False, index=True)
```

### 8.3 이벤트 핸들러 등록 및 디스패치 설계

#### Redis Pub/Sub 기반 실시간 처리
```python
# infrastructure/events/redis_event_publisher.py
class RedisEventPublisher:
    """Redis 기반 실시간 이벤트 발행"""
    
    def __init__(self, redis_client):
        self._redis = redis_client
    
    async def publish_event(self, event: DomainEvent):
        """Redis로 실시간 이벤트 발행"""
        event_data = {
            'event_type': event.__class__.__name__,
            'data': asdict(event),
            'occurred_at': event.occurred_at.isoformat()
        }
        
        channel = f"events.{event.__class__.__name__}"
        await self._redis.publish(channel, json.dumps(event_data))

# 이벤트 핸들러 등록
def event_handler(event_type):
    """이벤트 핸들러 데코레이터"""
    def decorator(func):
        func._event_type = event_type.__name__
        return func
    return decorator

class UserEventHandlers:
    @event_handler(UserRegistered)
    async def handle_user_registered(self, event: UserRegistered):
        """사용자 등록 시 환영 이메일 발송"""
        await self._email_service.send_welcome_email(event.email)
    
    @event_handler(UserDeactivated)
    async def handle_user_deactivated(self, event: UserDeactivated):
        """사용자 비활성화 시 캐시 정리"""
        await self._cache_service.invalidate_user(event.user_id)
```

### 8.4 비동기 이벤트 처리 설계

#### 하이브리드 이벤트 발행
```python
# infrastructure/events/hybrid_event_publisher.py
class HybridEventPublisher:
    """PostgreSQL + Redis 하이브리드 이벤트 발행"""
    
    def __init__(self, event_store: PostgreSQLEventStore, redis_publisher: RedisEventPublisher):
        self._event_store = event_store  # 영구 보관
        self._redis_publisher = redis_publisher  # 실시간 알림
    
    async def publish_domain_events(self, aggregate_id: UUID, events: List[DomainEvent]):
        """이중 안전장치 이벤트 발행"""
        # 1. PostgreSQL에 영구 저장 (안전성)
        await self._event_store.save_events(aggregate_id, events)
        
        # 2. Redis로 실시간 발행 (속도)
        for event in events:
            await self._redis_publisher.publish_event(event)

# 애플리케이션 서비스에서 사용
class UserRegistrationApplicationService:
    @transactional
    async def complete_registration(self, command: CompleteRegistrationCommand):
        # 비즈니스 로직 수행
        user_aggregate = UserAggregate.create_new_user(...)
        await self._user_repo.save(user_aggregate)
        
        # 이벤트 발행 (PostgreSQL + Redis)
        events = user_aggregate.get_domain_events()
        if events:
            await self._event_publisher.publish_domain_events(
                user_aggregate.user.user_id, events
            )
            user_aggregate.clear_domain_events()
```

### 8.5 이벤트 재시도 및 실패 처리 설계

#### 실패 처리 메커니즘
```python
# infrastructure/events/event_retry_handler.py
class EventRetryHandler:
    """이벤트 처리 실패 시 재시도"""
    
    async def handle_with_retry(self, handler: Callable, event: DomainEvent):
        """3회 재시도"""
        for attempt in range(3):
            try:
                await handler(event)
                return
            except Exception as e:
                if attempt == 2:  # 마지막 시도
                    await self._handle_permanent_failure(event, e)
                else:
                    await asyncio.sleep(2 ** attempt)  # 지수 백오프
    
    async def _handle_permanent_failure(self, event: DomainEvent, error: Exception):
        """영구 실패 처리"""
        # PostgreSQL에서 이벤트 다시 읽어서 수동 처리 가능
        logger.error(f"Event permanently failed: {event}, error: {error}")
```

### 8.6 이벤트 버전 관리 및 스키마 진화 설계

#### 이벤트 버전 관리
```python
# domain/events/versioned_events.py
@dataclass
class UserRegisteredV1(DomainEvent):
    """사용자 등록 이벤트 V1"""
    user_id: UUID
    email: str
    registered_at: datetime

@dataclass  
class UserRegisteredV2(DomainEvent):
    """사용자 등록 이벤트 V2 - 프로필 정보 추가"""
    user_id: UUID
    email: str
    profile_id: UUID  # 새 필드
    gender: Optional[str]  # 새 필드
    registered_at: datetime

# 이벤트 핸들러에서 버전 호환성 처리
class UserEventHandlers:
    @event_handler(UserRegistered)
    async def handle_user_registered(self, event):
        """모든 버전의 UserRegistered 이벤트 처리"""
        # V1, V2 모두 처리 가능
        await self._send_welcome_email(event.email)
        
        # V2에만 있는 필드 처리
        if hasattr(event, 'profile_id'):
            await self._setup_default_preferences(event.profile_id)
```

## 이벤트 아키텍처 요약

### 이벤트 플로우
```
1. 비즈니스 로직 수행 → 도메인 이벤트 생성
2. PostgreSQL 저장 (영구 보관) 📚
3. Redis 발행 (실시간 알림) 📢
4. 이벤트 핸들러들이 Redis에서 받아서 처리
5. 실패 시 PostgreSQL에서 재처리 가능
```

### 장점
- **안전성**: PostgreSQL 영구 보관
- **속도**: Redis 실시간 처리  
- **복구**: 실패 시 재처리 가능
- **확장성**: 새 핸들러 쉽게 추가

## 9. 성능 및 확장성 설계

### 9.1 Redis 캐싱 레이어 설계

#### 3단계 캐싱 전략 구현
```python
# infrastructure/cache/redis_cache_service.py
class RedisCacheService:
    """Redis 기반 캐싱 서비스"""
    
    def __init__(self, redis_client):
        self._redis = redis_client
    
    # 1순위: 사용자 세션 캐싱 (가장 빈번한 접근)
    async def cache_session(self, session_id: UUID, session_data: dict, ttl: int = 604800):
        """세션 캐싱 - TTL 7일"""
        key = f"session:{session_id}"
        await self._redis.setex(key, ttl, json.dumps(session_data))
    
    async def get_session(self, session_id: UUID) -> Optional[dict]:
        """세션 조회 - 밀리초 응답"""
        key = f"session:{session_id}"
        data = await self._redis.get(key)
        return json.loads(data) if data else None
    
    # 2순위: 사용자 기본 정보 캐싱
    async def cache_user_info(self, user_id: UUID, user_data: dict, ttl: int = 3600):
        """사용자 기본 정보 캐싱 - TTL 1시간"""
        key = f"user:{user_id}"
        await self._redis.setex(key, ttl, json.dumps(user_data))
    
    async def get_user_info(self, user_id: UUID) -> Optional[dict]:
        """사용자 정보 조회"""
        key = f"user:{user_id}"
        data = await self._redis.get(key)
        return json.loads(data) if data else None
    
    # 3순위: 인증 코드 캐싱
    async def cache_verification_code(self, email: str, purpose: str, 
                                    code_data: dict, ttl: int = 900):
        """인증 코드 캐싱 - TTL 15분"""
        key = f"verification:{email}:{purpose}"
        await self._redis.setex(key, ttl, json.dumps(code_data))
    
    # 캐시 무효화 전략
    async def invalidate_user_cache(self, user_id: UUID):
        """사용자 관련 캐시 무효화"""
        patterns = [
            f"user:{user_id}",
            f"session:*"  # 사용자의 모든 세션 (복잡한 쿼리 필요)
        ]
        
        for pattern in patterns:
            if "*" in pattern:
                keys = await self._redis.keys(pattern)
                if keys:
                    await self._redis.delete(*keys)
            else:
                await self._redis.delete(pattern)

# 캐시 워밍업 전략
class CacheWarmupService:
    """캐시 워밍업 서비스"""
    
    async def warmup_user_cache(self, user_id: UUID):
        """사용자 로그인 시 관련 데이터 미리 캐싱"""
        # 사용자 기본 정보 캐싱
        user_data = await self._user_repo.find_basic_info(user_id)
        await self._cache_service.cache_user_info(user_id, user_data)
        
        # 활성 세션 정보 캐싱
        sessions = await self._session_repo.find_active_sessions_by_user_id(user_id)
        for session in sessions:
            session_data = {
                "user_id": str(session.user_id),
                "device_fingerprint": session.device_info.device_fingerprint,
                "expires_at": session.expires_at.isoformat()
            }
            await self._cache_service.cache_session(session.session_id, session_data)
```

### 9.2 PostgreSQL 쿼리 최적화 전략

#### 인덱스 기반 쿼리 최적화
```python
# infrastructure/persistence/optimized_queries.py
class OptimizedUserRepository:
    """최적화된 사용자 리포지토리"""
    
    async def find_by_email_optimized(self, email: Email) -> Optional[UserAggregate]:
        """이메일 조회 최적화 - UNIQUE 인덱스 활용"""
        # idx_users_email 인덱스 사용
        query = select(UserModel, ProfileModel).join(
            ProfileModel, UserModel.user_id == ProfileModel.user_id
        ).where(UserModel.email == email.value)
        
        result = await self._session.execute(query)
        row = result.first()
        
        if row:
            user_model, profile_model = row
            return UserAggregate.from_existing(
                user_model.to_entity(),
                profile_model.to_entity()
            )
        return None
    
    async def find_active_users_batch(self, user_ids: List[UUID]) -> List[UserAggregate]:
        """배치 사용자 조회 - IN 절 최적화"""
        # idx_users_status 인덱스 + Primary Key 활용
        query = select(UserModel, ProfileModel).join(
            ProfileModel, UserModel.user_id == ProfileModel.user_id
        ).where(
            UserModel.user_id.in_(user_ids),
            UserModel.status == UserStatus.ACTIVE
        )
        
        result = await self._session.execute(query)
        return [
            UserAggregate.from_existing(user_model.to_entity(), profile_model.to_entity())
            for user_model, profile_model in result
        ]

class OptimizedSessionRepository:
    """최적화된 세션 리포지토리"""
    
    async def find_active_sessions_optimized(self, user_id: UUID) -> List[SessionAggregate]:
        """활성 세션 조회 최적화 - 복합 인덱스 활용"""
        # idx_sessions_user_active 인덱스 사용
        query = select(SessionModel).where(
            SessionModel.user_id == user_id,
            SessionModel.is_active == True,
            SessionModel.expires_at > func.now()
        ).order_by(SessionModel.expires_at.asc())
        
        result = await self._session.execute(query)
        sessions = result.scalars().all()
        
        return [SessionAggregate.from_existing(s.to_entity()) for s in sessions]
    
    async def cleanup_expired_sessions_batch(self) -> int:
        """만료된 세션 배치 삭제 - 인덱스 최적화"""
        # idx_sessions_expires_cleanup 인덱스 사용
        query = delete(SessionModel).where(
            SessionModel.expires_at < func.now(),
            SessionModel.is_active == True
        )
        
        result = await self._session.execute(query)
        return result.rowcount

# 연결 풀 최적화
class OptimizedDatabaseConfig:
    """최적화된 데이터베이스 설정"""
    
    def __init__(self):
        self.pool_size = 20          # 기본 연결 수
        self.max_overflow = 30       # 최대 추가 연결
        self.pool_timeout = 30       # 연결 대기 시간
        self.pool_recycle = 3600     # 연결 재사용 시간 (1시간)
        self.pool_pre_ping = True    # 연결 유효성 사전 확인
        
        # 읽기 전용 복제본 설정
        self.read_replica_url = os.getenv("READ_REPLICA_URL")
        self.write_ratio = 0.3       # 30% 쓰기, 70% 읽기
```

### 9.3 API 응답 시간 최적화 설계

#### 응답 시간 최적화 전략
```python
# interfaces/api/middlewares/performance_middleware.py
class PerformanceMiddleware:
    """성능 최적화 미들웨어"""
    
    def __init__(self, app):
        self.app = app
        self.slow_query_threshold = 1.0  # 1초
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()
            
            # 요청 처리
            await self.app(scope, receive, send)
            
            # 응답 시간 측정
            duration = time.time() - start_time
            
            # 느린 쿼리 로깅
            if duration > self.slow_query_threshold:
                logger.warning(f"Slow request: {scope['path']} took {duration:.2f}s")

# 비동기 처리 최적화
class AsyncOptimizedAuthService:
    """비동기 최적화된 인증 서비스"""
    
    async def complete_login_optimized(self, command: CompleteLoginCommand):
        """로그인 완료 - 병렬 처리 최적화"""
        # 병렬로 처리 가능한 작업들
        tasks = [
            self._verify_code_async(command.email, command.verification_code),
            self._get_user_async(command.email),
            self._check_device_async(command.device_info)
        ]
        
        # 동시 실행
        code_valid, user_aggregate, device_known = await asyncio.gather(*tasks)
        
        if not code_valid:
            raise InvalidVerificationCodeException()
        
        # 세션 생성 (순차 처리 필요)
        session_data = await self._create_session_async(user_aggregate, command.device_info)
        
        # 백그라운드 작업 (응답 후 처리)
        asyncio.create_task(self._post_login_tasks(user_aggregate, session_data))
        
        return LoginResult(success=True, token=session_data["access_token"])
    
    async def _post_login_tasks(self, user_aggregate, session_data):
        """로그인 후 백그라운드 작업"""
        # 캐시 워밍업
        await self._cache_warmup_service.warmup_user_cache(user_aggregate.user.user_id)
        
        # 보안 로깅
        await self._security_logger.log_login_success(user_aggregate.user.user_id)
        
        # 이벤트 발행
        await self._event_publisher.publish_login_event(session_data)

# 응답 압축 및 캐싱
class ResponseOptimizationMiddleware:
    """응답 최적화 미들웨어"""
    
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        # 정적 응답 캐싱 (프로필 정보 등)
        if request.url.path.startswith("/api/profile"):
            response.headers["Cache-Control"] = "private, max-age=300"  # 5분
        
        # 압축 적용
        if "gzip" in request.headers.get("accept-encoding", ""):
            response.headers["Content-Encoding"] = "gzip"
        
        return response
```

### 9.4 동시성 제어 및 락 전략 설계

#### 낙관적 락 + 분산 락 전략
```python
# infrastructure/concurrency/distributed_lock.py
class DistributedLockManager:
    """Redis 기반 분산 락"""
    
    def __init__(self, redis_client):
        self._redis = redis_client
        self.default_timeout = 30  # 30초
    
    async def acquire_lock(self, resource_id: str, timeout: int = None) -> bool:
        """분산 락 획득"""
        timeout = timeout or self.default_timeout
        lock_key = f"lock:{resource_id}"
        lock_value = str(uuid4())
        
        # SET NX EX 명령으로 원자적 락 획득
        result = await self._redis.set(
            lock_key, 
            lock_value, 
            nx=True,  # 키가 없을 때만 설정
            ex=timeout  # 만료 시간
        )
        
        return result is True
    
    async def release_lock(self, resource_id: str, lock_value: str):
        """분산 락 해제"""
        lock_key = f"lock:{resource_id}"
        
        # Lua 스크립트로 원자적 해제
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        await self._redis.eval(lua_script, 1, lock_key, lock_value)

# 동시 로그인 제한에 분산 락 적용
class ConcurrentSessionManager:
    """동시 세션 관리 - 분산 락 적용"""
    
    def __init__(self, session_repo: SessionRepository, 
                 lock_manager: DistributedLockManager):
        self._session_repo = session_repo
        self._lock_manager = lock_manager
    
    async def create_session_with_limit(self, user_id: UUID, device_info: DeviceInfo):
        """동시 로그인 제한이 적용된 세션 생성"""
        lock_key = f"session_limit:{user_id}"
        
        # 사용자별 락 획득
        if not await self._lock_manager.acquire_lock(lock_key):
            raise ConcurrencyException("Session creation in progress")
        
        try:
            # 현재 활성 세션 수 확인
            active_sessions = await self._session_repo.find_active_sessions_by_user_id(user_id)
            
            # 동일 디바이스 확인
            existing_session = self._find_same_device_session(active_sessions, device_info)
            if existing_session:
                # 기존 세션 연장
                existing_session.extend()
                await self._session_repo.save(existing_session)
                return existing_session
            
            # 세션 제한 확인 (3개)
            if len(active_sessions) >= 3:
                # 가장 오래된 세션 종료
                oldest_session = min(active_sessions, key=lambda s: s.expires_at)
                oldest_session.expire()
                await self._session_repo.save(oldest_session)
            
            # 새 세션 생성
            new_session = SessionAggregate.create_new_session(user_id, device_info)
            await self._session_repo.save(new_session)
            
            return new_session
            
        finally:
            await self._lock_manager.release_lock(lock_key)

# 낙관적 락 재시도 전략
class OptimisticLockRetryService:
    """낙관적 락 재시도 서비스"""
    
    async def execute_with_retry(self, operation: Callable, max_retries: int = 3):
        """낙관적 락 충돌 시 재시도"""
        for attempt in range(max_retries):
            try:
                return await operation()
            except ConcurrencyException as e:
                if attempt == max_retries - 1:
                    raise e
                
                # 지수 백오프로 재시도
                await asyncio.sleep(0.1 * (2 ** attempt))
        
        raise ConcurrencyException("Max retries exceeded")
```

### 9.5 수평 확장 전략 설계

#### 마이크로서비스 분리 전략
```python
# 서비스 분리 경계
class ServiceBoundaries:
    """서비스 분리 경계 정의"""
    
    # 인증 서비스 (현재 Unit1)
    authentication_service = {
        "responsibilities": [
            "사용자 등록/로그인",
            "세션 관리", 
            "JWT 토큰 발급",
            "프로필 관리"
        ],
        "database": "auth_db",
        "cache": "auth_redis",
        "scaling_strategy": "stateless_horizontal"
    }
    
    # 향후 분리 가능한 서비스들
    notification_service = {
        "responsibilities": ["이메일 발송", "알림 관리"],
        "scaling_strategy": "queue_based"
    }
    
    audit_service = {
        "responsibilities": ["보안 로깅", "감사 추적"],
        "scaling_strategy": "event_driven"
    }

# 로드 밸런싱 전략
class LoadBalancingStrategy:
    """로드 밸런싱 전략"""
    
    def __init__(self):
        # 세션 기반 스티키 세션 (선택적)
        self.sticky_sessions = False  # JWT 사용으로 불필요
        
        # 라운드 로빈 + 헬스 체크
        self.balancing_algorithm = "round_robin"
        self.health_check_interval = 30  # 30초
        
        # 지역별 라우팅
        self.geo_routing = True
```

### 9.6 모니터링 및 메트릭 수집 설계

#### 성능 메트릭 수집
```python
# infrastructure/monitoring/metrics_collector.py
class MetricsCollector:
    """성능 메트릭 수집"""
    
    def __init__(self, redis_client):
        self._redis = redis_client
    
    async def record_api_latency(self, endpoint: str, duration: float):
        """API 응답 시간 기록"""
        key = f"metrics:latency:{endpoint}"
        await self._redis.lpush(key, duration)
        await self._redis.ltrim(key, 0, 999)  # 최근 1000개만 보관
    
    async def record_cache_hit_rate(self, cache_type: str, hit: bool):
        """캐시 히트율 기록"""
        key = f"metrics:cache:{cache_type}"
        value = 1 if hit else 0
        await self._redis.lpush(key, value)
        await self._redis.ltrim(key, 0, 9999)  # 최근 10000개
    
    async def record_concurrent_sessions(self, count: int):
        """동시 세션 수 기록"""
        timestamp = int(time.time())
        await self._redis.zadd("metrics:sessions", {timestamp: count})
        
        # 1일 이전 데이터 정리
        cutoff = timestamp - 86400
        await self._redis.zremrangebyscore("metrics:sessions", 0, cutoff)
    
    async def get_performance_summary(self) -> dict:
        """성능 요약 조회"""
        return {
            "avg_api_latency": await self._calculate_avg_latency(),
            "cache_hit_rate": await self._calculate_cache_hit_rate(),
            "peak_concurrent_sessions": await self._get_peak_sessions(),
            "error_rate": await self._calculate_error_rate()
        }

# 알림 및 임계값 모니터링
class PerformanceAlertManager:
    """성능 알림 관리"""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self._metrics = metrics_collector
        self.thresholds = {
            "api_latency": 2.0,      # 2초
            "cache_hit_rate": 0.8,   # 80%
            "error_rate": 0.05,      # 5%
            "concurrent_sessions": 10000  # 10,000개
        }
    
    async def check_performance_alerts(self):
        """성능 임계값 확인 및 알림"""
        summary = await self._metrics.get_performance_summary()
        
        alerts = []
        
        if summary["avg_api_latency"] > self.thresholds["api_latency"]:
            alerts.append(f"High API latency: {summary['avg_api_latency']:.2f}s")
        
        if summary["cache_hit_rate"] < self.thresholds["cache_hit_rate"]:
            alerts.append(f"Low cache hit rate: {summary['cache_hit_rate']:.2%}")
        
        if alerts:
            await self._send_performance_alert(alerts)
    
    async def _send_performance_alert(self, alerts: List[str]):
        """성능 알림 발송"""
        # Slack, 이메일 등으로 알림
        logger.warning(f"Performance alerts: {alerts}")
```

## 10. 테스트 전략 설계

### 10.1 pytest 기반 단위 테스트 구조 설계

#### 도메인 레이어 테스트
```python
# tests/unit/domain/test_user_aggregate.py
import pytest
from datetime import datetime, timedelta
from domain.aggregates.user_aggregate import UserAggregate
from domain.value_objects.email import Email
from domain.events.user_events import UserDeactivated

class TestUserAggregate:
    """사용자 애그리게이트 단위 테스트"""
    
    def test_create_new_user_should_generate_events(self):
        """새 사용자 생성 시 이벤트 발생 확인"""
        # Given
        email = Email("test@example.com")
        
        # When
        user_aggregate = UserAggregate.create_new_user(email, None, None)
        
        # Then
        events = user_aggregate.get_domain_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "UserRegistrationRequested"
        assert events[0].email == email
    
    def test_deactivate_user_should_set_retention_period(self):
        """사용자 비활성화 시 1년 보관 기간 설정"""
        # Given
        user_aggregate = UserAggregate.create_new_user(Email("test@example.com"), None, None)
        user_aggregate.clear_domain_events()
        
        # When
        user_aggregate.deactivate()
        
        # Then
        assert user_aggregate.user.status == UserStatus.DEACTIVATED
        assert user_aggregate.user.deactivated_at is not None
        
        events = user_aggregate.get_domain_events()
        deactivated_event = events[0]
        assert isinstance(deactivated_event, UserDeactivated)
        
        # 1년 보관 기간 확인
        expected_retention = user_aggregate.user.deactivated_at + timedelta(days=365)
        assert deactivated_event.retention_until == expected_retention

# tests/unit/domain/test_session_aggregate.py
class TestSessionAggregate:
    """세션 애그리게이트 단위 테스트"""
    
    def test_session_extend_should_reset_expiry_to_7_days(self):
        """세션 연장 시 7일로 재설정"""
        # Given
        device_info = DeviceInfo.create("Chrome", "192.168.1.1", "1920x1080", "Asia/Seoul", "ko")
        session_aggregate = SessionAggregate.create_new_session(uuid4(), device_info)
        
        original_expiry = session_aggregate.session.expires_at
        
        # When (1초 후 연장)
        time.sleep(0.001)
        session_aggregate.extend()
        
        # Then
        new_expiry = session_aggregate.session.expires_at
        assert new_expiry > original_expiry
        
        # 7일 후 만료 확인 (오차 1분 허용)
        expected_expiry = datetime.utcnow() + timedelta(days=7)
        assert abs((new_expiry - expected_expiry).total_seconds()) < 60

# tests/unit/domain/test_verification_code_policy.py
class TestVerificationCodePolicy:
    """인증 코드 정책 단위 테스트"""
    
    def test_code_should_expire_after_15_minutes(self):
        """인증 코드 15분 후 만료"""
        # Given
        policy = VerificationCodePolicy()
        created_at = datetime.utcnow()
        
        # When & Then
        # 14분 59초 후 - 유효
        almost_expired = created_at + timedelta(minutes=14, seconds=59)
        assert not policy.is_code_expired(almost_expired)
        
        # 15분 1초 후 - 만료
        expired = created_at + timedelta(minutes=15, seconds=1)
        assert policy.is_code_expired(expired)
```

#### 값 객체 테스트
```python
# tests/unit/domain/test_value_objects.py
class TestEmail:
    """이메일 값 객체 테스트"""
    
    @pytest.mark.parametrize("valid_email", [
        "test@example.com",
        "user.name@domain.co.kr",
        "123@test-domain.org"
    ])
    def test_valid_email_should_be_created(self, valid_email):
        """유효한 이메일 생성 테스트"""
        email = Email(valid_email)
        assert email.value == valid_email
    
    @pytest.mark.parametrize("invalid_email", [
        "invalid-email",
        "@domain.com",
        "test@",
        "test..test@domain.com"
    ])
    def test_invalid_email_should_raise_exception(self, invalid_email):
        """잘못된 이메일 형식 예외 테스트"""
        with pytest.raises(InvalidEmailFormatException):
            Email(invalid_email)

class TestDeviceInfo:
    """디바이스 정보 값 객체 테스트"""
    
    def test_same_device_fingerprint_should_be_equal(self):
        """동일한 디바이스 핑거프린트 확인"""
        # Given
        device1 = DeviceInfo.create("Chrome", "192.168.1.1", "1920x1080", "Asia/Seoul", "ko")
        device2 = DeviceInfo.create("Chrome", "192.168.1.2", "1920x1080", "Asia/Seoul", "ko")  # IP만 다름
        
        # When & Then
        assert device1.is_same_device(device2)  # 핑거프린트는 동일
    
    def test_different_device_should_not_be_equal(self):
        """다른 디바이스 구분 확인"""
        # Given
        device1 = DeviceInfo.create("Chrome", "192.168.1.1", "1920x1080", "Asia/Seoul", "ko")
        device2 = DeviceInfo.create("Safari", "192.168.1.1", "1366x768", "Asia/Seoul", "ko")  # 브라우저, 해상도 다름
        
        # When & Then
        assert not device1.is_same_device(device2)
```

### 10.2 통합 테스트 시나리오 설계

#### 데이터베이스 통합 테스트
```python
# tests/integration/test_user_repository.py
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from infrastructure.persistence.repositories.postgresql_user_repository import PostgreSQLUserRepository

@pytest.fixture
async def test_db_session():
    """테스트용 데이터베이스 세션"""
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost/test_db")
    
    async with engine.begin() as conn:
        # 테스트용 스키마 생성
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session
        await session.rollback()  # 테스트 후 롤백
    
    await engine.dispose()

class TestUserRepositoryIntegration:
    """사용자 리포지토리 통합 테스트"""
    
    async def test_save_and_find_user_with_profile(self, test_db_session):
        """사용자-프로필 저장 및 조회 통합 테스트"""
        # Given
        repo = PostgreSQLUserRepository(test_db_session)
        user_aggregate = UserAggregate.create_new_user(
            Email("test@example.com"), 
            Gender.male(), 
            BirthYear(1990)
        )
        
        # When
        await repo.save(user_aggregate)
        await test_db_session.commit()
        
        found_user = await repo.find_by_email(Email("test@example.com"))
        
        # Then
        assert found_user is not None
        assert found_user.user.email.value == "test@example.com"
        assert found_user.profile.gender.value == GenderType.MALE
        assert found_user.profile.birth_year.value == 1990
    
    async def test_concurrent_session_limit_enforcement(self, test_db_session):
        """동시 세션 제한 통합 테스트"""
        # Given
        session_repo = PostgreSQLSessionRepository(test_db_session)
        user_id = uuid4()
        
        # When - 4개 세션 생성 시도
        sessions = []
        for i in range(4):
            device_info = DeviceInfo.create(f"Device{i}", "192.168.1.1", "1920x1080", "Asia/Seoul", "ko")
            session = SessionAggregate.create_new_session(user_id, device_info)
            sessions.append(session)
            await session_repo.save(session)
        
        await test_db_session.commit()
        
        # Then - 활성 세션은 최대 3개
        active_sessions = await session_repo.find_active_sessions_by_user_id(user_id)
        assert len(active_sessions) <= 3
```

#### 캐시 통합 테스트
```python
# tests/integration/test_redis_cache.py
class TestRedisCacheIntegration:
    """Redis 캐시 통합 테스트"""
    
    @pytest.fixture
    async def redis_client(self):
        """테스트용 Redis 클라이언트"""
        import aioredis
        redis = await aioredis.from_url("redis://localhost:6379/1")  # 테스트 DB
        yield redis
        await redis.flushdb()  # 테스트 후 정리
        await redis.close()
    
    async def test_session_cache_ttl(self, redis_client):
        """세션 캐시 TTL 테스트"""
        # Given
        cache_service = RedisCacheService(redis_client)
        session_id = uuid4()
        session_data = {"user_id": str(uuid4()), "expires_at": datetime.utcnow().isoformat()}
        
        # When
        await cache_service.cache_session(session_id, session_data, ttl=2)  # 2초 TTL
        
        # Then
        # 즉시 조회 - 존재
        cached_data = await cache_service.get_session(session_id)
        assert cached_data == session_data
        
        # 3초 후 조회 - 만료
        await asyncio.sleep(3)
        expired_data = await cache_service.get_session(session_id)
        assert expired_data is None
```

### 10.3 FastAPI TestClient 기반 API 테스트 설계

#### API 엔드포인트 테스트
```python
# tests/api/test_auth_endpoints.py
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

class TestAuthEndpoints:
    """인증 API 엔드포인트 테스트"""
    
    @pytest.fixture
    def test_client(self):
        """테스트 클라이언트"""
        from interfaces.api.main import app
        return TestClient(app)
    
    @patch('application.services.user_registration_app_service.UserRegistrationApplicationService')
    def test_register_request_success(self, mock_service, test_client):
        """회원가입 요청 성공 테스트"""
        # Given
        mock_service.request_registration.return_value = RequestRegistrationResult(
            success=True, 
            message="Verification code sent"
        )
        
        request_data = {
            "email": "test@example.com",
            "gender": "MALE",
            "birth_year": 1990
        }
        
        # When
        response = test_client.post("/api/auth/register", json=request_data)
        
        # Then
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "Verification code sent" in response.json()["message"]
    
    def test_register_invalid_email_format(self, test_client):
        """잘못된 이메일 형식 검증 테스트"""
        # Given
        request_data = {
            "email": "invalid-email",
            "gender": "MALE"
        }
        
        # When
        response = test_client.post("/api/auth/register", json=request_data)
        
        # Then
        assert response.status_code == 422  # Validation Error
        assert "email" in response.json()["error"]["details"][0]["loc"]
    
    @patch('application.services.authentication_app_service.AuthenticationApplicationService')
    def test_login_complete_success(self, mock_service, test_client):
        """로그인 완료 성공 테스트"""
        # Given
        mock_service.complete_login.return_value = LoginResult(
            success=True,
            access_token="jwt_token_here",
            expires_at=datetime.utcnow() + timedelta(days=7),
            user={"user_id": str(uuid4()), "email": "test@example.com"}
        )
        
        request_data = {
            "email": "test@example.com",
            "verification_code": "123456",
            "screen_resolution": "1920x1080",
            "timezone": "Asia/Seoul",
            "language": "ko"
        }
        
        # When
        response = test_client.post(
            "/api/auth/login/verify", 
            json=request_data,
            headers={"User-Agent": "Chrome/119.0", "X-Forwarded-For": "192.168.1.1"}
        )
        
        # Then
        assert response.status_code == 200
        assert response.json()["success"] is True
        assert "access_token" in response.json()
        assert response.json()["access_token"] == "jwt_token_here"

# API 보안 테스트
class TestAPISecurityEndpoints:
    """API 보안 테스트"""
    
    def test_protected_endpoint_without_token(self, test_client):
        """토큰 없이 보호된 엔드포인트 접근"""
        # When
        response = test_client.get("/api/profile")
        
        # Then
        assert response.status_code == 401
        assert "Authorization header missing" in response.json()["error"]["message"]
    
    def test_protected_endpoint_with_invalid_token(self, test_client):
        """잘못된 토큰으로 보호된 엔드포인트 접근"""
        # When
        response = test_client.get(
            "/api/profile",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        # Then
        assert response.status_code == 401
        assert "Invalid token" in response.json()["error"]["message"]
```

### 10.4 성능 테스트 시나리오 설계

#### 부하 테스트
```python
# tests/performance/test_load_scenarios.py
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor

class TestLoadScenarios:
    """부하 테스트 시나리오"""
    
    async def test_concurrent_login_performance(self):
        """동시 로그인 성능 테스트"""
        # Given
        base_url = "http://localhost:8000"
        concurrent_users = 100
        
        async def login_user(session, user_id):
            """단일 사용자 로그인"""
            start_time = time.time()
            
            # 1. 로그인 요청
            login_data = {
                "email": f"user{user_id}@test.com",
                "screen_resolution": "1920x1080",
                "timezone": "Asia/Seoul",
                "language": "ko"
            }
            
            async with session.post(f"{base_url}/api/auth/login", json=login_data) as resp:
                assert resp.status == 200
            
            # 2. 인증 코드 검증 (모의)
            verify_data = {
                **login_data,
                "verification_code": "123456"
            }
            
            async with session.post(f"{base_url}/api/auth/login/verify", json=verify_data) as resp:
                assert resp.status == 200
                token = (await resp.json())["access_token"]
            
            # 3. 프로필 조회
            headers = {"Authorization": f"Bearer {token}"}
            async with session.get(f"{base_url}/api/profile", headers=headers) as resp:
                assert resp.status == 200
            
            return time.time() - start_time
        
        # When
        async with aiohttp.ClientSession() as session:
            tasks = [login_user(session, i) for i in range(concurrent_users)]
            response_times = await asyncio.gather(*tasks)
        
        # Then
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        print(f"Average response time: {avg_response_time:.2f}s")
        print(f"Max response time: {max_response_time:.2f}s")
        
        # 성능 기준 검증
        assert avg_response_time < 2.0  # 평균 2초 이내
        assert max_response_time < 5.0  # 최대 5초 이내
    
    async def test_session_limit_under_load(self):
        """부하 상황에서 세션 제한 정확성 테스트"""
        # Given
        user_email = "loadtest@example.com"
        concurrent_logins = 10  # 동시에 10개 로그인 시도
        
        async def attempt_login(session_num):
            """로그인 시도"""
            # 서로 다른 디바이스로 로그인
            device_data = {
                "email": user_email,
                "verification_code": "123456",
                "screen_resolution": f"{1920 + session_num}x1080",  # 다른 해상도
                "timezone": "Asia/Seoul",
                "language": "ko"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post("http://localhost:8000/api/auth/login/verify", json=device_data) as resp:
                    return resp.status == 200
        
        # When
        tasks = [attempt_login(i) for i in range(concurrent_logins)]
        results = await asyncio.gather(*tasks)
        
        # Then
        successful_logins = sum(results)
        
        # 동시 로그인 제한 확인 (최대 3개 + 기존 세션 갱신)
        assert successful_logins <= 3, f"Too many concurrent sessions: {successful_logins}"
```

### 10.5 보안 테스트 계획 설계

#### 보안 취약점 테스트
```python
# tests/security/test_security_vulnerabilities.py
class TestSecurityVulnerabilities:
    """보안 취약점 테스트"""
    
    def test_sql_injection_prevention(self, test_client):
        """SQL 인젝션 방어 테스트"""
        # Given - SQL 인젝션 시도
        malicious_email = "test@example.com'; DROP TABLE users; --"
        
        request_data = {
            "email": malicious_email,
            "gender": "MALE"
        }
        
        # When
        response = test_client.post("/api/auth/register", json=request_data)
        
        # Then - 정상적으로 검증 오류 발생 (SQL 실행 안됨)
        assert response.status_code == 422
        assert "email" in str(response.json())
    
    def test_xss_prevention_in_user_agent(self, test_client):
        """User-Agent XSS 방어 테스트"""
        # Given
        malicious_user_agent = "<script>alert('XSS')</script>"
        
        # When
        response = test_client.post(
            "/api/auth/login",
            json={"email": "test@example.com", "screen_resolution": "1920x1080", "timezone": "Asia/Seoul", "language": "ko"},
            headers={"User-Agent": malicious_user_agent}
        )
        
        # Then - 요청은 처리되지만 스크립트는 새니타이징됨
        assert response.status_code in [200, 400]  # 비즈니스 로직에 따라
        # 로그에서 스크립트 태그가 제거되었는지 확인 (별도 검증)
    
    def test_rate_limiting_enforcement(self, test_client):
        """레이트 리미팅 적용 테스트"""
        # Given
        request_data = {"email": "test@example.com"}
        
        # When - 연속으로 6회 요청 (제한: 5회/5분)
        responses = []
        for _ in range(6):
            response = test_client.post("/api/auth/login", json=request_data)
            responses.append(response.status_code)
        
        # Then - 6번째 요청은 429 (Too Many Requests)
        assert responses[-1] == 429
        assert responses[:-1] == [200] * 5  # 처음 5개는 성공
    
    def test_jwt_token_expiration(self, test_client):
        """JWT 토큰 만료 테스트"""
        # Given - 만료된 토큰 (테스트용으로 생성)
        expired_token = create_expired_jwt_token()
        
        # When
        response = test_client.get(
            "/api/profile",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        # Then
        assert response.status_code == 401
        assert "expired" in response.json()["error"]["message"].lower()

def create_expired_jwt_token() -> str:
    """테스트용 만료된 JWT 토큰 생성"""
    import jwt
    from datetime import datetime, timedelta
    
    payload = {
        "user_id": str(uuid4()),
        "session_id": str(uuid4()),
        "exp": datetime.utcnow() - timedelta(hours=1)  # 1시간 전 만료
    }
    
    return jwt.encode(payload, "test_secret", algorithm="HS256")
```

### 10.6 테스트 데이터 관리 전략 설계

#### 테스트 픽스처 및 팩토리
```python
# tests/fixtures/test_factories.py
class UserAggregateFactory:
    """사용자 애그리게이트 팩토리"""
    
    @staticmethod
    def create_active_user(email: str = None, gender: str = None, birth_year: int = None) -> UserAggregate:
        """활성 사용자 생성"""
        return UserAggregate.create_new_user(
            Email(email or f"user{uuid4().hex[:8]}@test.com"),
            Gender.from_string(gender) if gender else None,
            BirthYear(birth_year) if birth_year else None
        )
    
    @staticmethod
    def create_deactivated_user() -> UserAggregate:
        """비활성화된 사용자 생성"""
        user = UserAggregateFactory.create_active_user()
        user.deactivate()
        return user

class SessionAggregateFactory:
    """세션 애그리게이트 팩토리"""
    
    @staticmethod
    def create_active_session(user_id: UUID = None, device_type: str = "Chrome") -> SessionAggregate:
        """활성 세션 생성"""
        device_info = DeviceInfo.create(
            user_agent=f"{device_type}/119.0",
            ip_address="192.168.1.1",
            screen_resolution="1920x1080",
            timezone="Asia/Seoul",
            language="ko"
        )
        
        return SessionAggregate.create_new_session(
            user_id or uuid4(),
            device_info
        )

# 테스트 데이터베이스 관리
class TestDatabaseManager:
    """테스트 데이터베이스 관리"""
    
    @staticmethod
    async def setup_test_data(session: AsyncSession):
        """테스트 데이터 설정"""
        # 기본 테스트 사용자들 생성
        test_users = [
            UserAggregateFactory.create_active_user("active@test.com", "MALE", 1990),
            UserAggregateFactory.create_deactivated_user(),
        ]
        
        for user in test_users:
            user_model = UserModel.from_entity(user.user)
            profile_model = ProfileModel.from_entity(user.profile)
            session.add(user_model)
            session.add(profile_model)
        
        await session.commit()
    
    @staticmethod
    async def cleanup_test_data(session: AsyncSession):
        """테스트 데이터 정리"""
        # 모든 테스트 데이터 삭제
        await session.execute(delete(SessionModel))
        await session.execute(delete(ProfileModel))
        await session.execute(delete(UserModel))
        await session.execute(delete(VerificationCodeModel))
        await session.commit()

# pytest 설정
# conftest.py
@pytest.fixture(scope="session")
def event_loop():
    """이벤트 루프 픽스처"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def clean_database():
    """깨끗한 테스트 데이터베이스"""
    # 테스트 전 정리
    async with get_test_db_session() as session:
        await TestDatabaseManager.cleanup_test_data(session)
        yield session
        # 테스트 후 정리
        await TestDatabaseManager.cleanup_test_data(session)
```

## 11. 배포 및 운영 설계

### 11.1 AWS 인프라 아키텍처 설계 (RDS, ElastiCache, ECS)

#### AWS 인프라 구성도
```yaml
# infrastructure/aws/infrastructure.yml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Unit1 Authentication Service Infrastructure'

Parameters:
  Environment:
    Type: String
    Default: 'dev'
    AllowedValues: ['dev', 'staging', 'prod']

Resources:
  # VPC 및 네트워킹
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-auth-vpc'

  # 프라이빗 서브넷 (데이터베이스용)
  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']

  PrivateSubnet2:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [1, !GetAZs '']

  # 퍼블릭 서브넷 (로드 밸런서용)
  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.101.0/24
      AvailabilityZone: !Select [0, !GetAZs '']

  # RDS PostgreSQL (Primary + Read Replica)
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: 'Subnet group for auth database'
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2

  AuthDatabase:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: !Sub '${Environment}-auth-db'
      DBInstanceClass: 
        !If [IsProd, 'db.r5.large', 'db.t3.micro']
      Engine: postgres
      EngineVersion: '15.4'
      AllocatedStorage: !If [IsProd, 100, 20]
      StorageType: gp2
      DBName: authdb
      MasterUsername: authuser
      MasterUserPassword: !Ref DBPassword
      DBSubnetGroupName: !Ref DBSubnetGroup
      VpcSecurityGroups:
        - !Ref DatabaseSecurityGroup
      BackupRetentionPeriod: !If [IsProd, 7, 1]
      MultiAZ: !If [IsProd, true, false]

  # ElastiCache Redis (캐시 + 세션 스토어)
  CacheSubnetGroup:
    Type: AWS::ElastiCache::SubnetGroup
    Properties:
      Description: 'Subnet group for Redis cache'
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2

  RedisCache:
    Type: AWS::ElastiCache::ReplicationGroup
    Properties:
      ReplicationGroupId: !Sub '${Environment}-auth-redis'
      Description: 'Redis for auth service'
      NodeType: !If [IsProd, 'cache.r6g.large', 'cache.t3.micro']
      NumCacheClusters: !If [IsProd, 2, 1]
      Engine: redis
      EngineVersion: '7.0'
      Port: 6379
      CacheSubnetGroupName: !Ref CacheSubnetGroup
      SecurityGroupIds:
        - !Ref CacheSecurityGroup
      AtRestEncryptionEnabled: true
      TransitEncryptionEnabled: true

  # ECS 클러스터 (컨테이너 실행)
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: !Sub '${Environment}-auth-cluster'
      CapacityProviders:
        - FARGATE
        - FARGATE_SPOT

Conditions:
  IsProd: !Equals [!Ref Environment, 'prod']
```

#### ECS 서비스 정의
```yaml
# infrastructure/aws/ecs-service.yml
version: '3.8'
services:
  auth-service:
    image: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/auth-service:${IMAGE_TAG}
    cpu: 512
    memory: 1024
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
      - AWS_REGION=${AWS_REGION}
    logging:
      driver: awslogs
      options:
        awslogs-group: /ecs/auth-service
        awslogs-region: ${AWS_REGION}
        awslogs-stream-prefix: ecs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
```

### 11.2 CI/CD 파이프라인 설계 (GitHub Actions)

#### GitHub Actions 워크플로우
```yaml
# .github/workflows/deploy.yml
name: Deploy Auth Service

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  AWS_REGION: ap-northeast-2
  ECR_REPOSITORY: auth-service

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_auth
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      env:
        DATABASE_URL: postgresql://postgres:test@localhost/test_auth
        REDIS_URL: redis://localhost:6379/1
      run: |
        pytest tests/ -v --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  security-scan:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run security scan
      uses: securecodewarrior/github-action-add-sarif@v1
      with:
        sarif-file: 'security-scan-results.sarif'

  build-and-deploy:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push Docker image
      env:
        ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
        IMAGE_TAG: ${{ github.sha }}
      run: |
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
        docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest
        docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest
    
    - name: Deploy to ECS
      env:
        IMAGE_TAG: ${{ github.sha }}
      run: |
        aws ecs update-service \
          --cluster prod-auth-cluster \
          --service auth-service \
          --force-new-deployment
```

#### Dockerfile 최적화
```dockerfile
# Dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

# 의존성 설치 (캐시 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 멀티스테이지 빌드 (프로덕션)
FROM python:3.11-slim

WORKDIR /app

# 보안: 비루트 사용자 생성
RUN groupadd -r appuser && useradd -r -g appuser appuser

# 의존성 복사
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 애플리케이션 코드 복사
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .

# 권한 설정
RUN chown -R appuser:appuser /app
USER appuser

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "src.interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 11.3 환경별 설정 관리 설계 (Pydantic Settings)

#### 환경별 설정 클래스
```python
# src/infrastructure/config/settings.py
from pydantic import BaseSettings, Field
from typing import Optional
import os

class DatabaseSettings(BaseSettings):
    """데이터베이스 설정"""
    url: str = Field(..., env="DATABASE_URL")
    pool_size: int = Field(10, env="DB_POOL_SIZE")
    max_overflow: int = Field(20, env="DB_MAX_OVERFLOW")
    pool_timeout: int = Field(30, env="DB_POOL_TIMEOUT")
    echo_sql: bool = Field(False, env="DB_ECHO_SQL")

class CacheSettings(BaseSettings):
    """캐시 설정"""
    redis_url: str = Field(..., env="REDIS_URL")
    session_ttl: int = Field(604800, env="SESSION_TTL")  # 7일
    user_info_ttl: int = Field(3600, env="USER_INFO_TTL")  # 1시간

class SecuritySettings(BaseSettings):
    """보안 설정"""
    jwt_secret: str = Field(..., env="JWT_SECRET")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    session_expire_days: int = Field(7, env="SESSION_EXPIRE_DAYS")
    
    # AWS SES 설정
    aws_access_key_id: str = Field(..., env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(..., env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field("ap-northeast-2", env="AWS_REGION")
    sender_email: str = Field(..., env="SENDER_EMAIL")

class AppSettings(BaseSettings):
    """애플리케이션 설정"""
    environment: str = Field("dev", env="ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    # CORS 설정
    allowed_origins: list = Field(["http://localhost:3000"], env="ALLOWED_ORIGINS")
    
    # 레이트 리미팅
    rate_limit_per_minute: int = Field(60, env="RATE_LIMIT_PER_MINUTE")
    
    class Config:
        env_file = f".env.{os.getenv('ENVIRONMENT', 'dev')}"
        case_sensitive = False

class Settings(BaseSettings):
    """통합 설정"""
    database: DatabaseSettings = DatabaseSettings()
    cache: CacheSettings = CacheSettings()
    security: SecuritySettings = SecuritySettings()
    app: AppSettings = AppSettings()
    
    @property
    def is_production(self) -> bool:
        return self.app.environment == "prod"
    
    @property
    def is_development(self) -> bool:
        return self.app.environment == "dev"

# 싱글톤 설정 인스턴스
settings = Settings()
```

#### 환경별 설정 파일
```bash
# .env.dev
ENVIRONMENT=dev
DEBUG=true
LOG_LEVEL=DEBUG

DATABASE_URL=postgresql://dev_user:dev_pass@localhost/dev_auth_db
REDIS_URL=redis://localhost:6379/0

JWT_SECRET=dev_jwt_secret_key_change_in_production
SENDER_EMAIL=noreply-dev@yourdomain.com

ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8080"]
RATE_LIMIT_PER_MINUTE=1000

# .env.prod
ENVIRONMENT=prod
DEBUG=false
LOG_LEVEL=INFO

DATABASE_URL=postgresql://prod_user:${DB_PASSWORD}@prod-auth-db.cluster-xxx.ap-northeast-2.rds.amazonaws.com/authdb
REDIS_URL=redis://prod-auth-redis.xxx.cache.amazonaws.com:6379

JWT_SECRET=${JWT_SECRET}
SENDER_EMAIL=noreply@yourdomain.com

ALLOWED_ORIGINS=["https://yourdomain.com"]
RATE_LIMIT_PER_MINUTE=100
```

### 11.4 로깅 및 모니터링 시스템 설계 (CloudWatch)

#### 구조화된 로깅 설정
```python
# src/infrastructure/logging/logger_config.py
import logging
import json
from datetime import datetime
from typing import Dict, Any

class JSONFormatter(logging.Formatter):
    """JSON 형식 로그 포매터"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # 추가 컨텍스트 정보
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        # 예외 정보
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

def setup_logging(settings: AppSettings):
    """로깅 설정"""
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.log_level))
    
    # 핸들러 설정
    if settings.is_production:
        # 프로덕션: JSON 형식으로 CloudWatch에 전송
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
    else:
        # 개발: 읽기 쉬운 형식
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
    
    root_logger.addHandler(handler)
    
    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('uvicorn.access').setLevel(logging.INFO)

# 로깅 미들웨어
class LoggingMiddleware:
    """요청 로깅 미들웨어"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request_id = str(uuid4())
            start_time = time.time()
            
            # 요청 로깅
            logger.info(
                f"Request started: {scope['method']} {scope['path']}",
                extra={
                    'request_id': request_id,
                    'method': scope['method'],
                    'path': scope['path'],
                    'client_ip': scope.get('client', ['unknown'])[0]
                }
            )
            
            # 요청 처리
            await self.app(scope, receive, send)
            
            # 응답 로깅
            duration = time.time() - start_time
            logger.info(
                f"Request completed in {duration:.3f}s",
                extra={
                    'request_id': request_id,
                    'duration': duration
                }
            )
```

#### CloudWatch 메트릭 및 알람
```python
# src/infrastructure/monitoring/cloudwatch_metrics.py
import boto3
from datetime import datetime

class CloudWatchMetrics:
    """CloudWatch 메트릭 발송"""
    
    def __init__(self, aws_region: str):
        self.cloudwatch = boto3.client('cloudwatch', region_name=aws_region)
        self.namespace = 'AuthService'
    
    async def put_metric(self, metric_name: str, value: float, 
                        unit: str = 'Count', dimensions: Dict = None):
        """메트릭 발송"""
        try:
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=[
                    {
                        'MetricName': metric_name,
                        'Value': value,
                        'Unit': unit,
                        'Timestamp': datetime.utcnow(),
                        'Dimensions': [
                            {'Name': k, 'Value': v} 
                            for k, v in (dimensions or {}).items()
                        ]
                    }
                ]
            )
        except Exception as e:
            logger.error(f"Failed to send metric {metric_name}: {e}")
    
    async def record_api_latency(self, endpoint: str, duration: float):
        """API 응답 시간 메트릭"""
        await self.put_metric(
            'APILatency',
            duration * 1000,  # 밀리초 단위
            'Milliseconds',
            {'Endpoint': endpoint}
        )
    
    async def record_login_success(self):
        """로그인 성공 메트릭"""
        await self.put_metric('LoginSuccess', 1)
    
    async def record_login_failure(self, reason: str):
        """로그인 실패 메트릭"""
        await self.put_metric(
            'LoginFailure', 
            1, 
            dimensions={'Reason': reason}
        )
    
    async def record_concurrent_sessions(self, count: int):
        """동시 세션 수 메트릭"""
        await self.put_metric('ConcurrentSessions', count, 'Count')

# CloudWatch 알람 설정 (Terraform)
resource "aws_cloudwatch_metric_alarm" "high_api_latency" {
  alarm_name          = "${var.environment}-auth-high-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "APILatency"
  namespace           = "AuthService"
  period              = "300"
  statistic           = "Average"
  threshold           = "2000"  # 2초
  alarm_description   = "This metric monitors API latency"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "high_error_rate" {
  alarm_name          = "${var.environment}-auth-high-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "LoginFailure"
  namespace           = "AuthService"
  period              = "300"
  statistic           = "Sum"
  threshold           = "50"  # 5분간 50회 이상 실패
  alarm_description   = "This metric monitors login failure rate"
  alarm_actions       = [aws_sns_topic.alerts.arn]
}
```

### 11.5 알림 및 장애 대응 프로세스 설계

#### 알림 시스템
```python
# src/infrastructure/notifications/alert_manager.py
class AlertManager:
    """알림 관리자"""
    
    def __init__(self, sns_client, slack_webhook_url: str):
        self.sns = sns_client
        self.slack_webhook = slack_webhook_url
    
    async def send_critical_alert(self, title: str, message: str, details: Dict = None):
        """중요 알림 발송"""
        # SNS로 이메일/SMS 발송
        await self._send_sns_alert(title, message, 'critical')
        
        # Slack으로 즉시 알림
        await self._send_slack_alert(title, message, 'danger', details)
    
    async def send_warning_alert(self, title: str, message: str):
        """경고 알림 발송"""
        await self._send_slack_alert(title, message, 'warning')
    
    async def _send_slack_alert(self, title: str, message: str, 
                               color: str, details: Dict = None):
        """Slack 알림 발송"""
        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": title,
                    "text": message,
                    "fields": [
                        {"title": k, "value": str(v), "short": True}
                        for k, v in (details or {}).items()
                    ],
                    "footer": "Auth Service",
                    "ts": int(time.time())
                }
            ]
        }
        
        async with aiohttp.ClientSession() as session:
            await session.post(self.slack_webhook, json=payload)

# 장애 대응 자동화
class IncidentResponseAutomation:
    """장애 대응 자동화"""
    
    async def handle_database_connection_failure(self):
        """데이터베이스 연결 실패 대응"""
        # 1. 연결 풀 재시작
        await self._restart_connection_pool()
        
        # 2. 읽기 전용 모드로 전환
        await self._enable_readonly_mode()
        
        # 3. 알림 발송
        await self.alert_manager.send_critical_alert(
            "Database Connection Failure",
            "Switched to read-only mode. Manual intervention required."
        )
    
    async def handle_high_memory_usage(self, usage_percent: float):
        """높은 메모리 사용률 대응"""
        if usage_percent > 90:
            # 캐시 정리
            await self._clear_non_essential_cache()
            
            # 가비지 컬렉션 강제 실행
            import gc
            gc.collect()
            
            await self.alert_manager.send_warning_alert(
                "High Memory Usage",
                f"Memory usage: {usage_percent}%. Cache cleared."
            )
```

### 11.6 백업 및 재해 복구 계획 설계

#### 자동 백업 시스템
```python
# src/infrastructure/backup/backup_manager.py
class BackupManager:
    """백업 관리자"""
    
    def __init__(self, s3_client, rds_client):
        self.s3 = s3_client
        self.rds = rds_client
        self.backup_bucket = "auth-service-backups"
    
    async def create_database_backup(self):
        """데이터베이스 백업 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        snapshot_id = f"auth-db-backup-{timestamp}"
        
        # RDS 스냅샷 생성
        response = await self.rds.create_db_snapshot(
            DBSnapshotIdentifier=snapshot_id,
            DBInstanceIdentifier="prod-auth-db"
        )
        
        # 백업 메타데이터 저장
        metadata = {
            "snapshot_id": snapshot_id,
            "created_at": timestamp,
            "type": "automated",
            "retention_days": 30
        }
        
        await self.s3.put_object(
            Bucket=self.backup_bucket,
            Key=f"metadata/{snapshot_id}.json",
            Body=json.dumps(metadata)
        )
        
        return snapshot_id
    
    async def cleanup_old_backups(self, retention_days: int = 30):
        """오래된 백업 정리"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # 오래된 스냅샷 조회
        snapshots = await self.rds.describe_db_snapshots(
            DBInstanceIdentifier="prod-auth-db",
            SnapshotType="manual"
        )
        
        for snapshot in snapshots['DBSnapshots']:
            if snapshot['SnapshotCreateTime'] < cutoff_date:
                await self.rds.delete_db_snapshot(
                    DBSnapshotIdentifier=snapshot['DBSnapshotIdentifier']
                )

# 재해 복구 절차
class DisasterRecoveryManager:
    """재해 복구 관리자"""
    
    async def initiate_failover_to_read_replica(self):
        """읽기 복제본으로 페일오버"""
        # 1. 읽기 복제본을 마스터로 승격
        await self.rds.promote_read_replica(
            DBInstanceIdentifier="prod-auth-db-replica"
        )
        
        # 2. DNS 레코드 업데이트
        await self._update_dns_record(
            "auth-db.internal.yourdomain.com",
            "prod-auth-db-replica.cluster-xxx.ap-northeast-2.rds.amazonaws.com"
        )
        
        # 3. 애플리케이션 재시작
        await self._restart_ecs_service()
        
        # 4. 알림 발송
        await self.alert_manager.send_critical_alert(
            "Database Failover Completed",
            "Failed over to read replica. Service restored."
        )
    
    async def restore_from_backup(self, snapshot_id: str):
        """백업에서 복구"""
        # 새 DB 인스턴스 생성
        restore_id = f"restored-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        await self.rds.restore_db_instance_from_db_snapshot(
            DBInstanceIdentifier=restore_id,
            DBSnapshotIdentifier=snapshot_id,
            DBInstanceClass="db.r5.large"
        )
        
        return restore_id

## 12. 문서화 및 검토

### 12.1 FastAPI 자동 API 문서 생성 설계

#### OpenAPI 스펙 자동 생성
```python
# src/interfaces/api/documentation.py
def custom_openapi_schema(app: FastAPI):
    """커스텀 OpenAPI 스키마 생성"""
    openapi_schema = get_openapi(
        title="Authentication & Profile Management API",
        version="1.0.0",
        description="""
        ## Unit1 인증 및 프로필 관리 API
        
        ### 주요 기능
        - 이메일 기반 회원가입/로그인
        - JWT 토큰 기반 인증 (7일 자동 연장)
        - 세션 관리 (최대 3개 동시 로그인)
        - 프로필 관리 (성별, 출생년도, 언어)
        """,
        routes=app.routes
    )
    
    # 보안 스키마 추가
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    return openapi_schema
```

### 12.2 아키텍처 결정 기록(ADR) 작성

#### 주요 ADR 문서
```markdown
# ADR-001: PostgreSQL vs DynamoDB 선택

## 결정: PostgreSQL 선택

## 근거
- User-Profile 강한 일관성 요구
- 이메일 유일성 보장 (UNIQUE 제약)
- 복잡한 쿼리 지원 (세션 만료, JOIN)
- ACID 트랜잭션으로 데이터 무결성 보장

# ADR-002: JWT + 세션 하이브리드 방식

## 결정: JWT + Redis 세션 조합

## 근거
- JWT: 빠른 토큰 검증, 상태 없음
- Redis 세션: 정확한 세션 제한, 즉시 무효화
- 성능과 정확성 모두 확보
```

### 12.3 코드 리뷰 가이드라인 작성

#### 리뷰 체크리스트
```markdown
## 도메인 레이어 리뷰
- [ ] 비즈니스 규칙이 올바르게 구현되었는가?
- [ ] 도메인 이벤트가 적절한 시점에 발행되는가?
- [ ] 불변식이 보장되는가?

## 보안 리뷰
- [ ] 입력 검증이 적용되었는가?
- [ ] 인증/인가가 올바른가?
- [ ] SQL 인젝션 방어가 되어있는가?

## 성능 리뷰
- [ ] N+1 쿼리 문제가 없는가?
- [ ] 캐시 전략이 적절한가?
- [ ] 트랜잭션 범위가 최적인가?
```

### 12.4 운영 가이드 작성

#### 장애 대응 매뉴얼
```markdown
## 일상 운영 체크리스트
- [ ] API 응답시간 < 2초 확인
- [ ] 오류율 < 5% 확인
- [ ] 캐시 히트율 > 80% 확인

## 장애 대응 절차

### 높은 API 지연시간
1. 로그 확인: `aws logs tail /ecs/auth-service`
2. 캐시 상태 확인: `redis-cli info memory`
3. DB 연결 확인: `psql -h db-host -c "SELECT 1;"`

### 데이터베이스 연결 실패
1. 읽기 복제본으로 페일오버
2. DNS 업데이트
3. 애플리케이션 재시작
```

### 12.5 논리적 설계 검토 및 승인

#### 설계 완성도 검증
```markdown
## 요구사항 준수 확인 ✅
- [x] 이메일 기반 인증 (15분 코드 유효)
- [x] 7일 세션 + 자동 연장
- [x] 최대 3개 동시 로그인
- [x] 프로필 관리 (성별, 출생년도, 언어)
- [x] 1년 데이터 보관 후 삭제

## 아키텍처 품질 확인 ✅
- [x] DDD 전술적 패턴 완전 적용
- [x] 헥사고날 아키텍처 구조
- [x] 이벤트 기반 아키텍처
- [x] PostgreSQL + Redis 최적화

## 성능 목표 달성 ✅
- [x] API 응답시간 < 2초
- [x] 동시 사용자 10,000명 지원
- [x] 캐시 히트율 > 80%
- [x] 수평 확장 가능
```

### 12.6 구현 가이드라인 작성

#### 개발 시작 가이드
```markdown
## 구현 순서
1. **도메인 레이어**: 값 객체 → 엔티티 → 애그리게이트
2. **인프라 레이어**: PostgreSQL → Redis → 이벤트 스토어
3. **애플리케이션 레이어**: 서비스 → 커맨드/쿼리 → 핸들러
4. **인터페이스 레이어**: API → 미들웨어 → 스키마

## 테스트 전략
- 도메인 로직: 100% 커버리지
- API 엔드포인트: 주요 시나리오
- 통합 테스트: 핵심 플로우
- 성능 테스트: 동시 로그인 100명

## 배포 전 체크리스트
- [ ] 모든 테스트 통과
- [ ] 보안 스캔 통과
- [ ] 성능 기준 만족
- [ ] 문서 업데이트 완료
```

---

## 🎉 Unit1 논리적 설계 완료!

**총 12단계 모든 설계가 완성되었습니다:**

1. ✅ 아키텍처 레이어 설계
2. ✅ 도메인 레이어 논리적 설계  
3. ✅ 애플리케이션 레이어 논리적 설계
4. ✅ 인프라스트럭처 레이어 논리적 설계
5. ✅ 인터페이스 레이어 논리적 설계
6. ✅ 데이터 모델링 및 영속성 설계
7. ✅ 보안 및 인증 설계
8. ✅ 이벤트 기반 아키텍처 설계
9. ✅ 성능 및 확장성 설계
10. ✅ 테스트 전략 설계
11. ✅ 배포 및 운영 설계
12. ✅ 문서화 및 검토

**이제 실제 구현을 시작할 수 있는 완전한 설계가 준비되었습니다!**

# 백업 스케줄링 (Lambda + EventBridge)
def lambda_backup_handler(event, context):
    """Lambda 백업 핸들러"""
    backup_manager = BackupManager(boto3.client('s3'), boto3.client('rds'))
    
    # 일일 백업 실행
    snapshot_id = asyncio.run(backup_manager.create_database_backup())
    
    # 오래된 백업 정리
    asyncio.run(backup_manager.cleanup_old_backups())
    
    return {
        'statusCode': 200,
        'body': json.dumps(f'Backup completed: {snapshot_id}')
    }
```

## 주요 변경사항 요약

1. **Refresh Token 제거**: 30일 토큰 삭제, 7일 제한 준수
2. **세션 연장 방식**: 웹앱 활동 시 자동으로 7일 재연장
3. **토큰 갱신**: 새 Access Token 발급으로 처리
4. **만료 처리**: 7일 비활성 시 완전 로그아웃
5. **모니터링**: 7일 제한 준수 여부 추적

이제 요구사항에 완전히 부합하는 보안 설계가 되었습니다!
