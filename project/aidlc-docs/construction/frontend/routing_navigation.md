# 라우팅 및 네비게이션 설계

## 라우트 구조

### 1. 전체 라우트 맵
```
/ (홈페이지)
├── /auth
│   ├── /login (로그인)
│   ├── /register (회원가입)
│   └── /verify (인증 코드 확인)
├── /cards (인증 필요)
│   ├── / (내 카드 목록)
│   ├── /create (카드 생성)
│   ├── /favorites (즐겨찾기)
│   └── /:id (카드 상세)
├── /search
│   ├── / (검색 페이지)
│   └── /public (공개 카드 검색)
├── /categories (인증 필요)
│   └── / (카테고리 관리)
├── /profile (인증 필요)
│   └── / (프로필 설정)
├── /shared
│   └── /:shareId (공유 카드 조회)
└── /404 (페이지 없음)
```

### 2. 라우터 설정
```typescript
// app/router/routes.tsx
import { createBrowserRouter } from 'react-router-dom';
import { ProtectedRoute } from './ProtectedRoute';
import { PublicRoute } from './PublicRoute';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    errorElement: <ErrorPage />,
    children: [
      // 홈페이지
      {
        index: true,
        element: <HomePage />
      },

      // 인증 라우트 (로그인 상태에서 접근 불가)
      {
        path: 'auth',
        element: <PublicRoute />,
        children: [
          {
            path: 'login',
            element: <LoginPage />
          },
          {
            path: 'register', 
            element: <RegisterPage />
          },
          {
            path: 'verify',
            element: <VerifyPage />
          }
        ]
      },

      // 보호된 라우트 (인증 필요)
      {
        path: 'cards',
        element: <ProtectedRoute />,
        children: [
          {
            index: true,
            element: <CardListPage />
          },
          {
            path: 'create',
            element: <CardCreatePage />
          },
          {
            path: 'favorites',
            element: <FavoritesPage />
          },
          {
            path: ':id',
            element: <CardDetailPage />
          }
        ]
      },

      // 검색 라우트 (공개)
      {
        path: 'search',
        children: [
          {
            index: true,
            element: <SearchPage />
          },
          {
            path: 'public',
            element: <PublicSearchPage />
          }
        ]
      },

      // 카테고리 관리 (인증 필요)
      {
        path: 'categories',
        element: <ProtectedRoute />,
        children: [
          {
            index: true,
            element: <CategoriesPage />
          }
        ]
      },

      // 프로필 (인증 필요)
      {
        path: 'profile',
        element: <ProtectedRoute />,
        children: [
          {
            index: true,
            element: <ProfilePage />
          }
        ]
      },

      // 공유 카드 (공개)
      {
        path: 'shared/:shareId',
        element: <SharedCardPage />
      },

      // 404 페이지
      {
        path: '*',
        element: <NotFoundPage />
      }
    ]
  }
]);
```

## 인증 가드 설계

### 1. ProtectedRoute 컴포넌트
```typescript
// app/router/ProtectedRoute.tsx
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/app/store/authStore';
import { LoadingSpinner } from '@/shared/components';

export const ProtectedRoute: React.FC = () => {
  const { isAuthenticated, checkSession } = useAuthStore();
  const location = useLocation();

  // 세션 유효성 검사
  if (isAuthenticated && !checkSession()) {
    useAuthStore.getState().logout();
    return <Navigate to="/auth/login" state={{ from: location }} replace />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
};
```

### 2. PublicRoute 컴포넌트
```typescript
// app/router/PublicRoute.tsx
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/app/store/authStore';

export const PublicRoute: React.FC = () => {
  const { isAuthenticated } = useAuthStore();

  // 이미 로그인된 사용자는 홈으로 리다이렉트
  if (isAuthenticated) {
    return <Navigate to="/cards" replace />;
  }

  return <Outlet />;
};
```

### 3. 권한별 접근 제어
```typescript
// shared/hooks/usePermissions.ts
export const usePermissions = () => {
  const { user } = useAuthStore();

  const canCreateCard = () => {
    return !!user; // 로그인한 사용자만
  };

  const canEditCard = (card: Card) => {
    return user?.id === card.user_id;
  };

  const canDeleteCard = (card: Card) => {
    return user?.id === card.user_id;
  };

  const canManageCategories = () => {
    return !!user;
  };

  return {
    canCreateCard,
    canEditCard,
    canDeleteCard,
    canManageCategories
  };
};
```

## 네비게이션 컴포넌트

### 1. 메인 네비게이션
```typescript
// shared/components/navigation/MainNavigation.tsx
interface NavigationItem {
  label: string;
  path: string;
  icon: React.ComponentType<{ className?: string }>;
  requireAuth?: boolean;
  badge?: number;
}

const navigationItems: NavigationItem[] = [
  {
    label: '내 카드',
    path: '/cards',
    icon: RectangleStackIcon,
    requireAuth: true
  },
  {
    label: '즐겨찾기',
    path: '/cards/favorites',
    icon: StarIcon,
    requireAuth: true
  },
  {
    label: '검색',
    path: '/search',
    icon: MagnifyingGlassIcon
  },
  {
    label: '공개 카드',
    path: '/search/public',
    icon: GlobeAltIcon
  },
  {
    label: '카테고리',
    path: '/categories',
    icon: FolderIcon,
    requireAuth: true
  }
];

export const MainNavigation: React.FC = () => {
  const { isAuthenticated } = useAuthStore();
  const location = useLocation();

  const visibleItems = navigationItems.filter(item => 
    !item.requireAuth || isAuthenticated
  );

  return (
    <nav className="space-y-1">
      {visibleItems.map((item) => {
        const isActive = location.pathname === item.path || 
          (item.path !== '/' && location.pathname.startsWith(item.path));

        return (
          <Link
            key={item.path}
            to={item.path}
            className={`
              group flex items-center px-2 py-2 text-sm font-medium rounded-md
              ${isActive
                ? 'bg-primary-100 text-primary-900'
                : 'text-neutral-600 hover:bg-neutral-50 hover:text-neutral-900'
              }
            `}
          >
            <item.icon
              className={`
                mr-3 flex-shrink-0 h-6 w-6
                ${isActive ? 'text-primary-500' : 'text-neutral-400 group-hover:text-neutral-500'}
              `}
            />
            {item.label}
            {item.badge && (
              <span className="ml-auto inline-block py-0.5 px-3 text-xs rounded-full bg-neutral-100 text-neutral-600">
                {item.badge}
              </span>
            )}
          </Link>
        );
      })}
    </nav>
  );
};
```

### 2. 브레드크럼
```typescript
// shared/components/navigation/Breadcrumb.tsx
interface BreadcrumbItem {
  label: string;
  path?: string;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items }) => {
  return (
    <nav className="flex" aria-label="Breadcrumb">
      <ol className="flex items-center space-x-4">
        {items.map((item, index) => (
          <li key={index}>
            <div className="flex items-center">
              {index > 0 && (
                <ChevronRightIcon className="flex-shrink-0 h-5 w-5 text-neutral-400 mr-4" />
              )}
              {item.path ? (
                <Link
                  to={item.path}
                  className="text-sm font-medium text-neutral-500 hover:text-neutral-700"
                >
                  {item.label}
                </Link>
              ) : (
                <span className="text-sm font-medium text-neutral-900">
                  {item.label}
                </span>
              )}
            </div>
          </li>
        ))}
      </ol>
    </nav>
  );
};
```

### 3. 사용자 메뉴
```typescript
// shared/components/navigation/UserMenu.tsx
interface UserMenuProps {
  user: User;
}

export const UserMenu: React.FC<UserMenuProps> = ({ user }) => {
  const [isOpen, setIsOpen] = useState(false);
  const { logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
      >
        <img
          className="h-8 w-8 rounded-full"
          src={user.avatar || '/default-avatar.png'}
          alt={user.email}
        />
      </button>

      {isOpen && (
        <div className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5">
          <div className="py-1">
            <div className="px-4 py-2 text-sm text-neutral-700 border-b border-neutral-100">
              <p className="font-medium">{user.email}</p>
            </div>
            
            <Link
              to="/profile"
              className="block px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-100"
              onClick={() => setIsOpen(false)}
            >
              프로필 설정
            </Link>
            
            <button
              onClick={handleLogout}
              className="block w-full text-left px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-100"
            >
              로그아웃
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
```

## 페이지 타이틀 관리

### 1. useDocumentTitle 훅
```typescript
// shared/hooks/useDocumentTitle.ts
export const useDocumentTitle = (title?: string) => {
  useEffect(() => {
    const baseTitle = 'YouTube Link App';
    document.title = title ? `${title} - ${baseTitle}` : baseTitle;
    
    return () => {
      document.title = baseTitle;
    };
  }, [title]);
};
```

### 2. 페이지별 타이틀 설정
```typescript
// features/cards/pages/CardListPage.tsx
export const CardListPage: React.FC = () => {
  useDocumentTitle('내 카드');
  
  return (
    <PageLayout title="내 카드" subtitle="저장한 YouTube 링크를 관리하세요">
      <CardList />
    </PageLayout>
  );
};

// features/cards/pages/CardDetailPage.tsx
export const CardDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { data: card } = useCard(id!);
  
  useDocumentTitle(card?.title);
  
  return (
    <PageLayout>
      <CardDetail card={card} />
    </PageLayout>
  );
};
```

## 라우트 기반 코드 스플리팅

### 1. Lazy Loading 설정
```typescript
// app/router/lazyRoutes.tsx
import { lazy } from 'react';

// 페이지 컴포넌트 lazy loading
export const HomePage = lazy(() => import('@/pages/HomePage'));
export const LoginPage = lazy(() => import('@/features/auth/pages/LoginPage'));
export const RegisterPage = lazy(() => import('@/features/auth/pages/RegisterPage'));
export const CardListPage = lazy(() => import('@/features/cards/pages/CardListPage'));
export const CardDetailPage = lazy(() => import('@/features/cards/pages/CardDetailPage'));
export const SearchPage = lazy(() => import('@/features/search/pages/SearchPage'));
```

### 2. Suspense 래퍼
```typescript
// app/router/SuspenseWrapper.tsx
interface SuspenseWrapperProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export const SuspenseWrapper: React.FC<SuspenseWrapperProps> = ({ 
  children, 
  fallback 
}) => {
  const defaultFallback = (
    <div className="flex items-center justify-center min-h-screen">
      <Spinner size="lg" />
    </div>
  );

  return (
    <Suspense fallback={fallback || defaultFallback}>
      {children}
    </Suspense>
  );
};
```

## 네비게이션 상태 관리

### 1. 네비게이션 히스토리
```typescript
// shared/hooks/useNavigationHistory.ts
export const useNavigationHistory = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const goBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
    } else {
      navigate('/');
    }
  };

  const goToWithState = (path: string, state?: any) => {
    navigate(path, { state });
  };

  const isFromRoute = (routePath: string) => {
    return location.state?.from?.pathname === routePath;
  };

  return {
    goBack,
    goToWithState,
    isFromRoute,
    currentPath: location.pathname
  };
};
```

### 2. 활성 라우트 감지
```typescript
// shared/hooks/useActiveRoute.ts
export const useActiveRoute = () => {
  const location = useLocation();

  const isActive = (path: string, exact = false) => {
    if (exact) {
      return location.pathname === path;
    }
    return location.pathname.startsWith(path);
  };

  const getActiveSection = () => {
    const path = location.pathname;
    if (path.startsWith('/cards')) return 'cards';
    if (path.startsWith('/search')) return 'search';
    if (path.startsWith('/categories')) return 'categories';
    if (path.startsWith('/profile')) return 'profile';
    if (path.startsWith('/auth')) return 'auth';
    return 'home';
  };

  return {
    isActive,
    getActiveSection,
    currentPath: location.pathname
  };
};
```

이 라우팅 시스템은 인증 기반 접근 제어, 코드 스플리팅, 사용자 친화적 네비게이션을 제공합니다.
