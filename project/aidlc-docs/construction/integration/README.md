# Unit2 + Unit3 통합 테스트 환경

## 🚀 빠른 시작

### 1. 환경 변수 설정
```bash
# YouTube API 키를 로컬 환경변수로 설정
export YOUTUBE_API_KEY=your_actual_youtube_api_key_here

# 또는 .env.local 파일 생성 (권장)
cp .env.example .env.local
# .env.local 파일에서 YOUTUBE_API_KEY 값 설정
```

### 2. 서비스 시작
```bash
cd integration
docker compose up -d
```

### 3. 서비스 확인
```bash
# Unit2 카테고리 관리
curl http://localhost:8012/health

# Unit3 카드 생성
curl http://localhost:8013/health

# API Gateway
curl http://localhost:8080
```

## 📊 포트 구성

| 서비스 | 포트 | 설명 |
|--------|------|------|
| Unit2 | 8012 | 카테고리 관리 API |
| Unit3 | 8013 | 카드 생성 API |
| Gateway | 8080 | 통합 API 게이트웨이 |
| PostgreSQL | 5436 | 공유 데이터베이스 |
| Redis | 6382 | 공유 캐시 |
| LocalStack | 4568 | AWS 서비스 모킹 |

## 🔧 환경 변수

### 필수 환경 변수
- `YOUTUBE_API_KEY`: YouTube Data API v3 키

### 자동 설정되는 변수
- 데이터베이스 연결 정보
- Redis 연결 정보  
- JWT 설정
- AWS LocalStack 설정

## 🧪 테스트

### 통합 테스트 실행
```bash
cd tests
python integration_test.py
```

## 🛠️ 문제 해결

### 환경 변수 확인
```bash
echo $YOUTUBE_API_KEY
```

### 서비스 로그 확인
```bash
docker compose logs unit2
docker compose logs unit3
```

### 서비스 재시작
```bash
docker compose restart unit2 unit3
```
