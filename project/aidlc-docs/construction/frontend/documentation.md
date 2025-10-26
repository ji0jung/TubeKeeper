# 문서화 및 가이드라인

## 컴포넌트 사용 가이드

### 1. 컴포넌트 문서화 표준
```typescript
// shared/components/ui/Button/README.md
# Button 컴포넌트

재사용 가능한 버튼 컴포넌트입니다.

## 사용법

```tsx
import { Button } from '@/shared/components/ui/Button';

// 기본 사용
<Button onClick={handleClick}>클릭하세요</Button>

// 다양한 variant
<Button variant="primary">Primary</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="outline">Outline</Button>

// 아이콘과 함께
<Button leftIcon={<PlusIcon />}>추가</Button>

// 로딩 상태
<Button loading>처리 중...</Button>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | 'primary' \| 'secondary' \| 'outline' \| 'ghost' | 'primary' | 버튼 스타일 |
| size | 'sm' \| 'md' \| 'lg' | 'md' | 버튼 크기 |
| loading | boolean | false | 로딩 상태 표시 |
| disabled | boolean | false | 비활성화 상태 |
| fullWidth | boolean | false | 전체 너비 사용 |
| leftIcon | ReactNode | - | 왼쪽 아이콘 |
| rightIcon | ReactNode | - | 오른쪽 아이콘 |

## 접근성

- 키보드 네비게이션 지원 (Tab, Enter, Space)
- 스크린 리더 호환
- 적절한 색상 대비 (WCAG AA)
- 로딩 상태 시 aria-label 제공

## 예시

### 기본 버튼들
```tsx
<div className="flex gap-2">
  <Button variant="primary">Primary</Button>
  <Button variant="secondary">Secondary</Button>
  <Button variant="outline">Outline</Button>
  <Button variant="ghost">Ghost</Button>
</div>
```

### 크기별 버튼
```tsx
<div className="flex items-center gap-2">
  <Button size="sm">Small</Button>
  <Button size="md">Medium</Button>
  <Button size="lg">Large</Button>
</div>
```
```

### 2. 훅 문서화 표준
```typescript
// shared/hooks/useDebounce/README.md
# useDebounce 훅

값의 변경을 지연시켜 불필요한 API 호출을 방지하는 훅입니다.

## 사용법

```tsx
import { useDebounce } from '@/shared/hooks/useDebounce';

function SearchComponent() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (debouncedQuery) {
      // API 호출
      searchApi(debouncedQuery);
    }
  }, [debouncedQuery]);

  return (
    <input
      value={query}
      onChange={(e) => setQuery(e.target.value)}
      placeholder="검색어 입력..."
    />
  );
}
```

## 매개변수

- `value: T` - 디바운스할 값
- `delay: number` - 지연 시간 (밀리초)

## 반환값

- `T` - 디바운스된 값

## 사용 사례

- 검색 입력 최적화
- API 호출 빈도 제한
- 실시간 검증 지연
```

## 코딩 컨벤션

### 1. TypeScript 컨벤션
```typescript
// 좋은 예시
interface UserProfile {
  id: string;
  email: string;
  displayName: string;
  avatar?: string;
}

// 나쁜 예시
interface userprofile {
  id: any;
  email: any;
  displayname: any;
  avatar: any;
}

// 컴포넌트 Props 네이밍
interface ButtonProps {
  variant: 'primary' | 'secondary';
  onClick: () => void;
}

// 훅 반환 타입
interface UseAuthReturn {
  user: User | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}
```

### 2. 컴포넌트 구조 컨벤션
```typescript
// 컴포넌트 파일 구조
import React, { useState, useEffect } from 'react';
import { SomeIcon } from '@heroicons/react/24/outline';

import { Button } from '@/shared/components/ui/Button';
import { useAuth } from '@/features/auth/hooks/useAuth';
import { formatDate } from '@/shared/utils/dateUtils';

// 1. 타입 정의
interface ComponentProps {
  title: string;
  onSubmit: (data: FormData) => void;
}

// 2. 컴포넌트 정의
export const Component: React.FC<ComponentProps> = ({
  title,
  onSubmit
}) => {
  // 3. 상태 및 훅
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useAuth();

  // 4. 이벤트 핸들러
  const handleSubmit = useCallback((data: FormData) => {
    setIsLoading(true);
    onSubmit(data);
  }, [onSubmit]);

  // 5. 부수 효과
  useEffect(() => {
    // 초기화 로직
  }, []);

  // 6. 렌더링
  return (
    <div className="component-container">
      <h1>{title}</h1>
      {/* 컴포넌트 내용 */}
    </div>
  );
};
```

### 3. 파일 및 폴더 네이밍
```
// 컴포넌트: PascalCase
Button.tsx
CardList.tsx
UserProfile.tsx

// 훅: camelCase with 'use' prefix
useAuth.ts
useDebounce.ts
useLocalStorage.ts

// 유틸리티: camelCase
dateUtils.ts
validationUtils.ts
apiClient.ts

// 타입: camelCase with '.types' suffix
auth.types.ts
card.types.ts
api.types.ts

// 상수: UPPER_SNAKE_CASE
API_ENDPOINTS.ts
ERROR_MESSAGES.ts
```

## 배포 가이드

### 1. 환경별 배포 절차

#### 개발 환경 배포
```bash
# 1. 의존성 설치
npm install

# 2. 환경 변수 설정
cp .env.example .env.local
# .env.local 파일 수정

# 3. 개발 서버 실행
npm run dev

# 4. 테스트 실행
npm run test
npm run test:e2e
```

#### 스테이징 환경 배포
```bash
# 1. 스테이징 브랜치로 전환
git checkout staging

# 2. 최신 변경사항 병합
git merge develop

# 3. 빌드 및 테스트
npm run build:staging
npm run test:run

# 4. 배포 (자동화된 경우)
git push origin staging
```

#### 프로덕션 환경 배포
```bash
# 1. 메인 브랜치로 전환
git checkout main

# 2. 스테이징 변경사항 병합
git merge staging

# 3. 버전 태그 생성
npm version patch  # 또는 minor, major
git push origin main --tags

# 4. 프로덕션 배포 (GitHub Actions 자동 실행)
# 배포 완료 후 확인
curl -f https://youtubeapp.com/health
```

### 2. 배포 체크리스트

#### 배포 전 확인사항
- [ ] 모든 테스트 통과 (단위, 통합, E2E)
- [ ] 코드 리뷰 완료
- [ ] 환경 변수 설정 확인
- [ ] 빌드 에러 없음
- [ ] 번들 크기 확인 (1MB 이하)
- [ ] 접근성 테스트 통과
- [ ] 성능 테스트 통과 (Lighthouse 90점 이상)

#### 배포 후 확인사항
- [ ] 애플리케이션 정상 로드
- [ ] 주요 기능 동작 확인
- [ ] API 연동 정상
- [ ] 에러 모니터링 확인
- [ ] 성능 지표 확인

## 트러블슈팅 가이드

### 1. 일반적인 문제 해결

#### 빌드 실패
```bash
# 의존성 문제
rm -rf node_modules package-lock.json
npm install

# 타입 에러
npm run type-check

# 메모리 부족
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

#### 개발 서버 문제
```bash
# 포트 충돌
lsof -ti:5173 | xargs kill -9
npm run dev

# 캐시 문제
rm -rf .vite
npm run dev
```

#### 테스트 실패
```bash
# 테스트 캐시 클리어
npm run test -- --clearCache

# 특정 테스트 실행
npm run test -- Button.test.tsx

# 디버그 모드
npm run test -- --inspect-brk
```

### 2. 성능 문제 해결

#### 번들 크기 분석
```bash
# 번들 분석 실행
npm run build:analyze

# 큰 의존성 확인
npx webpack-bundle-analyzer dist/stats.json
```

#### 메모리 누수 디버깅
```typescript
// React DevTools Profiler 사용
// 또는 브라우저 개발자 도구 Memory 탭 활용

// 컴포넌트에서 메모리 누수 방지
useEffect(() => {
  const subscription = api.subscribe();
  
  return () => {
    subscription.unsubscribe(); // 정리 함수 필수
  };
}, []);
```

### 3. 접근성 문제 해결

#### 자동 테스트
```bash
# Storybook에서 접근성 테스트
npm run storybook
# Accessibility 탭 확인

# axe-core로 자동 테스트
npm run test:a11y
```

#### 수동 테스트
- 키보드만으로 모든 기능 사용 가능한지 확인
- 스크린 리더로 콘텐츠 읽기 테스트
- 고대비 모드에서 시각적 확인

## 유지보수 가이드

### 1. 정기 업데이트

#### 의존성 업데이트
```bash
# 보안 취약점 확인
npm audit

# 의존성 업데이트 확인
npx npm-check-updates

# 안전한 업데이트
npm update

# 메이저 버전 업데이트 (주의)
npx npm-check-updates -u
npm install
```

#### 코드 품질 유지
```bash
# 정기적인 린트 실행
npm run lint

# 사용하지 않는 코드 제거
npx unimported

# 중복 코드 검사
npx jscpd src/
```

### 2. 모니터링 및 로깅

#### 에러 모니터링 (Sentry)
```typescript
// src/shared/services/monitoring.ts
import * as Sentry from '@sentry/react';

if (env.SENTRY_DSN) {
  Sentry.init({
    dsn: env.SENTRY_DSN,
    environment: env.APP_ENV,
    tracesSampleRate: env.APP_ENV === 'production' ? 0.1 : 1.0,
  });
}

export const captureError = (error: Error, context?: any) => {
  if (env.APP_ENV === 'development') {
    console.error(error, context);
  } else {
    Sentry.captureException(error, { extra: context });
  }
};
```

#### 성능 모니터링
```typescript
// src/shared/hooks/usePerformanceMonitoring.ts
export const usePerformanceMonitoring = () => {
  useEffect(() => {
    // Core Web Vitals 측정
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(console.log);
      getFID(console.log);
      getFCP(console.log);
      getLCP(console.log);
      getTTFB(console.log);
    });
  }, []);
};
```

이 문서화 가이드는 개발팀의 생산성과 코드 품질을 보장하며, 프로젝트의 장기적인 유지보수를 지원합니다.
