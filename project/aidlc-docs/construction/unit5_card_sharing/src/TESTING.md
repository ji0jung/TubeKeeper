# Unit5 카드 공유 시스템 테스트 가이드

## 📋 개요

Unit5 카드 공유 시스템의 테스트 구조와 실행 방법을 설명합니다. 모든 테스트는 Unit3과 동일한 JWT 인증 방식을 사용하며, timezone-safe한 naive datetime을 적용합니다.

## 🏗️ 테스트 구조

```
tests/
├── test_config.py              # 테스트 설정 및 공통 유틸리티
├── unit/
│   └── test_domain.py         # 도메인 레이어 단위 테스트
└── integration/
    └── test_share_api.py      # API 통합 테스트

test_docker.py                 # Docker 환경 통합 테스트
docker_test.sh                 # Docker 테스트 자동화 스크립트
pytest.ini                    # pytest 설정
```

## 📝 테스트 파일별 상세 설명

### 1. `tests/test_config.py` - 테스트 설정 및 공통 유틸리티

**역할**: 모든 테스트에서 사용되는 공통 설정과 유틸리티 제공

**주요 기능**:
- JWT 토큰 생성 (Unit3 방식과 동일)
- 테스트 환경 설정 (포트 8005 사용)
- 데이터베이스 정리 함수
- 인증 헤더 생성

**사용 예시**:
```python
from tests.test_config import TestConfig

# JWT 토큰 생성
token, user_id = TestConfig.generate_test_token()
headers = TestConfig.get_auth_headers(token)

# 테스트 데이터 정리
await TestConfig.cleanup_test_data()
```

### 2. `tests/unit/test_domain.py` - 도메인 레이어 단위 테스트

**역할**: 비즈니스 로직의 정확성과 도메인 규칙 준수 검증

**테스트 대상**:
- **값 객체**: ShareToken, ExpirationDate, ShareUrl
- **엔티티**: ShareLink
- **애그리게이트**: ShareLinkAggregate

**테스트 범위**:
- 객체 생성 및 유효성 검증
- 비즈니스 규칙 준수
- 도메인 이벤트 발생
- 만료 처리 로직

**실행 방법**:
```bash
pytest tests/unit/test_domain.py -v
```

### 3. `tests/integration/test_share_api.py` - API 통합 테스트

**역할**: REST API 엔드포인트들의 통합 동작 검증

**테스트 대상 API**:
- `POST /api/cards/{card_id}/share` - 공유 링크 생성
- `GET /api/shared/{share_token}` - 공유 카드 조회
- `POST /api/shared/{share_token}/save` - 공유 카드 저장

**테스트 시나리오**:
- 정상 플로우 (생성 → 조회 → 저장)
- 인증 및 권한 검증
- 오류 처리 (만료, 존재하지 않는 링크 등)
- 크롤러 감지 및 HTML 응답
- 표준 응답 형식 검증

**실행 방법**:
```bash
python tests/integration/test_share_api.py
```

### 4. `test_docker.py` - Docker 환경 통합 테스트

**역할**: 실제 운영 환경과 유사한 조건에서 전체 시스템 통합 테스트

**테스트 환경**:
- PostgreSQL 데이터베이스 (포트 5435)
- Redis 캐시 서버 (포트 6381)
- FastAPI 애플리케이션 (포트 8005)

**테스트 기능**:
- 서비스 헬스체크 및 준비 상태 확인
- 전체 API 플로우 테스트
- 오류 시나리오 처리 검증
- 크롤러 HTML 응답 테스트
- 자동 데이터 정리 (성공 시에만)

**데이터 관리**:
- **테스트 시작 전**: 기존 데이터 정리
- **테스트 성공 시**: 생성된 데이터 자동 삭제
- **테스트 실패 시**: 디버깅을 위해 데이터 보존

**실행 방법**:
```bash
python test_docker.py
# 또는
./docker_test.sh
```

## 🚀 테스트 실행 방법

### 1. 단위 테스트만 실행
```bash
pytest tests/unit/ -v
```

### 2. 통합 테스트만 실행
```bash
python tests/integration/test_share_api.py
```

### 3. Docker 환경 전체 테스트 (권장)
```bash
./docker_test.sh
```

### 4. 개별 테스트 파일 실행
```bash
# 도메인 테스트
pytest tests/unit/test_domain.py::TestValueObjects::test_share_token_creation -v

# API 테스트
python tests/integration/test_share_api.py

# Docker 테스트
python test_docker.py
```

## 🔧 테스트 환경 설정

### 필수 의존성
```bash
pip install -r requirements.txt
```

### 환경 변수
```bash
# .env 파일 또는 환경 변수 설정
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5435/unit5_sharing
REDIS_URL=redis://localhost:6381/0
JWT_SECRET_KEY=unit5-secret-key
SHARE_LINK_BASE_URL=http://localhost:8005
```

### Docker 환경
```bash
# Docker 컨테이너 시작
docker compose up -d

# 테스트 실행
python test_docker.py

# 컨테이너 정리
docker compose down
```

## 📊 테스트 커버리지

| 레이어 | 테스트 파일 | 커버리지 |
|--------|-------------|----------|
| 도메인 | `test_domain.py` | 값 객체, 엔티티, 애그리게이트 |
| 애플리케이션 | `test_share_api.py` | 유스케이스, 서비스 |
| 인프라 | `test_docker.py` | 데이터베이스, 캐시, API |
| 프레젠테이션 | `test_share_api.py` | 컨트롤러, 미들웨어 |

## 🎯 테스트 시나리오

### 정상 플로우
1. **공유 링크 생성**: JWT 인증 → 카드 ID 검증 → 링크 생성
2. **공유 카드 조회**: 토큰 검증 → 만료 확인 → 카드 정보 반환
3. **공유 카드 저장**: JWT 인증 → 중복 확인 → 카드 저장

### 오류 시나리오
- **인증 오류**: JWT 토큰 없음/잘못됨
- **권한 오류**: 다른 사용자의 카드 접근
- **데이터 오류**: 존재하지 않는 카드/링크
- **만료 오류**: 만료된 공유 링크 접근
- **형식 오류**: 잘못된 UUID 형식

### 크롤러 테스트
- **User-Agent 감지**: Facebook, Twitter, LinkedIn 등
- **HTML 응답**: Open Graph 메타데이터 포함
- **JSON 응답**: 일반 사용자 요청

## 🔍 디버깅 가이드

### 테스트 실패 시 확인사항
1. **서비스 상태**: `curl http://localhost:8005/health`
2. **데이터베이스 연결**: PostgreSQL 포트 5435 확인
3. **Redis 연결**: Redis 포트 6381 확인
4. **JWT 토큰**: 만료 시간 및 서명 확인

### 로그 확인
```bash
# Docker 로그 확인
docker compose logs app

# 데이터베이스 로그
docker compose logs db

# Redis 로그
docker compose logs redis
```

### 데이터 확인
```bash
# 데이터베이스 접속
psql -h localhost -p 5435 -U postgres -d unit5_sharing

# 테이블 확인
\dt
SELECT * FROM share_links;
SELECT * FROM share_link_access_logs;
```

## 📈 성능 테스트

현재는 기능 테스트에 집중하고 있으며, 향후 다음 성능 테스트를 추가할 예정입니다:
- 동시 접속 테스트
- 대용량 데이터 처리 테스트
- 캐시 성능 테스트
- API 응답 시간 측정

## 🔄 CI/CD 통합

GitHub Actions 또는 다른 CI/CD 파이프라인에서 사용할 수 있는 테스트 명령어:

```yaml
# GitHub Actions 예시
- name: Run Unit Tests
  run: pytest tests/unit/ -v

- name: Run Integration Tests
  run: python tests/integration/test_share_api.py

- name: Run Docker Tests
  run: ./docker_test.sh
```

## 📚 참고 자료

- [Unit3 테스트 구조](../unit3_card_creation/src/tests/)
- [FastAPI 테스트 가이드](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest 문서](https://docs.pytest.org/)
- [Docker Compose 테스트](https://docs.docker.com/compose/)
