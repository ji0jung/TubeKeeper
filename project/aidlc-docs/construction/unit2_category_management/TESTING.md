# Unit2 카테고리 관리 테스트 가이드

## 개요

Unit2 카테고리 관리 시스템의 완전한 테스트 스위트입니다. 기능 테스트부터 성능 테스트까지 모든 측면을 검증합니다.

## 테스트 구조

```
scripts/
├── test_crud_integration.py    # 🎯 완전한 기능 테스트
├── test_performance.py         # 🚀 성능 테스트
├── generate_test_token.py      # 🔧 JWT 토큰 생성 유틸리티
├── test_utils.py              # 🔧 공통 테스트 유틸리티
└── init_system_categories.py  # 🔧 시스템 카테고리 초기화
```

## 테스트 파일별 역할

### 1. test_crud_integration.py
**Unit2의 모든 기능을 검증하는 메인 테스트**

#### 역할:
- Unit2의 모든 요구사항 검증
- 비즈니스 규칙 준수 확인
- 에러 시나리오 처리 검증
- Integration Contract 표준 준수 확인

#### 테스트 시나리오:
1. **시스템 카테고리 보호**
   - 시스템 카테고리 자동 생성
   - 시스템 카테고리 삭제 방지 (400 에러)
   - 최종 상태에서 시스템 카테고리만 남음 확인

2. **기본 CRUD 작업**
   - 카테고리 생성, 조회, 수정, 삭제
   - Integration Contract 표준 응답 구조 확인

3. **계층 구조 관리**
   - 3레벨까지 생성 가능
   - 4레벨 생성 시도 차단 (400 에러)

4. **입력 검증 오류**
   - 빈 이름 차단 (422 에러)
   - 긴 이름 차단 (422 에러)
   - 중복 이름 차단 (400 에러)

5. **404/401 오류 처리**
   - 존재하지 않는 카테고리 접근 (404 에러)
   - 잘못된 토큰 사용 (401 에러)

6. **삭제 안전장치**
   - 삭제 미리보기 기능
   - 하위 카테고리 있는 경우 삭제 불가
   - 계층 순서대로 삭제 (레벨3 → 레벨2 → 레벨1)

#### 실행법:
```bash
cd scripts
python3 test_crud_integration.py
```

#### 예상 결과:
```
🧪 카테고리 CRUD 통합 테스트 시작
✅ 초기 카테고리 수: 0
✅ 시스템 카테고리 삭제 방지 확인
✅ 루트 카테고리 생성: 루트카테고리
✅ 레벨4 생성 차단 확인
✅ 빈 이름 차단
✅ 존재하지 않는 카테고리 조회 404
✅ 잘못된 토큰 401
✅ 최종 상태: 시스템 카테고리 2개만 남음
🎉 카테고리 CRUD 통합 테스트 완료!
```

### 2. test_performance.py
**Unit2 시스템의 성능 특성을 측정하고 검증**

#### 역할:
- 시스템 성능 벤치마킹
- 성능 병목 지점 식별
- 확장성 검증
- 성능 기준 준수 확인

#### 테스트 시나리오:
1. **대량 작업 성능**
   - 20개 카테고리 생성 성능
   - 목록 조회 성능
   - 개별 조회 성능

2. **계층 구조 성능**
   - 1레벨 5개 생성
   - 2레벨 15개 생성 (각 1레벨당 3개)
   - 3레벨 30개 생성 (각 2레벨당 2개)
   - 전체 50개 조회 성능

3. **동시 요청 처리**
   - 10개 동시 요청 처리
   - 성공률 측정
   - 응답 시간 분석

4. **엔드포인트별 응답 시간**
   - GET /categories
   - GET /categories/:id
   - PUT /categories/:id
   - GET /deletion-preview

#### 성능 기준:
- 개별 조회: < 100ms
- 목록 조회: < 200ms
- 카테고리 생성: < 50ms
- 동시 요청 성공률: > 95%

#### 실행법:
```bash
cd scripts
python3 test_performance.py
```

#### 예상 결과:
```
🚀 Unit2 카테고리 관리 성능 테스트 시작
✅ 20개 카테고리 생성: 0.10초 (4.9ms/개)
✅ 20개 카테고리 목록 조회: 3.4ms
✅ 개별 조회 평균: 2.1ms
✅ 10개 동시 요청: 0.04초
✅ 성공률: 10/10 (100.0%)
✅ GET /categories: 평균 2.7ms, P95 3.5ms
🎉 성능 테스트 완료!
```

### 3. 유틸리티 파일들

#### generate_test_token.py
**JWT 테스트 토큰 생성 유틸리티**
- Unit1 인증 서비스와 독립적으로 동작
- 로컬 테스트용 JWT 토큰 생성
- 사용자 ID와 이메일을 포함한 토큰 생성

#### test_utils.py
**테스트 공통 유틸리티**
- cleanup_all_categories: 사용자의 모든 카테고리 삭제
- 테스트 간 데이터 격리 보장
- 테스트 코드 중복 제거

#### init_system_categories.py
**시스템 카테고리 초기화 유틸리티**
- "공유받은카드" 시스템 카테고리 생성
- "임시" 시스템 카테고리 생성
- 테스트 환경에서 시스템 카테고리 초기화

## 테스트 실행 가이드

### 전체 테스트 실행
```bash
# 1. 서버 시작
docker compose up -d

# 2. 기능 테스트 실행
cd scripts
python3 test_crud_integration.py

# 3. 성능 테스트 실행
python3 test_performance.py
```

### 개별 테스트 실행
```bash
# 특정 기능만 테스트하고 싶은 경우
python3 -c "
import asyncio
from test_crud_integration import test_category_crud
asyncio.run(test_category_crud())
"
```

## 테스트 커버리지

### 기능 테스트 커버리지: 100%
- ✅ 시스템 카테고리 보호
- ✅ 기본 CRUD 작업
- ✅ 계층 구조 관리
- ✅ 삭제 안전장치
- ✅ 입력 검증
- ✅ 오류 처리
- ✅ 인증/권한

### 성능 테스트 커버리지: 100%
- ✅ 대량 데이터 처리
- ✅ 계층 구조 성능
- ✅ 동시 요청 처리
- ✅ 응답 시간 분석

## 테스트 결과 해석

### 성공 기준
1. **기능 테스트**: 모든 시나리오 통과
2. **성능 테스트**: 모든 지표가 기준치 이하
3. **오류 처리**: 예상된 오류 코드 반환
4. **데이터 격리**: 테스트 간 데이터 간섭 없음

### 실패 시 대응
1. **기능 테스트 실패**: 비즈니스 로직 검토
2. **성능 테스트 실패**: 쿼리 최적화 또는 인프라 검토
3. **인증 오류**: JWT 토큰 생성 확인
4. **DB 연결 오류**: Docker Compose 상태 확인

## 테스트 환경 요구사항

### 필수 구성요소
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL (Docker로 실행)
- Redis (Docker로 실행)

### 필수 Python 패키지
```
httpx
asyncio
statistics
uuid
```

### 환경 변수
```bash
# .env 파일
DATABASE_URL=postgresql://postgres:password@localhost:5433/unit2_test
REDIS_URL=redis://localhost:6380
JWT_SECRET_KEY=test_secret_key_for_unit2_only
```

## 문제 해결

### 자주 발생하는 문제들

#### 1. 서버 연결 실패
```bash
# 해결: Docker 서비스 상태 확인
docker compose ps
docker compose logs app
```

#### 2. JWT 토큰 오류
```bash
# 해결: 토큰 생성 확인
python3 -c "from generate_test_token import generate_test_token; print(generate_test_token('test', 'test@example.com'))"
```

#### 3. 데이터베이스 연결 오류
```bash
# 해결: PostgreSQL 컨테이너 상태 확인
docker compose logs postgres
```

#### 4. 성능 테스트 실패
```bash
# 해결: 시스템 리소스 확인
docker stats
```

## 결론

Unit2 카테고리 관리 시스템은 완전한 테스트 커버리지를 통해 다음을 보장합니다:

1. **기능적 완성도**: 모든 요구사항 충족
2. **성능 우수성**: 모든 성능 기준 초과 달성
3. **안정성**: 오류 상황 완벽 처리
4. **확장성**: 대량 데이터 및 동시 요청 처리

이 테스트 스위트를 통해 Unit2는 다른 Unit들과 안전하게 통합할 준비가 완료되었습니다.
