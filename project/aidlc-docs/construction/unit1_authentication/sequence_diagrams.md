# Unit1 Authentication & Profile Management - API 시퀀스 다이어그램

## 1. 회원가입 요청 API (POST /api/auth/register)

```mermaid
sequenceDiagram
    participant User as 사용자
    participant API as FastAPI Controller
    participant AppService as UserRegistrationAppService
    participant UserRepo as UserRepository
    participant EmailService as EmailVerificationService
    participant VerificationRepo as VerificationCodeRepository
    participant SES as AWS SES
    participant Cache as Redis Cache
    participant EventPub as EventPublisher

    User->>API: POST /api/auth/register<br/>{email, gender, birthYear}
    
    API->>AppService: request_registration(command)
    
    Note over AppService: 1. 이메일 중복 확인
    AppService->>UserRepo: exists_by_email(email)
    UserRepo-->>AppService: false
    
    Note over AppService: 2. 인증 코드 생성
    AppService->>EmailService: generate_verification_code(email, REGISTRATION)
    EmailService->>VerificationRepo: save(verification_code)
    VerificationRepo-->>EmailService: saved
    
    Note over AppService: 3. 이메일 발송
    EmailService->>SES: send_verification_email(email, code)
    SES-->>EmailService: sent
    
    Note over AppService: 4. 캐시 저장 (15분 TTL)
    EmailService->>Cache: cache_verification_code(email, code, 900s)
    Cache-->>EmailService: cached
    
    Note over AppService: 5. 이벤트 발행
    AppService->>EventPub: publish(UserRegistrationRequested)
    EventPub-->>AppService: published
    
    AppService-->>API: RequestRegistrationResult(success=true)
    API-->>User: 200 OK<br/>{success: true, message: "Verification code sent"}
```

## 2. 회원가입 완료 API (POST /api/auth/register/verify)

```mermaid
sequenceDiagram
    participant User as 사용자
    participant API as FastAPI Controller
    participant AppService as UserRegistrationAppService
    participant AuthService as AuthenticationService
    participant VerificationRepo as VerificationCodeRepository
    participant UserRepo as UserRepository
    participant Cache as Redis Cache
    participant EventPub as EventPublisher
    participant DB as PostgreSQL

    User->>API: POST /api/auth/register/verify<br/>{email, verificationCode}
    
    API->>AppService: complete_registration(command)
    
    Note over AppService: 1. 인증 코드 검증
    AppService->>AuthService: validate_verification_code(email, code, REGISTRATION)
    AuthService->>VerificationRepo: find_valid_code(email, REGISTRATION)
    VerificationRepo-->>AuthService: verification_code
    AuthService->>AuthService: verify_code(input_code)
    AuthService-->>AppService: valid=true
    
    Note over AppService: 2. 사용자 생성 (트랜잭션)
    AppService->>DB: BEGIN TRANSACTION
    AppService->>UserRepo: save(user_aggregate)
    Note over UserRepo: User + Profile 동시 생성
    UserRepo-->>AppService: saved
    AppService->>DB: COMMIT
    
    Note over AppService: 3. 인증 코드 사용 처리
    AppService->>VerificationRepo: mark_as_used(code_id)
    VerificationRepo-->>AppService: marked
    
    Note over AppService: 4. 캐시 정리
    AppService->>Cache: invalidate_verification_code(email, REGISTRATION)
    Cache-->>AppService: invalidated
    
    Note over AppService: 5. 이벤트 발행
    AppService->>EventPub: publish(UserRegistered)
    EventPub-->>AppService: published
    
    AppService-->>API: CompleteRegistrationResult(success=true, user)
    API-->>User: 200 OK<br/>{success: true, user: {...}}
```

## 3. 로그인 요청 API (POST /api/auth/login)

```mermaid
sequenceDiagram
    participant User as 사용자
    participant API as FastAPI Controller
    participant AppService as AuthenticationAppService
    participant UserRepo as UserRepository
    participant EmailService as EmailVerificationService
    participant SES as AWS SES
    participant Cache as Redis Cache
    participant SecurityLogger as SecurityLogger

    User->>API: POST /api/auth/login<br/>{email, deviceInfo}
    
    API->>AppService: request_login(command)
    
    Note over AppService: 1. 사용자 존재 확인
    AppService->>UserRepo: find_by_email(email)
    UserRepo-->>AppService: user_aggregate
    AppService->>AppService: validate_user_can_login()
    
    Note over AppService: 2. 인증 코드 생성
    AppService->>EmailService: generate_verification_code(email, LOGIN)
    EmailService->>Cache: cache_verification_code(email, LOGIN, code, 900s)
    Cache-->>EmailService: cached
    
    Note over AppService: 3. 이메일 발송
    EmailService->>SES: send_login_verification_email(email, code)
    SES-->>EmailService: sent
    
    Note over AppService: 4. 보안 로깅
    AppService->>SecurityLogger: log_event(LOGIN_INITIATED, {email, deviceInfo})
    SecurityLogger-->>AppService: logged
    
    AppService-->>API: RequestLoginResult(success=true)
    API-->>User: 200 OK<br/>{success: true, message: "Verification code sent"}
```

## 4. 로그인 완료 API (POST /api/auth/login/verify)

```mermaid
sequenceDiagram
    participant User as 사용자
    participant API as FastAPI Controller
    participant AppService as AuthenticationAppService
    participant AuthService as AuthenticationService
    participant SessionService as SessionManagementService
    participant UserRepo as UserRepository
    participant SessionRepo as SessionRepository
    participant Cache as Redis Cache
    participant JWTManager as JWTManager
    participant DistributedLock as DistributedLock

    User->>API: POST /api/auth/login/verify<br/>{email, code, deviceInfo}
    
    API->>AppService: complete_login(command)
    
    Note over AppService: 1. 인증 코드 검증
    AppService->>AuthService: validate_verification_code(email, code, LOGIN)
    AuthService-->>AppService: valid=true
    
    Note over AppService: 2. 사용자 조회
    AppService->>UserRepo: find_by_email(email)
    UserRepo-->>AppService: user_aggregate
    
    Note over AppService: 3. 세션 생성 (동시 로그인 제한)
    AppService->>SessionService: create_session_with_limit(user_id, device_info)
    
    Note over SessionService: 분산 락 획득
    SessionService->>DistributedLock: acquire_lock(session_limit:user_id)
    DistributedLock-->>SessionService: acquired
    
    Note over SessionService: 활성 세션 확인
    SessionService->>SessionRepo: find_active_sessions_by_user_id(user_id)
    SessionRepo-->>SessionService: active_sessions[2개]
    
    Note over SessionService: 동일 디바이스 확인
    SessionService->>SessionService: check_same_device(device_info)
    
    Note over SessionService: 새 세션 생성 (3개 제한 내)
    SessionService->>SessionRepo: save(new_session)
    SessionRepo-->>SessionService: saved
    
    SessionService->>DistributedLock: release_lock(session_limit:user_id)
    DistributedLock-->>SessionService: released
    
    Note over AppService: 4. JWT 토큰 생성
    SessionService->>JWTManager: create_access_token(user_id, session_id)
    JWTManager-->>SessionService: jwt_token
    
    Note over AppService: 5. 세션 캐싱 (7일 TTL)
    SessionService->>Cache: cache_session(session_id, session_data, 604800s)
    Cache-->>SessionService: cached
    
    Note over AppService: 6. 사용자 활동 시간 업데이트
    AppService->>UserRepo: update_last_activity(user_id)
    UserRepo-->>AppService: updated
    
    SessionService-->>AppService: session_data{token, expires_at}
    AppService-->>API: LoginResult(success=true, token, user)
    API-->>User: 200 OK<br/>{success: true, access_token: "jwt...", user: {...}}
```

## 5. 프로필 조회 API (GET /api/profile)

```mermaid
sequenceDiagram
    participant User as 사용자
    participant API as FastAPI Controller
    participant AuthMiddleware as AuthenticationMiddleware
    participant JWTManager as JWTManager
    participant Cache as Redis Cache
    participant AppService as ProfileManagementAppService
    participant UserRepo as UserRepository

    User->>API: GET /api/profile<br/>Authorization: Bearer jwt_token
    
    Note over API: 인증 미들웨어
    API->>AuthMiddleware: authenticate_request(jwt_token)
    AuthMiddleware->>JWTManager: verify_token(jwt_token)
    JWTManager-->>AuthMiddleware: payload{user_id, session_id}
    
    Note over AuthMiddleware: 세션 유효성 확인
    AuthMiddleware->>Cache: get_session(session_id)
    Cache-->>AuthMiddleware: session_data
    AuthMiddleware-->>API: current_user{user_id, session_id}
    
    API->>AppService: get_profile(GetProfileQuery{user_id})
    
    Note over AppService: 캐시 확인
    AppService->>Cache: get_user_info(user_id)
    Cache-->>AppService: null (cache miss)
    
    Note over AppService: 데이터베이스 조회
    AppService->>UserRepo: find_by_id(user_id)
    UserRepo-->>AppService: user_aggregate
    
    Note over AppService: 캐시 저장 (1시간 TTL)
    AppService->>Cache: cache_user_info(user_id, profile_data, 3600s)
    Cache-->>AppService: cached
    
    AppService-->>API: ProfileDto{profile_id, gender, birth_year, language}
    API-->>User: 200 OK<br/>{profile: {...}}
```

## 6. 프로필 수정 API (PUT /api/profile)

```mermaid
sequenceDiagram
    participant User as 사용자
    participant API as FastAPI Controller
    participant AuthMiddleware as AuthenticationMiddleware
    participant AppService as ProfileManagementAppService
    participant UserRepo as UserRepository
    participant Cache as Redis Cache
    participant EventPub as EventPublisher

    User->>API: PUT /api/profile<br/>{gender, birthYear}<br/>Authorization: Bearer jwt_token
    
    API->>AuthMiddleware: authenticate_request(jwt_token)
    AuthMiddleware-->>API: current_user{user_id}
    
    API->>AppService: update_profile(UpdateProfileCommand{user_id, gender, birthYear})
    
    Note over AppService: 사용자 조회
    AppService->>UserRepo: find_by_id(user_id)
    UserRepo-->>AppService: user_aggregate
    
    Note over AppService: 프로필 업데이트
    AppService->>AppService: user_aggregate.update_profile(gender, birthYear)
    
    Note over AppService: 저장 (낙관적 락)
    AppService->>UserRepo: save(user_aggregate)
    UserRepo-->>AppService: saved
    
    Note over AppService: 캐시 무효화
    AppService->>Cache: invalidate_user_cache(user_id)
    Cache-->>AppService: invalidated
    
    Note over AppService: 이벤트 발행
    AppService->>EventPub: publish(ProfileUpdated)
    EventPub-->>AppService: published
    
    AppService-->>API: UpdateProfileResult(success=true, profile)
    API-->>User: 200 OK<br/>{success: true, profile: {...}}
```

## 7. 로그아웃 API (POST /api/auth/logout)

```mermaid
sequenceDiagram
    participant User as 사용자
    participant API as FastAPI Controller
    participant AuthMiddleware as AuthenticationMiddleware
    participant AppService as AuthenticationAppService
    participant SessionRepo as SessionRepository
    participant Cache as Redis Cache
    participant EventPub as EventPublisher

    User->>API: POST /api/auth/logout<br/>Authorization: Bearer jwt_token
    
    API->>AuthMiddleware: authenticate_request(jwt_token)
    AuthMiddleware-->>API: current_user{user_id, session_id}
    
    API->>AppService: logout(LogoutCommand{session_id})
    
    Note over AppService: 세션 만료 처리
    AppService->>SessionRepo: find_by_id(session_id)
    SessionRepo-->>AppService: session_aggregate
    AppService->>AppService: session_aggregate.expire()
    AppService->>SessionRepo: save(session_aggregate)
    SessionRepo-->>AppService: saved
    
    Note over AppService: 캐시 무효화
    AppService->>Cache: invalidate_session(session_id)
    Cache-->>AppService: invalidated
    
    Note over AppService: 이벤트 발행
    AppService->>EventPub: publish(UserLoggedOut)
    EventPub-->>AppService: published
    
    AppService-->>API: LogoutResult(success=true)
    API-->>User: 200 OK<br/>{success: true}
```

## 8. 세션 자동 연장 (미들웨어)

```mermaid
sequenceDiagram
    participant User as 사용자
    participant API as FastAPI Controller
    participant ExtensionMiddleware as SessionExtensionMiddleware
    participant SessionService as SessionSecurityService
    participant SessionRepo as SessionRepository
    participant Cache as Redis Cache
    participant JWTManager as JWTManager

    User->>API: Any API Request<br/>Authorization: Bearer jwt_token
    
    Note over API: 요청 처리 후
    API->>ExtensionMiddleware: process_response(request, response)
    
    Note over ExtensionMiddleware: 인증된 요청인지 확인
    ExtensionMiddleware->>ExtensionMiddleware: check_authenticated_request()
    
    Note over ExtensionMiddleware: 세션 연장
    ExtensionMiddleware->>SessionService: extend_session_on_activity(session_id)
    
    SessionService->>SessionRepo: find_by_id(session_id)
    SessionRepo-->>SessionService: session_aggregate
    
    Note over SessionService: 세션 연장 (7일로 재설정)
    SessionService->>SessionService: session_aggregate.extend()
    SessionService->>SessionRepo: save(session_aggregate)
    SessionRepo-->>SessionService: saved
    
    Note over SessionService: 새 JWT 토큰 생성
    SessionService->>JWTManager: create_access_token(user_id, session_id)
    JWTManager-->>SessionService: new_jwt_token
    
    Note over SessionService: 캐시 업데이트 (7일 TTL)
    SessionService->>Cache: cache_session(session_id, session_data, 604800s)
    Cache-->>SessionService: cached
    
    SessionService-->>ExtensionMiddleware: {access_token, expires_at}
    
    Note over ExtensionMiddleware: 응답 헤더에 새 토큰 추가
    ExtensionMiddleware->>ExtensionMiddleware: add_response_headers(new_token)
    
    ExtensionMiddleware-->>API: response_with_new_token
    API-->>User: Response + Headers<br/>X-New-Token: new_jwt_token<br/>X-Token-Expires: expires_at
```

이 시퀀스 다이어그램들은 Unit1의 핵심 API 플로우를 보여주며, 각 단계에서의 상호작용, 캐싱 전략, 보안 검증, 이벤트 발행 등을 상세히 나타냅니다.
