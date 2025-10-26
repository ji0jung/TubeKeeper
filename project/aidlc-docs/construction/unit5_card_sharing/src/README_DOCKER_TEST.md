# Unit5 Docker 테스트 가이드

## 🐳 Docker 테스트 실행

### 자동 실행 (권장)
```bash
./docker_test.sh
```

### 수동 실행
```bash
# 1. Docker 컨테이너 시작
docker-compose up -d

# 2. 테스트 실행
python test_docker.py

# 3. 컨테이너 정리
docker-compose down
```

## 📋 테스트 내용

### 1. 데이터 정리
- **시작 전**: 기존 데이터베이스 및 Redis 데이터 정리
- **종료 후**: 테스트 성공 시 생성된 데이터 자동 정리
- **실패 시**: 디버깅을 위해 데이터 보존

### 2. 테스트 케이스
- ✅ 헬스체크
- ✅ 공유 링크 생성/조회/저장 플로우
- ✅ 인증 오류 처리
- ✅ 크롤러 HTML 응답
- ✅ 표준 응답 형식 검증

### 3. 포트 설정
- **애플리케이션**: 8005
- **PostgreSQL**: 5435
- **Redis**: 6381

## 🔧 트러블슈팅

### 포트 충돌 시
```bash
# 포트 사용 확인
lsof -i :8005
lsof -i :5435
lsof -i :6381

# 기존 컨테이너 정리
docker-compose down
docker system prune -f
```

### 데이터베이스 연결 실패 시
```bash
# PostgreSQL 컨테이너 로그 확인
docker-compose logs db

# 수동 연결 테스트
psql -h localhost -p 5435 -U postgres -d unit5_sharing
```

## 📊 테스트 결과

### 성공 시
```
🎉 모든 Docker 테스트 통과!
🧹 테스트 성공 - 생성된 데이터 정리 중...
✅ Unit5 Docker 테스트 성공!
```

### 실패 시
```
❌ Docker 테스트 실패: [오류 메시지]
⚠️ 테스트 실패 - 디버깅을 위해 데이터 보존
생성된 토큰들: [토큰 목록]
```
