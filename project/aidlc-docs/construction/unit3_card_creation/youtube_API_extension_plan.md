# 📋 **Unit3 카드 관리 시스템 - YouTube API 확장 계획**

## 🎯 **현재 완료된 기능**

### ✅ **핵심 기능**
- 카드 CRUD (생성, 조회, 수정, 삭제)
- YouTube 메타데이터 수집 (제목, 썸네일, 재생시간, 발행일)
- 사용자 메모 및 태그 관리
- 즐겨찾기 기능
- 공개/비공개 설정
- 커서 기반 페이지네이션

### ✅ **기술적 완성도**
- 도메인 주도 설계 (DDD) 적용
- 클린 아키텍처 구조
- 단위/통합 테스트 완료
- API 문서화
- 데이터베이스 스키마 설계

---

## 📊 **YouTube 카테고리 분석 결과**

### **사용자 설정 가능한 카테고리 (assignable: true)**

| ID | 영문명 | 한국어명 | 활용도 |
|----|--------|----------|--------|
| **1** | Film & Animation | 영화 & 애니메이션 | ⭐⭐⭐ |
| **2** | Autos & Vehicles | 자동차 & 교통수단 | ⭐⭐ |
| **10** | Music | 음악 | ⭐⭐⭐⭐⭐ |
| **15** | Pets & Animals | 반려동물 & 동물 | ⭐⭐⭐ |
| **17** | Sports | 스포츠 | ⭐⭐⭐⭐ |
| **19** | Travel & Events | 여행 & 이벤트 | ⭐⭐⭐⭐ |
| **20** | Gaming | 게임 | ⭐⭐⭐⭐⭐ |
| **22** | People & Blogs | 사람 & 블로그 | ⭐⭐⭐⭐⭐ |
| **23** | Comedy | 코미디 | ⭐⭐⭐ |
| **24** | Entertainment | 엔터테인먼트 | ⭐⭐⭐⭐ |
| **25** | News & Politics | 뉴스 & 정치 | ⭐⭐ |
| **26** | **Howto & Style** | **하우투 & 스타일** | ⭐⭐⭐⭐⭐ |
| **27** | Education | 교육 | ⭐⭐⭐⭐⭐ |
| **28** | Science & Technology | 과학 & 기술 | ⭐⭐⭐⭐ |

### **시스템 전용 카테고리 (assignable: false)**
- **18**: Short Movies (단편 영화)
- **21**: Videoblogging (비디오 블로깅)
- **30-44**: Movies 관련 세부 장르들
- **42**: Shorts (YouTube Shorts)
- **43**: Shows (TV 쇼)

### **우리 앱 타겟 카테고리 분석**

#### **🎯 핵심 타겟 (높은 활용도 예상)**
- **26 - Howto & Style**: 패션, 뷰티, 라이프스타일
- **27 - Education**: 학습, 튜토리얼, 강의
- **22 - People & Blogs**: 일상 브이로그, 개인 채널
- **20 - Gaming**: 게임 리뷰, 플레이 영상
- **10 - Music**: 음악, MV, 커버

#### **🎯 보조 타겟 (중간 활용도)**
- **28 - Science & Technology**: IT, 개발, 리뷰
- **17 - Sports**: 운동, 피트니스, 스포츠
- **19 - Travel & Events**: 여행, 맛집, 이벤트
- **24 - Entertainment**: 예능, 엔터테인먼트

---

## 🚀 **Phase 2: 고도화 기능 개발 계획**

### **우선순위 1: YouTube 메타데이터 확장**

#### **1.1 YouTube 카테고리 연동**
```python
# 구현 예정 기능
class YouTubeCategory:
    category_id: str
    category_name: str
    korean_name: str
    
# 자동 카테고리 매핑
youtube_category_mapping = {
    "26": "패션/뷰티",
    "27": "교육/학습", 
    "28": "IT/기술",
    "10": "음악/엔터",
    "20": "게임",
    "22": "일상/브이로그",
    "17": "스포츠/운동",
    "19": "여행/라이프",
    "24": "엔터테인먼트"
}
```

**개발 내용:**
- YouTube API에서 categoryId 수집
- 카드 생성 시 자동 카테고리 제안
- 카테고리별 통계 및 필터링
- 사용자 선호 카테고리 분석

#### **1.2 YouTube 태그 시스템**
```python
# 구현 예정 구조
@dataclass
class CardTags:
    user_tags: List[str]      # 사용자 입력 태그
    youtube_tags: List[str]   # YouTube 원본 태그
    suggested_tags: List[str] # AI 추천 태그
```

**개발 내용:**
- YouTube API tags 필드 수집
- 사용자 태그와 YouTube 태그 분리 저장
- 태그 기반 검색 및 필터링
- 인기 태그 추천 시스템

### **우선순위 2: 제품 링크 파싱 시스템**

#### **2.1 Description 파싱 엔진**
```python
class ProductLinkExtractor:
    def extract_links(self, description: str) -> List[ProductLink]:
        # 정규식으로 쇼핑몰 링크 추출
        # 제품명과 링크 매칭
        # 가격 정보 스크래핑
        pass
```

**개발 내용:**
- 주요 쇼핑몰 도메인 인식 (무신사, 지그재그, W컨셉 등)
- 제품명-링크 매칭 알고리즘
- 제품 메타데이터 수집 (제목, 가격, 이미지)
- 링크 유효성 검사 및 업데이트

#### **2.2 제품 정보 구조화**
```python
@dataclass
class ProductInfo:
    name: str
    url: str
    price: Optional[str]
    image_url: Optional[str]
    brand: Optional[str]
    category: Optional[str]
```

**개발 내용:**
- AI 기반 제품 정보 추출
- 브랜드 및 카테고리 자동 분류
- 가격 변동 추적
- 제품 리뷰 연동

---

## 💡 **추가 후보 아이디어**

### **2. 카테고리별 통계**
- 가장 많이 저장되는 YouTube 카테고리 분석
- 사용자별 선호 카테고리 패턴 파악

### **3. 추천 시스템**
- 동일한 YouTube 카테고리의 다른 영상 추천
- 카테고리 기반 사용자 취향 분석

---

## 📊 **데이터베이스 스키마 확장 계획**

### **새로 추가될 테이블**

#### **youtube_categories**
```sql
CREATE TABLE youtube_categories (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    korean_name VARCHAR(100),
    assignable BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 0  -- 우리 앱에서의 중요도
);

-- 초기 데이터 삽입
INSERT INTO youtube_categories VALUES 
('26', 'Howto & Style', '하우투 & 스타일', true, 5),
('27', 'Education', '교육', true, 5),
('22', 'People & Blogs', '사람 & 블로그', true, 5),
('20', 'Gaming', '게임', true, 5),
('10', 'Music', '음악', true, 5),
('28', 'Science & Technology', '과학 & 기술', true, 4),
('17', 'Sports', '스포츠', true, 4),
('19', 'Travel & Events', '여행 & 이벤트', true, 4),
('24', 'Entertainment', '엔터테인먼트', true, 4);
```

#### **card_youtube_tags**
```sql
CREATE TABLE card_youtube_tags (
    card_id UUID REFERENCES cards(card_id),
    tag VARCHAR(100),
    PRIMARY KEY (card_id, tag)
);
```

#### **product_links**
```sql
CREATE TABLE product_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id UUID REFERENCES cards(card_id),
    name VARCHAR(200),
    url TEXT NOT NULL,
    price VARCHAR(50),
    image_url TEXT,
    brand VARCHAR(100),
    extracted_at TIMESTAMP DEFAULT NOW()
);
```

#### **user_category_stats** (통계 기능용)
```sql
CREATE TABLE user_category_stats (
    user_id UUID REFERENCES users(user_id),
    youtube_category_id VARCHAR(10),
    card_count INTEGER DEFAULT 0,
    last_saved_at TIMESTAMP,
    PRIMARY KEY (user_id, youtube_category_id)
);
```

---

## 🔧 **API 확장 계획**

### **새로운 엔드포인트**

#### **카테고리 관련**
```http
GET /api/categories/youtube
GET /api/cards/by-youtube-category/{category_id}
GET /api/analytics/categories
GET /api/users/{user_id}/category-stats
```

#### **태그 관련**
```http
GET /api/tags/popular
GET /api/tags/suggestions?query={keyword}
GET /api/cards/by-tag/{tag}
```

#### **제품 링크 관련**
```http
GET /api/cards/{id}/products
POST /api/cards/{id}/products/refresh
GET /api/products/trending
```

#### **추천 시스템**
```http
GET /api/recommendations/by-category
GET /api/recommendations/similar-users
GET /api/analytics/user-preferences
```

---

## 🧪 **테스트 계획**

### **추가 테스트 시나리오**
- YouTube 카테고리 매핑 정확성
- 태그 추출 및 분리 로직
- 제품 링크 파싱 성능
- 대용량 description 처리
- 외부 API 장애 대응
- 통계 데이터 정확성
- 추천 알고리즘 성능

---

## 📈 **성능 최적화 계획**

### **캐싱 전략**
- YouTube 카테고리 정보 캐싱
- 인기 태그 Redis 캐싱
- 제품 메타데이터 캐싱
- 사용자 통계 데이터 캐싱
- 추천 결과 캐싱

### **배치 처리**
- 기존 카드 YouTube 태그 일괄 수집
- 제품 링크 유효성 정기 검사
- 가격 정보 업데이트 스케줄링
- 사용자 카테고리 통계 업데이트
- 추천 모델 학습 및 업데이트

---

## 🎯 **개발 마일스톤**

### **Phase 2.1: YouTube 메타데이터 확장 (2주)**
- [ ] YouTube 카테고리 API 연동
- [ ] YouTube 태그 수집 및 저장
- [ ] 기존 데이터 마이그레이션
- [ ] API 엔드포인트 추가

### **Phase 2.2: 제품 링크 파싱 (3주)**
- [ ] Description 파싱 엔진 개발
- [ ] 주요 쇼핑몰 메타데이터 수집기
- [ ] 제품 정보 구조화 AI 모델
- [ ] 제품 관련 API 개발

### **Phase 2.3: 통계 및 추천 시스템 (2주)**
- [ ] 카테고리별 통계 수집 시스템
- [ ] 사용자 선호도 분석 알고리즘
- [ ] 기본 추천 시스템 구현
- [ ] 통계 대시보드 API

### **Phase 2.4: 통합 및 최적화 (1주)**
- [ ] 전체 기능 통합 테스트
- [ ] 성능 최적화
- [ ] 문서 업데이트
- [ ] 배포 및 모니터링

---

## 📝 **기술 스택 추가 요소**

### **새로운 의존성**
- **BeautifulSoup4**: 웹 스크래핑
- **aiohttp**: 비동기 HTTP 클라이언트
- **redis-py**: 캐싱
- **celery**: 배치 작업 스케줄링
- **pandas**: 데이터 분석
- **scikit-learn**: 추천 알고리즘

### **외부 서비스**
- **YouTube Data API v3**: 확장된 메타데이터
- **쇼핑몰 API**: 제품 정보 (가능한 경우)
- **가격 비교 서비스**: 가격 추적

---

## 🔍 **YouTube API 응답 예시**

### **현재 수집 중인 필드**
```json
{
  "title": "영상 제목",
  "thumbnails": {"high": {"url": "..."}},
  "publishedAt": "2024-10-25T10:30:00Z",
  "duration": "PT15M33S"
}
```

### **추가 수집 예정 필드**
```json
{
  "categoryId": "26",
  "channelTitle": "채널명",
  "tags": ["패션", "스타일링", "하울"],
  "description": "제품 정보\n무신사: https://...\n지그재그: https://..."
}
```

---

## 📋 **구현 우선순위**

1. **YouTube 태그 수집** (가장 간단, 즉시 가치 제공)
2. **YouTube 카테고리 연동** (자동 분류 기능)
3. **카테고리별 통계** (사용자 인사이트 제공)
4. **기본 추천 시스템** (사용자 경험 향상)
5. **제품 링크 파싱** (가장 복잡하지만 높은 가치)

**배포 완료 후 이 계획서를 바탕으로 단계적 고도화를 진행합니다!** 🚀
