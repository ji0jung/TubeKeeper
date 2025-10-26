# Unit3 카드 생성 시스템 테스트 문서

## 📋 개요

Unit3 카드 생성 시스템의 모든 기능을 검증하기 위한 테스트 스위트입니다. 인프라 검증부터 개별 기능 테스트, 통합 테스트까지 포괄적으로 다룹니다.

## 🏗️ 테스트 구조

```
src/
├── test_*.py                    # 개발 중 기능 검증 테스트
└── tests/                       # 정식 테스트 스위트
    ├── unit/                    # 단위 테스트
    │   ├── domain/             # 도메인 로직 테스트
    │   └── application/        # 애플리케이션 서비스 테스트
    └── integration/            # 통합 테스트
```

## 🔧 인프라 및 환경 테스트

### `test_docker.py`
**Docker 환경 테스트**

Docker Compose로 구성된 개발 환경의 각 서비스가 정상 동작하는지 검증합니다.

- ✅ PostgreSQL 데이터베이스 연결 테스트
- ✅ Redis 연결 테스트  
- ✅ FastAPI 애플리케이션 헬스체크
- ✅ 전체 인프라 상태 확인

```bash
python test_docker.py
```

### `test_cleanup.py`
**테스트 데이터 정리 유틸리티**

테스트 실행 후 남은 데이터를 정리하는 유틸리티입니다.

```bash
python test_cleanup.py
```

## 🎯 기능별 단위 테스트

### `test_card_creation_with_memo_tags.py`
**메모 및 태그 포함 카드 생성 테스트**

카드 생성 시 메모와 태그가 올바르게 저장되고 조회되는지 검증합니다.

- ✅ 메모 및 태그 포함 카드 생성
- ✅ 태그 유효성 검증 (길이, 개수 제한)
- ✅ 저장된 데이터 정확성 확인
- ✅ 한글 태그 및 특수문자 처리

```bash
python test_card_creation_with_memo_tags.py
```

### `test_favorites_and_thumbnail.py`
**즐겨찾기 및 썸네일 기능 테스트**

카드의 즐겨찾기 토글 기능과 썸네일 처리 기능을 검증합니다.

- ✅ 즐겨찾기 추가/제거 기능
- ✅ 썸네일 URL 생성 및 압축
- ✅ S3 업로드 및 URL 반환
- ✅ 즐겨찾기 상태 변경 추적

```bash
python test_favorites_and_thumbnail.py
```

### `test_async_metadata_completion.py`
**비동기 메타데이터 완성 테스트**

YouTube API를 통한 비동기 메타데이터 처리 과정을 검증합니다.

- ✅ 비동기 메타데이터 추출 및 완성
- ✅ 백그라운드 작업 처리
- ✅ 메타데이터 업데이트 상태 추적
- ✅ 실패 시 재시도 로직

```bash
python test_async_metadata_completion.py
```

### `test_s3_thumbnail_compression.py`
**S3 썸네일 압축 테스트**

YouTube 썸네일을 S3에 업로드하고 압축하는 기능을 검증합니다.

- ✅ YouTube 썸네일 다운로드
- ✅ 이미지 압축 및 최적화
- ✅ S3 업로드 및 URL 생성
- ✅ 압축률 및 품질 검증

```bash
python test_s3_thumbnail_compression.py
```

### `test_tag_frequency.py` ⭐
**태그 사용 빈도 테스트**

사용자가 여러 카드를 생성했을 때 태그 API가 올바른 빈도를 반환하는지 검증합니다.

- ✅ 4개 카드 생성 (서로 다른 태그 조합)
- ✅ 태그 사용 빈도 계산 검증
- ✅ 빈도순 정렬 검증
- ✅ 테스트 데이터 자동 정리

```bash
python test_tag_frequency.py
```

**예상 결과:**
```
📊 태그 사용 빈도 (빈도순):
   ✅ API: 3회 (예상: 3회)
   ✅ Python: 3회 (예상: 3회)
   ✅ FastAPI: 2회 (예상: 2회)
   ✅ Backend: 2회 (예상: 2회)
   ✅ Database: 1회 (예상: 1회)
   ✅ PostgreSQL: 1회 (예상: 1회)
```

### `test_multiple_cards.py`
**다중 카드 처리 테스트**

여러 카드를 동시에 처리할 때의 시스템 동작을 검증합니다.

```bash
python test_multiple_cards.py
```

## 🔄 통합 테스트

### `test_integration_complete.py`
**전체 시스템 통합 테스트**

Unit3 카드 생성 시스템의 모든 기능을 종합적으로 테스트합니다.

- ✅ 시스템 헬스체크 (DB, Redis, API)
- ✅ 카드 CRUD 전체 플로우 검증
- ✅ 메타데이터 처리 및 썸네일 생성
- ✅ 즐겨찾기, 태그, 메모 기능
- ✅ 에러 처리 및 예외 상황

```bash
python test_integration_complete.py
```

### `test_card_api_complete.py`
**카드 API 엔드포인트 완전성 테스트**

모든 카드 관련 API 엔드포인트의 동작을 검증합니다.

```bash
python test_card_api_complete.py
```

## 📁 정식 테스트 스위트

### 단위 테스트 (`tests/unit/`)

#### 도메인 테스트
- **`test_card.py`**: Card 엔티티 로직 테스트
- **`test_content_url.py`**: ContentUrl 값 객체 테스트

#### 애플리케이션 테스트
- **`test_create_card_use_case.py`**: 카드 생성 유스케이스 테스트

### 통합 테스트 (`tests/integration/`)
- **`test_card_api.py`**: 카드 API 통합 테스트

```bash
# pytest로 정식 테스트 실행
pytest tests/
```

## 🚀 테스트 실행 가이드

### 1. 전체 환경 검증
```bash
# Docker 환경 확인
python test_docker.py

# 통합 테스트 실행
python test_integration_complete.py
```

### 2. 개별 기능 테스트
```bash
# 태그 기능 검증
python test_tag_frequency.py

# 메모/태그 생성 검증
python test_card_creation_with_memo_tags.py

# 즐겨찾기/썸네일 검증
python test_favorites_and_thumbnail.py
```

### 3. 성능 및 부하 테스트
```bash
# 다중 카드 처리
python test_multiple_cards.py

# 비동기 메타데이터 처리
python test_async_metadata_completion.py
```

### 4. 정식 테스트 스위트
```bash
# 단위 테스트
pytest tests/unit/

# 통합 테스트
pytest tests/integration/

# 전체 테스트
pytest tests/
```

## 📊 테스트 커버리지

| 기능 영역 | 테스트 파일 | 상태 |
|----------|------------|------|
| 인프라 환경 | `test_docker.py` | ✅ |
| 카드 생성 | `test_card_creation_with_memo_tags.py` | ✅ |
| 즐겨찾기 | `test_favorites_and_thumbnail.py` | ✅ |
| 태그 관리 | `test_tag_frequency.py` | ✅ |
| 메타데이터 | `test_async_metadata_completion.py` | ✅ |
| 썸네일 처리 | `test_s3_thumbnail_compression.py` | ✅ |
| 통합 시나리오 | `test_integration_complete.py` | ✅ |
| API 엔드포인트 | `test_card_api_complete.py` | ✅ |

## 🔧 테스트 환경 설정

### 필수 환경 변수
```bash
# YouTube API (선택사항)
YOUTUBE_API_KEY=your_api_key

# AWS S3 (선택사항)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_S3_BUCKET=your_bucket_name
```

### Docker 환경 시작
```bash
docker compose up -d
```

### 테스트 데이터 정리
```bash
python test_cleanup.py
```

## 📝 테스트 작성 가이드

### 새로운 기능 테스트 추가 시
1. **단위 테스트**: `tests/unit/` 디렉토리에 추가
2. **통합 테스트**: `tests/integration/` 디렉토리에 추가
3. **기능 검증**: 루트에 `test_기능명.py` 파일 생성

### 테스트 명명 규칙
- **기능 테스트**: `test_기능명.py`
- **통합 테스트**: `test_integration_*.py`
- **단위 테스트**: `test_클래스명.py`

### 테스트 구조
```python
#!/usr/bin/env python3
"""
테스트 목적 및 설명

검증하는 기능들:
- 기능 1
- 기능 2
- 기능 3
"""

class TestClassName:
    async def test_specific_feature(self):
        # Given
        # When  
        # Then
        pass
```

---

**마지막 업데이트**: 2025-10-26  
**테스트 완성도**: 98% ✅  
**핵심 기능**: 태그 사용 빈도 계산 완료 🎯
