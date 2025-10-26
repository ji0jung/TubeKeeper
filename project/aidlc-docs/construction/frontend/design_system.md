# 반응형 디자인 시스템

## 브레이크포인트 정의

### 디바이스 분류
```css
/* Tailwind CSS 기본 브레이크포인트 활용 */
mobile: 320px - 767px     /* 모바일 디바이스 */
tablet: 768px - 1023px    /* 태블릿 디바이스 */
desktop: 1024px+          /* 데스크톱 디바이스 */

/* Tailwind 클래스 */
sm: 640px   /* 작은 모바일 */
md: 768px   /* 태블릿 */
lg: 1024px  /* 데스크톱 */
xl: 1280px  /* 큰 데스크톱 */
2xl: 1536px /* 초대형 화면 */
```

### 반응형 전략
- **Mobile First**: 모바일부터 설계 후 확장
- **Progressive Enhancement**: 기본 기능 → 고급 기능 순차 적용
- **Touch Friendly**: 터치 인터페이스 우선 고려

## 그리드 시스템

### 레이아웃 그리드
```css
/* 컨테이너 최대 너비 */
.container {
  mobile: 100% (padding: 16px)
  tablet: 100% (padding: 24px)  
  desktop: 1200px (center aligned)
}

/* 그리드 컬럼 */
mobile: 1-2 columns
tablet: 2-3 columns
desktop: 3-4 columns
```

### 카드 레이아웃
```css
/* 카드 목록 그리드 */
mobile: 1 column (full width)
tablet: 2 columns (gap: 16px)
desktop: 3 columns (gap: 20px)
large desktop: 4 columns (gap: 24px)
```

## 타이포그래피 시스템

### 폰트 패밀리
```css
font-family: 
  'Pretendard', /* 한글 최적화 */
  -apple-system, 
  BlinkMacSystemFont, 
  'Segoe UI', 
  Roboto, 
  sans-serif;
```

### 텍스트 스케일
```css
/* 제목 */
h1: 32px/40px (mobile), 40px/48px (desktop)
h2: 28px/36px (mobile), 32px/40px (desktop)  
h3: 24px/32px (mobile), 28px/36px (desktop)
h4: 20px/28px (mobile), 24px/32px (desktop)

/* 본문 */
body-lg: 18px/28px
body: 16px/24px
body-sm: 14px/20px
caption: 12px/16px

/* 버튼 */
button-lg: 16px/24px (font-weight: 600)
button: 14px/20px (font-weight: 600)
button-sm: 12px/16px (font-weight: 600)
```

### 반응형 타이포그래피
```css
/* Tailwind 클래스 예시 */
.heading-1 {
  @apply text-2xl md:text-3xl lg:text-4xl;
  @apply font-bold leading-tight;
}

.body-text {
  @apply text-sm md:text-base;
  @apply leading-relaxed;
}
```

## 컬러 팔레트

### 기본 컬러 시스템
```css
/* Primary (브랜드 컬러) */
primary-50: #eff6ff
primary-100: #dbeafe  
primary-500: #3b82f6  /* 메인 브랜드 컬러 */
primary-600: #2563eb
primary-900: #1e3a8a

/* Neutral (회색 계열) */
neutral-50: #f9fafb
neutral-100: #f3f4f6
neutral-200: #e5e7eb
neutral-500: #6b7280
neutral-700: #374151
neutral-900: #111827

/* Semantic (의미 컬러) */
success: #10b981
warning: #f59e0b  
error: #ef4444
info: #3b82f6
```

### 다크모드 대응 (향후 확장)
```css
/* 라이트 모드만 지원하되, 확장 가능한 구조 */
:root {
  --color-background: #ffffff;
  --color-foreground: #111827;
  --color-muted: #f3f4f6;
}
```

## 간격 시스템 (Spacing)

### 기본 간격 단위
```css
/* Tailwind 기본 스케일 활용 */
xs: 4px   (space-1)
sm: 8px   (space-2)  
md: 16px  (space-4)
lg: 24px  (space-6)
xl: 32px  (space-8)
2xl: 48px (space-12)
3xl: 64px (space-16)
```

### 컴포넌트별 간격
```css
/* 카드 간격 */
card-padding: 16px (mobile), 20px (tablet), 24px (desktop)
card-gap: 12px (mobile), 16px (tablet), 20px (desktop)

/* 섹션 간격 */
section-gap: 32px (mobile), 48px (tablet), 64px (desktop)

/* 버튼 간격 */
button-padding-sm: 8px 12px
button-padding: 12px 16px  
button-padding-lg: 16px 24px
```

## 모바일 터치 인터페이스

### 터치 타겟 크기
```css
/* 최소 터치 영역 */
min-touch-target: 44px × 44px (iOS 권장)
button-height-sm: 36px
button-height: 44px
button-height-lg: 52px

/* 터치 간격 */
touch-gap: 8px (최소 간격)
```

### 터치 제스처 지원
- **탭**: 기본 선택 동작
- **롱 프레스**: 컨텍스트 메뉴 (카드 옵션)
- **스와이프**: 카드 액션 (즐겨찾기, 삭제)
- **핀치 줌**: 이미지 확대 (썸네일)

## 애니메이션 및 전환

### 기본 전환 효과
```css
/* 표준 전환 시간 */
transition-fast: 150ms
transition-normal: 300ms  
transition-slow: 500ms

/* 이징 함수 */
ease-out: cubic-bezier(0, 0, 0.2, 1)
ease-in-out: cubic-bezier(0.4, 0, 0.2, 1)
```

### 반응형 애니메이션
```css
/* 모바일: 간소한 애니메이션 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}

/* 데스크톱: 풍부한 애니메이션 */
@media (min-width: 1024px) {
  .card-hover {
    @apply transform hover:scale-105 transition-transform;
  }
}
```

## 컴포넌트별 반응형 규칙

### 헤더 (Header)
```css
mobile: 
  - 높이: 56px
  - 햄버거 메뉴
  - 로고 + 사용자 아바타

tablet/desktop:
  - 높이: 64px  
  - 전체 네비게이션 표시
  - 검색바 포함
```

### 카드 (Card)
```css
mobile:
  - 1열 레이아웃
  - 썸네일: 16:9 비율
  - 패딩: 16px

tablet:
  - 2열 레이아웃
  - 썸네일: 16:9 비율
  - 패딩: 20px

desktop:
  - 3-4열 레이아웃
  - 썸네일: 16:9 비율
  - 패딩: 24px
  - 호버 효과 추가
```

### 폼 (Form)
```css
mobile:
  - 전체 너비 입력 필드
  - 스택 레이아웃
  - 큰 터치 타겟

desktop:
  - 최대 너비 제한 (480px)
  - 인라인 레이블 가능
  - 키보드 네비게이션 최적화
```

### 모달 (Modal)
```css
mobile:
  - 전체 화면 또는 바텀 시트
  - 스와이프로 닫기 지원

desktop:
  - 중앙 정렬 모달
  - 배경 클릭으로 닫기
  - ESC 키 지원
```

## 성능 최적화

### 이미지 반응형
```css
/* 썸네일 최적화 */
mobile: 320px width
tablet: 400px width  
desktop: 300px width (그리드 고려)

/* WebP 지원 */
.thumbnail {
  background-image: 
    image-set(
      url('image.webp') type('image/webp'),
      url('image.jpg') type('image/jpeg')
    );
}
```

### CSS 최적화
- **Critical CSS**: 첫 화면 렌더링에 필요한 CSS 우선 로드
- **Purge CSS**: 사용하지 않는 Tailwind 클래스 제거
- **CSS Grid/Flexbox**: 레이아웃 최적화

## 접근성 고려사항

### 반응형 접근성
```css
/* 포커스 표시 */
.focus-visible {
  @apply ring-2 ring-primary-500 ring-offset-2;
}

/* 고대비 모드 지원 */
@media (prefers-contrast: high) {
  .card {
    @apply border-2 border-neutral-900;
  }
}

/* 큰 텍스트 모드 */
@media (min-resolution: 2dppx) {
  .text-sm {
    @apply text-base;
  }
}
```

### 키보드 네비게이션
- **Tab 순서**: 논리적 순서로 포커스 이동
- **Skip Links**: 메인 콘텐츠로 바로 이동
- **ARIA Labels**: 스크린 리더 지원

이 디자인 시스템은 US-013 반응형 디자인 요구사항을 충족하며, 모든 디바이스에서 일관된 사용자 경험을 제공합니다.
