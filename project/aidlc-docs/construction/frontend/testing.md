# 테스트 전략 및 가이드라인

## 테스트 피라미드

```
        E2E Tests (10%)
       /              \
    Integration Tests (20%)
   /                      \
  Unit Tests (70%)
```

### 1. 단위 테스트 (Unit Tests) - 70%
- **도구**: Vitest + React Testing Library
- **대상**: 컴포넌트, 훅, 유틸리티 함수
- **목표**: 빠른 피드백, 높은 커버리지

### 2. 통합 테스트 (Integration Tests) - 20%
- **도구**: Vitest + MSW (Mock Service Worker)
- **대상**: API 통신, 상태 관리, 컴포넌트 간 상호작용
- **목표**: 실제 사용 시나리오 검증

### 3. E2E 테스트 (End-to-End Tests) - 10%
- **도구**: Playwright
- **대상**: 핵심 사용자 플로우
- **목표**: 전체 시스템 동작 검증

## 단위 테스트 전략

### 1. 컴포넌트 테스트
```typescript
// shared/components/ui/Button/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toHaveTextContent('Click me');
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('shows loading state', () => {
    render(<Button loading>Loading</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(screen.getByLabelText('로딩 중')).toBeInTheDocument();
  });

  it('applies correct variant styles', () => {
    render(<Button variant="secondary">Secondary</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-neutral-100');
  });

  it('supports keyboard navigation', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    const button = screen.getByRole('button');
    button.focus();
    fireEvent.keyDown(button, { key: 'Enter' });
    
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### 2. 훅 테스트
```typescript
// shared/hooks/useDebounce.test.ts
import { renderHook, act } from '@testing-library/react';
import { useDebounce } from './useDebounce';

describe('useDebounce', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('debounces value changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 500 } }
    );

    expect(result.current).toBe('initial');

    // 값 변경
    rerender({ value: 'updated', delay: 500 });
    expect(result.current).toBe('initial'); // 아직 변경되지 않음

    // 시간 경과
    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe('updated');
  });

  it('cancels previous timeout on rapid changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'first', delay: 500 } }
    );

    rerender({ value: 'second', delay: 500 });
    
    act(() => {
      jest.advanceTimersByTime(300);
    });
    
    rerender({ value: 'third', delay: 500 });
    
    act(() => {
      jest.advanceTimersByTime(500);
    });

    expect(result.current).toBe('third');
  });
});
```

### 3. 유틸리티 함수 테스트
```typescript
// shared/utils/validation.test.ts
import { validateEmail, validateYouTubeUrl } from './validation';

describe('validation utils', () => {
  describe('validateEmail', () => {
    it('validates correct email formats', () => {
      expect(validateEmail('test@example.com')).toBe(true);
      expect(validateEmail('user.name+tag@domain.co.kr')).toBe(true);
    });

    it('rejects invalid email formats', () => {
      expect(validateEmail('invalid-email')).toBe(false);
      expect(validateEmail('test@')).toBe(false);
      expect(validateEmail('@domain.com')).toBe(false);
    });
  });

  describe('validateYouTubeUrl', () => {
    it('validates YouTube URLs', () => {
      expect(validateYouTubeUrl('https://www.youtube.com/watch?v=dQw4w9WgXcQ')).toBe(true);
      expect(validateYouTubeUrl('https://youtu.be/dQw4w9WgXcQ')).toBe(true);
    });

    it('rejects non-YouTube URLs', () => {
      expect(validateYouTubeUrl('https://vimeo.com/123456')).toBe(false);
      expect(validateYouTubeUrl('not-a-url')).toBe(false);
    });
  });
});
```

## 통합 테스트 전략

### 1. API 통신 테스트 (MSW)
```typescript
// tests/mocks/handlers.ts
import { rest } from 'msw';
import { API_ENDPOINTS } from '@/shared/services/api/endpoints';

export const handlers = [
  // 카드 목록 조회
  rest.get(`*/api${API_ENDPOINTS.CARDS.LIST}`, (req, res, ctx) => {
    const cursor = req.url.searchParams.get('cursor');
    const limit = parseInt(req.url.searchParams.get('limit') || '10');

    return res(
      ctx.json({
        cards: mockCards.slice(0, limit),
        nextCursor: cursor ? null : 'next-cursor',
        hasMore: !cursor,
      })
    );
  }),

  // 카드 생성
  rest.post(`*/api${API_ENDPOINTS.CARDS.CREATE}`, (req, res, ctx) => {
    return res(
      ctx.json({
        success: true,
        card: {
          id: 'new-card-id',
          status: 'CREATING',
          ...req.body,
        },
      })
    );
  }),

  // 인증 에러 시뮬레이션
  rest.get(`*/api${API_ENDPOINTS.PROFILE.GET}`, (req, res, ctx) => {
    const authHeader = req.headers.get('Authorization');
    
    if (!authHeader || authHeader === 'Bearer invalid-token') {
      return res(
        ctx.status(401),
        ctx.json({
          error: {
            code: 'AUTH_002',
            message: 'Token expired',
          },
        })
      );
    }

    return res(ctx.json({ user: mockUser }));
  }),
];
```

### 2. 상태 관리 통합 테스트
```typescript
// features/cards/hooks/useCards.test.tsx
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useCards } from './useCards';
import { server } from '@/tests/mocks/server';

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useCards', () => {
  it('fetches cards successfully', async () => {
    const { result } = renderHook(
      () => useCards({ limit: 10 }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data?.pages[0].cards).toHaveLength(10);
    expect(result.current.data?.pages[0].hasMore).toBe(true);
  });

  it('handles API errors', async () => {
    server.use(
      rest.get('*/api/cards', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Server error' }));
      })
    );

    const { result } = renderHook(
      () => useCards({ limit: 10 }),
      { wrapper: createWrapper() }
    );

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
  });
});
```

### 3. 컴포넌트 통합 테스트
```typescript
// features/cards/components/CardList.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { CardList } from './CardList';

const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </BrowserRouter>
  );
};

describe('CardList Integration', () => {
  it('displays cards from API', async () => {
    render(<CardList />, { wrapper: AllTheProviders });

    // 로딩 상태 확인
    expect(screen.getByLabelText('콘텐츠 로딩 중')).toBeInTheDocument();

    // 카드 로드 완료 대기
    await waitFor(() => {
      expect(screen.getByText('Test Card 1')).toBeInTheDocument();
    });

    expect(screen.getByText('Test Card 2')).toBeInTheDocument();
  });

  it('handles empty state', async () => {
    server.use(
      rest.get('*/api/cards', (req, res, ctx) => {
        return res(ctx.json({ cards: [], hasMore: false }));
      })
    );

    render(<CardList />, { wrapper: AllTheProviders });

    await waitFor(() => {
      expect(screen.getByText('저장된 카드가 없습니다')).toBeInTheDocument();
    });
  });
});
```

## E2E 테스트 전략

### 1. Playwright 설정
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  
  use: {
    baseURL: 'http://localhost:5173',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
  },
});
```

### 2. 핵심 사용자 플로우 테스트
```typescript
// e2e/card-management.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Card Management Flow', () => {
  test.beforeEach(async ({ page }) => {
    // 로그인
    await page.goto('/auth/login');
    await page.fill('[data-testid="email-input"]', 'test@example.com');
    await page.click('[data-testid="login-button"]');
    
    // 인증 코드 입력 (테스트 환경)
    await page.fill('[data-testid="verification-code"]', '123456');
    await page.click('[data-testid="verify-button"]');
    
    await expect(page).toHaveURL('/cards');
  });

  test('creates a new card', async ({ page }) => {
    // 카드 생성 페이지로 이동
    await page.click('[data-testid="create-card-button"]');
    await expect(page).toHaveURL('/cards/create');

    // 폼 작성
    await page.fill('[data-testid="youtube-url-input"]', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    await page.selectOption('[data-testid="category-select"]', 'music');
    await page.fill('[data-testid="memo-input"]', 'Test memo');

    // 카드 생성
    await page.click('[data-testid="create-button"]');

    // 성공 알림 확인
    await expect(page.locator('[role="alert"]')).toContainText('카드가 생성되었습니다');

    // 카드 목록으로 리다이렉트
    await expect(page).toHaveURL('/cards');
    
    // 새 카드 확인
    await expect(page.locator('[data-testid="card-item"]').first()).toContainText('Test memo');
  });

  test('toggles favorite status', async ({ page }) => {
    // 첫 번째 카드의 즐겨찾기 버튼 클릭
    const favoriteButton = page.locator('[data-testid="favorite-button"]').first();
    await favoriteButton.click();

    // 즐겨찾기 상태 확인
    await expect(favoriteButton).toHaveAttribute('aria-pressed', 'true');
    
    // 즐겨찾기 페이지에서 확인
    await page.click('[data-testid="favorites-link"]');
    await expect(page).toHaveURL('/cards/favorites');
    await expect(page.locator('[data-testid="card-item"]')).toHaveCount(1);
  });

  test('searches cards', async ({ page }) => {
    // 검색어 입력
    await page.fill('[data-testid="search-input"]', 'test');
    
    // 검색 결과 확인
    await expect(page.locator('[data-testid="card-item"]')).toHaveCount(2);
    
    // 검색어 지우기
    await page.fill('[data-testid="search-input"]', '');
    
    // 전체 카드 표시 확인
    await expect(page.locator('[data-testid="card-item"]')).toHaveCount(5);
  });
});
```

### 3. 접근성 테스트
```typescript
// e2e/accessibility.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility Tests', () => {
  test('should not have any automatically detectable accessibility issues', async ({ page }) => {
    await page.goto('/');
    
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('keyboard navigation works', async ({ page }) => {
    await page.goto('/cards');
    
    // Tab으로 네비게이션
    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toHaveAttribute('data-testid', 'search-input');
    
    await page.keyboard.press('Tab');
    await expect(page.locator(':focus')).toHaveAttribute('data-testid', 'create-card-button');
    
    // Enter로 버튼 클릭
    await page.keyboard.press('Enter');
    await expect(page).toHaveURL('/cards/create');
  });

  test('screen reader announcements', async ({ page }) => {
    await page.goto('/cards');
    
    // 카드 생성 후 알림 확인
    await page.click('[data-testid="create-card-button"]');
    // ... 카드 생성 과정
    
    const alert = page.locator('[role="alert"]');
    await expect(alert).toBeVisible();
    await expect(alert).toHaveAttribute('aria-live', 'polite');
  });
});
```

## 테스트 유틸리티

### 1. 커스텀 렌더 함수
```typescript
// tests/utils/test-utils.tsx
import { render, RenderOptions } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '@/app/providers/AuthProvider';

const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return (
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          {children}
        </AuthProvider>
      </QueryClientProvider>
    </BrowserRouter>
  );
};

const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

export * from '@testing-library/react';
export { customRender as render };
```

### 2. 테스트 데이터 팩토리
```typescript
// tests/factories/cardFactory.ts
import { faker } from '@faker-js/faker';
import { Card } from '@/shared/types';

export const createMockCard = (overrides?: Partial<Card>): Card => ({
  id: faker.string.uuid(),
  title: faker.lorem.sentence(),
  thumbnail: faker.image.url(),
  script: faker.lorem.paragraphs(3),
  summary: faker.lorem.paragraph(),
  tags: faker.lorem.words(3).split(' '),
  memo: faker.lorem.sentence(),
  category: {
    id: faker.string.uuid(),
    name: faker.lorem.word(),
  },
  is_favorite: faker.datatype.boolean(),
  favorited_at: faker.date.recent().toISOString(),
  is_public: false,
  status: 'COMPLETED',
  created_at: faker.date.recent().toISOString(),
  updated_at: faker.date.recent().toISOString(),
  ...overrides,
});

export const createMockCards = (count: number): Card[] =>
  Array.from({ length: count }, () => createMockCard());
```

이 테스트 전략은 높은 품질과 안정성을 보장하며, 지속적인 개발과 리팩토링을 지원합니다.
