# Unit3 카드 생성 시스템

YouTube URL을 입력받아 카드를 생성하고 관리하는 시스템입니다.

## 🎯 주요 기능

- ✅ YouTube URL 기반 카드 생성
- ✅ 비동기 메타데이터 추출 및 완성
- ✅ 썸네일 압축 및 S3 업로드
- ✅ 메모 및 태그 관리
- ✅ 즐겨찾기 기능
- ✅ **태그 사용 빈도 계산** (최신 완성)
- ✅ 카드 목록 조회 (페이지네이션)
- ✅ 카드 상세 조회 및 수정/삭제

## 🏗️ 아키텍처

```
src/
├── unit3_card_creation/
│   ├── domain/                 # 도메인 로직
│   ├── application/           # 애플리케이션 서비스
│   ├── infrastructure/        # 인프라 구현
│   └── presentation/          # API 및 WebSocket
├── tests/                     # 정식 테스트
└── test_*.py                  # 기능 검증 테스트
```

## 🚀 빠른 시작

### 1. 환경 설정
```bash
cd src
cp .env.example .env
```

**중요**: `.env` 파일에서 다음 값들을 설정하세요:
```bash
# 필수: YouTube API 키
YOUTUBE_API_KEY=your_actual_youtube_api_key

# 선택사항: AWS S3 (썸네일 업로드용)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=your_s3_bucket_name
```

### 2. Docker 실행
```bash
docker compose up -d
```

### 3. 환경 확인
```bash
python test_docker.py
```

## 📡 API 엔드포인트

### 카드 관리
- `POST /api/cards/` - 카드 생성
- `GET /api/cards/` - 카드 목록 조회
- `GET /api/cards/{card_id}` - 카드 상세 조회
- `PUT /api/cards/{card_id}` - 카드 수정
- `DELETE /api/cards/{card_id}` - 카드 삭제
- `POST /api/cards/{card_id}/favorite` - 즐겨찾기 토글

### 태그 관리 ⭐
- `GET /api/tags/` - 사용자 태그 목록 (사용 빈도순)

### 시스템
- `GET /health` - 헬스체크

## 🧪 테스트

### 테스트 실행
```bash
# 전체 환경 검증
python test_docker.py

# 태그 기능 테스트 (최신 완성 기능)
python test_tag_frequency.py

# 통합 테스트
python test_integration_complete.py

# 정식 테스트 스위트
pytest tests/
```

### 테스트 문서
자세한 테스트 가이드는 [TESTING.md](./TESTING.md)를 참조하세요.

## 🔧 기술 스택

- **Backend**: FastAPI, Python 3.11+
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **Storage**: AWS S3
- **External API**: YouTube Data API v3
- **Container**: Docker, Docker Compose

## 📊 완성도

- **카드 CRUD**: 100% ✅
- **메타데이터 처리**: 100% ✅
- **썸네일 관리**: 100% ✅
- **태그 관리**: 100% ✅
- **즐겨찾기**: 100% ✅
- **전체 시스템**: 99% ✅

## 🎯 다음 단계

- [ ] Unit2 카테고리 시스템 연동
- [ ] 검색 기능 고도화
- [ ] 성능 최적화

---

**마지막 업데이트**: 2025-10-26  
**핵심 완성 기능**: 태그 사용 빈도 계산 🏷️
