# AIDLC Authentication & Profile Management

Unit1의 사용자 인증 및 프로필 관리 서비스입니다. 도메인 주도 설계(DDD)와 헥사고날 아키텍처를 기반으로 구현되었습니다.

## 🏗️ 아키텍처

- **헥사고날 아키텍처**: 도메인 중심의 계층 구조
- **이벤트 기반 시스템**: 도메인 이벤트를 통한 느슨한 결합
- **DDD 패턴**: 애그리게이트, 엔티티, 값 객체, 도메인 서비스

## 📁 프로젝트 구조

```
src/
├── domain/                 # 도메인 레이어 (핵심 비즈니스 로직)
│   ├── aggregates/        # 애그리게이트 (UserAggregate, SessionAggregate)
│   ├── entities/          # 엔티티 (User, Profile, Session, VerificationCode)
│   ├── value_objects/     # 값 객체 (Email, Gender, BirthYear, Language)
│   ├── events/            # 도메인 이벤트
│   ├── repositories/      # 리포지토리 인터페이스
│   ├── services/          # 도메인 서비스
│   ├── policies/          # 도메인 정책
│   └── exceptions/        # 도메인 예외
├── application/           # 애플리케이션 레이어 (유스케이스)
│   ├── services/          # 애플리케이션 서비스
│   ├── dtos/              # 데이터 전송 객체
│   ├── commands/          # 커맨드 객체
│   ├── queries/           # 쿼리 객체
│   ├── handlers/          # 이벤트 핸들러
│   └── interfaces/        # 외부 서비스 인터페이스
├── infrastructure/        # 인프라스트럭처 레이어 (기술적 구현)
│   ├── persistence/       # 데이터베이스 리포지토리
│   ├── external/          # 외부 서비스 (이메일, 캐시)
│   ├── config/            # 설정 관리
│   └── events/            # 이벤트 인프라
└── interfaces/           # 인터페이스 레이어 (API)
    └── api/              # FastAPI 컨트롤러, 스키마, 미들웨어
```

## 🚀 배포된 서비스

### Production Environment
- **Base URL**: `http://staging-aidlc-alb-809271486.us-east-1.elb.amazonaws.com`
- **Health Check**: `/health`
- **API 문서**: `/docs`

### 주요 API 엔드포인트
```bash
# 회원가입
POST /api/auth/register
POST /api/auth/verify-registration

# 로그인
POST /api/auth/login  
POST /api/auth/verify-login

# 프로필 관리
GET /api/profile
PUT /api/profile

# 세션 관리
POST /api/auth/logout
POST /api/auth/refresh-session
```

## 🧪 완료된 기능

### ✅ 인증 시스템
- **이메일 기반 인증**: 6자리 인증 코드 (15분 유효)
- **JWT 토큰**: 7일 유효기간, 자동 연장
- **세션 관리**: 디바이스당 최대 3개 세션

### ✅ 프로필 관리
- **사용자 정보**: 이메일, 성별, 출생년도, 언어 설정
- **프로필 업데이트**: updated_at 자동 갱신
- **데이터 검증**: 도메인 값 객체 기반

### ✅ 인프라스트럭처
- **데이터베이스**: PostgreSQL (RDS)
- **캐시**: Redis (ElastiCache)
- **컨테이너**: ECS Fargate
- **로드밸런서**: Application Load Balancer

## 🔧 기술 스택

- **언어**: Python 3.11
- **프레임워크**: FastAPI
- **데이터베이스**: PostgreSQL
- **캐시**: Redis
- **인프라**: AWS (ECS, RDS, ElastiCache, ALB)
- **컨테이너**: Docker

## 🧪 API 테스트

모든 API가 프로덕션 환경에서 테스트 완료되었습니다:

```bash
# 헬스 체크
curl http://staging-aidlc-alb-809271486.us-east-1.elb.amazonaws.com/health

# 회원가입 플로우
curl -X POST "http://staging-aidlc-alb-809271486.us-east-1.elb.amazonaws.com/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "gender": "male", "birth_year": 1990}'
```

## 📊 성능 지표

- **응답 시간**: Health Check ~50ms, API ~200-300ms
- **리소스**: CPU 256, Memory 512MB
- **가용성**: 99.9% (ALB + ECS Fargate)

## 📝 문서

- **API 명세**: `API_SPECIFICATION.md`
- **배포 가이드**: `DEPLOYMENT_GUIDE.md`
- **트러블슈팅**: `TROUBLESHOOTING.md`
- **시퀀스 다이어그램**: `sequence_diagrams.md`
- **구현 계획**: `implementation_plan_unit1_authentication.md`

## 🔗 관련 리소스

- **공유 리소스 가이드**: `/unit1_shared_resources.md`
- **완료 요약**: `/unit1_completion_summary.md`
- **Integration Contract**: `/aidlc-docs/inception/units/integration_contract.md`
