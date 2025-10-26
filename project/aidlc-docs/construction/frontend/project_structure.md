# 프로젝트 구조 및 폴더 구성

## 전체 폴더 구조

```
youtube-link-app/
├── public/                    # 정적 파일
│   ├── favicon.ico
│   ├── manifest.json
│   └── robots.txt
├── src/
│   ├── app/                   # 앱 설정 및 프로바이더
│   │   ├── providers/         # React Query, Router 등 프로바이더
│   │   ├── router/           # 라우팅 설정
│   │   ├── store/            # Zustand 스토어
│   │   └── App.tsx           # 루트 컴포넌트
│   ├── features/             # 도메인별 기능 모듈
│   │   ├── auth/             # 인증 및 프로필 관리
│   │   ├── cards/            # 카드 생성 및 관리
│   │   ├── categories/       # 카테고리 관리
│   │   ├── search/           # 카드 검색 및 표시
│   │   └── sharing/          # 카드 공유
│   ├── shared/               # 공통 모듈
│   │   ├── components/       # 재사용 가능한 UI 컴포넌트
│   │   ├── hooks/            # 커스텀 훅
│   │   ├── services/         # API 클라이언트
│   │   ├── utils/            # 유틸리티 함수
│   │   ├── types/            # 공통 타입 정의
│   │   └── constants/        # 상수
│   ├── assets/               # 정적 자산
│   │   ├── images/
│   │   └── icons/
│   ├── styles/               # 전역 스타일
│   │   ├── globals.css
│   │   └── tailwind.css
│   ├── main.tsx              # 앱 진입점
│   └── vite-env.d.ts         # Vite 타입 정의
├── .storybook/               # Storybook 설정
├── tests/                    # 테스트 파일
│   ├── __mocks__/
│   ├── setup.ts
│   └── utils/
├── package.json
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── README.md
```

## Feature 모듈 상세 구조

### features/auth/ (인증 및 프로필 관리)
```
auth/
├── components/               # 인증 관련 컴포넌트
│   ├── LoginForm.tsx
│   ├── RegisterForm.tsx
│   ├── VerificationForm.tsx
│   └── ProfileForm.tsx
├── hooks/                    # 인증 관련 훅
│   ├── useAuth.ts
│   ├── useLogin.ts
│   ├── useRegister.ts
│   └── useProfile.ts
├── services/                 # 인증 API 호출
│   ├── authApi.ts
│   └── profileApi.ts
├── types/                    # 인증 관련 타입
│   ├── auth.types.ts
│   └── profile.types.ts
├── utils/                    # 인증 유틸리티
│   ├── tokenStorage.ts
│   └── validation.ts
└── index.ts                  # 외부 노출 인터페이스
```

### features/cards/ (카드 생성 및 관리)
```
cards/
├── components/
│   ├── CardForm.tsx          # 카드 생성 폼
│   ├── CardList.tsx          # 카드 목록
│   ├── CardItem.tsx          # 개별 카드
│   ├── CardDetail.tsx        # 카드 상세
│   └── LoadingStates/        # 로딩 상태 컴포넌트
│       ├── CardSkeleton.tsx
│       ├── SummaryProgress.tsx
│       └── CreationSpinner.tsx
├── hooks/
│   ├── useCards.ts           # 카드 목록 관리
│   ├── useCardCreation.ts    # 카드 생성
│   ├── useCardDetail.ts      # 카드 상세
│   └── useFavorites.ts       # 즐겨찾기
├── services/
│   ├── cardApi.ts
│   ├── youtubeApi.ts
│   └── aiApi.ts
├── types/
│   └── card.types.ts
└── index.ts
```

### features/categories/ (카테고리 관리)
```
categories/
├── components/
│   ├── CategoryList.tsx
│   ├── CategoryForm.tsx
│   └── CategorySelector.tsx
├── hooks/
│   ├── useCategories.ts
│   └── useCategoryManagement.ts
├── services/
│   └── categoryApi.ts
├── types/
│   └── category.types.ts
└── index.ts
```

### features/search/ (카드 검색 및 표시)
```
search/
├── components/
│   ├── SearchBar.tsx
│   ├── SearchFilters.tsx
│   ├── SearchResults.tsx
│   ├── PublicCardList.tsx
│   └── LoadingStates/
│       └── SearchSkeleton.tsx
├── hooks/
│   ├── useSearch.ts
│   ├── usePublicCards.ts
│   └── useSearchSuggestions.ts
├── services/
│   └── searchApi.ts
├── types/
│   └── search.types.ts
└── index.ts
```

### features/sharing/ (카드 공유)
```
sharing/
├── components/
│   ├── ShareButton.tsx
│   ├── ShareModal.tsx
│   └── SharedCardView.tsx
├── hooks/
│   ├── useSharing.ts
│   └── useSharedCard.ts
├── services/
│   └── sharingApi.ts
├── types/
│   └── sharing.types.ts
└── index.ts
```

## shared/ 모듈 상세 구조

### shared/components/ (공통 UI 컴포넌트)
```
components/
├── ui/                       # 기본 UI 컴포넌트
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.stories.tsx
│   │   └── Button.test.tsx
│   ├── Input/
│   ├── Modal/
│   ├── Spinner/
│   └── ProgressBar/
├── layout/                   # 레이아웃 컴포넌트
│   ├── Header.tsx
│   ├── Sidebar.tsx
│   ├── Footer.tsx
│   └── PageLayout.tsx
├── feedback/                 # 피드백 컴포넌트
│   ├── Toast.tsx
│   ├── ErrorBoundary.tsx
│   └── LoadingOverlay.tsx
└── navigation/               # 네비게이션 컴포넌트
    ├── NavLink.tsx
    └── Breadcrumb.tsx
```

### shared/hooks/ (공통 훅)
```
hooks/
├── useApi.ts                 # API 호출 공통 훅
├── useLocalStorage.ts        # 로컬 스토리지 훅
├── useDebounce.ts           # 디바운스 훅
├── useInfiniteScroll.ts     # 무한 스크롤 훅
├── useResponsive.ts         # 반응형 훅
└── useLoadingState.ts       # 로딩 상태 훅
```

### shared/services/ (API 클라이언트)
```
services/
├── api/
│   ├── client.ts            # Axios 클라이언트 설정
│   ├── interceptors.ts      # 요청/응답 인터셉터
│   └── endpoints.ts         # API 엔드포인트 상수
├── auth/
│   └── tokenManager.ts      # 토큰 관리
└── utils/
    ├── errorHandler.ts      # 에러 처리
    └── responseTransformer.ts # 응답 변환
```

## 라우팅 구조

### app/router/routes.tsx
```typescript
// 라우트 정의
const routes = [
  {
    path: '/',
    element: <HomePage />,
  },
  {
    path: '/auth',
    children: [
      { path: 'login', element: <LoginPage /> },
      { path: 'register', element: <RegisterPage /> },
    ],
  },
  {
    path: '/cards',
    element: <ProtectedRoute />,
    children: [
      { path: '', element: <CardListPage /> },
      { path: ':id', element: <CardDetailPage /> },
      { path: 'create', element: <CardCreatePage /> },
    ],
  },
  {
    path: '/search',
    element: <SearchPage />,
  },
  {
    path: '/shared/:shareId',
    element: <SharedCardPage />,
  },
];
```

## 컴포넌트 계층 구조

```
App
├── Providers (React Query, Router, Toast)
├── Layout
│   ├── Header
│   │   ├── Navigation
│   │   └── UserMenu
│   ├── Main Content
│   │   └── Route Components
│   └── Footer
└── Global Components
    ├── ErrorBoundary
    ├── LoadingOverlay
    └── Toast Container
```

## 네이밍 컨벤션

### 파일 및 폴더
- **컴포넌트**: PascalCase (Button.tsx, CardList.tsx)
- **훅**: camelCase with 'use' prefix (useAuth.ts, useCards.ts)
- **유틸리티**: camelCase (formatDate.ts, validation.ts)
- **타입**: camelCase with '.types' suffix (auth.types.ts)
- **상수**: UPPER_SNAKE_CASE (API_ENDPOINTS.ts)

### 컴포넌트 Props
```typescript
// Props 인터페이스는 컴포넌트명 + Props
interface ButtonProps {
  variant: 'primary' | 'secondary';
  size: 'sm' | 'md' | 'lg';
  onClick: () => void;
}
```

## Import/Export 규칙

### Feature 모듈 index.ts
```typescript
// features/auth/index.ts
export { LoginForm, RegisterForm } from './components';
export { useAuth, useLogin } from './hooks';
export type { User, AuthState } from './types';
```

### 절대 경로 Import
```typescript
// tsconfig.json paths 설정 활용
import { Button } from '@/shared/components';
import { useAuth } from '@/features/auth';
import { API_ENDPOINTS } from '@/shared/constants';
```

이 구조는 확장성과 유지보수성을 고려하여 설계되었으며, 각 도메인별로 독립적인 개발이 가능합니다.
