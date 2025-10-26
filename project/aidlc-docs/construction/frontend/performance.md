# 성능 최적화 가이드

## 코드 스플리팅 전략

### 1. 라우트 기반 스플리팅
```typescript
// app/router/lazyRoutes.tsx
import { lazy } from 'react';

// 페이지별 lazy loading
export const HomePage = lazy(() => import('@/pages/HomePage'));
export const LoginPage = lazy(() => import('@/features/auth/pages/LoginPage'));
export const CardListPage = lazy(() => import('@/features/cards/pages/CardListPage'));
export const CardDetailPage = lazy(() => import('@/features/cards/pages/CardDetailPage'));
export const SearchPage = lazy(() => import('@/features/search/pages/SearchPage'));

// 기능별 청크 분리
export const CardForm = lazy(() => import('@/features/cards/components/CardForm'));
export const CategoryManager = lazy(() => import('@/features/categories/components/CategoryManager'));
```

### 2. 동적 임포트 최적화
```typescript
// shared/utils/dynamicImport.ts
export const loadComponent = <T extends React.ComponentType<any>>(
  importFn: () => Promise<{ default: T }>,
  fallback?: React.ComponentType
) => {
  return lazy(async () => {
    try {
      const module = await importFn();
      return module;
    } catch (error) {
      console.error('Component loading failed:', error);
      return { default: fallback || (() => <div>컴포넌트 로딩 실패</div>) };
    }
  });
};

// 사용 예시
const HeavyChart = loadComponent(
  () => import('@/components/charts/HeavyChart'),
  () => <div>차트를 불러올 수 없습니다</div>
);
```

### 3. 번들 분석 및 최적화
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          // 벤더 라이브러리 분리
          vendor: ['react', 'react-dom'],
          ui: ['@headlessui/react', '@heroicons/react'],
          query: ['@tanstack/react-query'],
          router: ['react-router-dom'],
          
          // 기능별 청크
          auth: ['./src/features/auth'],
          cards: ['./src/features/cards'],
          search: ['./src/features/search'],
        },
      },
    },
  },
  plugins: [
    visualizer({
      filename: 'dist/stats.html',
      open: true,
      gzipSize: true,
    }),
  ],
});
```

## 이미지 최적화

### 1. 반응형 이미지 컴포넌트
```typescript
// shared/components/ui/OptimizedImage.tsx
interface OptimizedImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  className?: string;
  loading?: 'lazy' | 'eager';
  sizes?: string;
}

export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  width,
  height,
  className,
  loading = 'lazy',
  sizes = '(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw'
}) => {
  const [imageError, setImageError] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // WebP 지원 확인
  const supportsWebP = useMemo(() => {
    const canvas = document.createElement('canvas');
    return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
  }, []);

  // 이미지 URL 최적화
  const getOptimizedSrc = (originalSrc: string, targetWidth?: number) => {
    // YouTube 썸네일 최적화
    if (originalSrc.includes('youtube.com') || originalSrc.includes('ytimg.com')) {
      if (targetWidth && targetWidth <= 320) {
        return originalSrc.replace(/maxresdefault|hqdefault/, 'mqdefault');
      }
      return originalSrc;
    }

    // 일반 이미지 최적화 (CDN 사용 시)
    if (targetWidth && originalSrc.includes('your-cdn.com')) {
      const format = supportsWebP ? 'webp' : 'jpg';
      return `${originalSrc}?w=${targetWidth}&f=${format}&q=80`;
    }

    return originalSrc;
  };

  const handleLoad = () => {
    setIsLoading(false);
  };

  const handleError = () => {
    setImageError(true);
    setIsLoading(false);
  };

  if (imageError) {
    return (
      <div 
        className={`bg-neutral-200 flex items-center justify-center ${className}`}
        style={{ width, height }}
      >
        <PhotoIcon className="w-8 h-8 text-neutral-400" />
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      {isLoading && (
        <div 
          className="absolute inset-0 bg-neutral-200 animate-pulse"
          style={{ width, height }}
        />
      )}
      
      <img
        src={getOptimizedSrc(src, width)}
        alt={alt}
        width={width}
        height={height}
        loading={loading}
        sizes={sizes}
        onLoad={handleLoad}
        onError={handleError}
        className={`${isLoading ? 'opacity-0' : 'opacity-100'} transition-opacity duration-300`}
      />
    </div>
  );
};
```

### 2. 이미지 프리로딩
```typescript
// shared/hooks/useImagePreload.ts
export const useImagePreload = (urls: string[]) => {
  const [loadedImages, setLoadedImages] = useState<Set<string>>(new Set());

  useEffect(() => {
    const preloadImage = (url: string) => {
      return new Promise<void>((resolve, reject) => {
        const img = new Image();
        img.onload = () => {
          setLoadedImages(prev => new Set(prev).add(url));
          resolve();
        };
        img.onerror = reject;
        img.src = url;
      });
    };

    // 중요한 이미지들만 프리로드 (첫 3개)
    const priorityUrls = urls.slice(0, 3);
    
    Promise.allSettled(priorityUrls.map(preloadImage));
  }, [urls]);

  return {
    isImageLoaded: (url: string) => loadedImages.has(url),
    loadedCount: loadedImages.size,
  };
};
```

## 메모이제이션 전략

### 1. 컴포넌트 메모이제이션
```typescript
// features/cards/components/CardItem.tsx
interface CardItemProps {
  card: Card;
  onClick?: () => void;
  onFavoriteToggle?: () => void;
}

export const CardItem = memo<CardItemProps>(({
  card,
  onClick,
  onFavoriteToggle
}) => {
  // 비용이 큰 계산 메모이제이션
  const formattedDate = useMemo(() => {
    return formatDistanceToNow(new Date(card.created_at), { 
      addSuffix: true,
      locale: ko 
    });
  }, [card.created_at]);

  // 태그 렌더링 메모이제이션
  const tagElements = useMemo(() => {
    return card.tags?.slice(0, 3).map(tag => (
      <span key={tag} className="tag-style">
        #{tag}
      </span>
    ));
  }, [card.tags]);

  // 이벤트 핸들러 메모이제이션
  const handleFavoriteClick = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    onFavoriteToggle?.();
  }, [onFavoriteToggle]);

  return (
    <div className="card" onClick={onClick}>
      <OptimizedImage
        src={card.thumbnail}
        alt={card.title}
        width={300}
        height={169}
        loading="lazy"
      />
      
      <div className="card-content">
        <h3>{card.title}</h3>
        <p>{card.summary}</p>
        <div className="tags">{tagElements}</div>
        <div className="meta">
          <span>{card.category?.name}</span>
          <span>{formattedDate}</span>
        </div>
        
        <button onClick={handleFavoriteClick}>
          <StarIcon className={card.is_favorite ? 'filled' : 'outline'} />
        </button>
      </div>
    </div>
  );
}, (prevProps, nextProps) => {
  // 커스텀 비교 함수
  return (
    prevProps.card.id === nextProps.card.id &&
    prevProps.card.is_favorite === nextProps.card.is_favorite &&
    prevProps.card.updated_at === nextProps.card.updated_at
  );
});
```

### 2. 검색 결과 메모이제이션
```typescript
// features/search/hooks/useSearchResults.ts
export const useSearchResults = (query: string, filters: SearchFilters) => {
  // 검색 파라미터 메모이제이션
  const searchParams = useMemo(() => ({
    query: query.trim(),
    categoryId: filters.category,
    tags: filters.tags,
    sortBy: filters.sortBy,
  }), [query, filters.category, filters.tags, filters.sortBy]);

  // 디바운스된 검색어
  const debouncedQuery = useDebounce(searchParams.query, 300);

  // 검색 결과 쿼리
  const searchResults = useQuery({
    queryKey: ['search', debouncedQuery, searchParams],
    queryFn: () => searchApi.searchMyCards({
      ...searchParams,
      query: debouncedQuery,
    }),
    enabled: debouncedQuery.length > 0,
    staleTime: 30 * 1000, // 30초간 fresh
  });

  // 필터링된 결과 메모이제이션
  const filteredResults = useMemo(() => {
    if (!searchResults.data?.cards) return [];

    return searchResults.data.cards.filter(card => {
      if (filters.dateRange) {
        const cardDate = new Date(card.created_at);
        const { start, end } = filters.dateRange;
        if (cardDate < start || cardDate > end) return false;
      }
      return true;
    });
  }, [searchResults.data?.cards, filters.dateRange]);

  return {
    results: filteredResults,
    isLoading: searchResults.isLoading,
    error: searchResults.error,
  };
};
```

## 번들 크기 최적화

### 1. Tree Shaking 최적화
```typescript
// shared/utils/lodash.ts - 필요한 함수만 임포트
export { debounce } from 'lodash-es/debounce';
export { throttle } from 'lodash-es/throttle';
export { uniqBy } from 'lodash-es/uniqBy';

// 대신 이렇게 사용하지 말 것
// import _ from 'lodash'; // 전체 라이브러리 임포트
```

### 2. 조건부 로딩
```typescript
// shared/components/ConditionalLoader.tsx
interface ConditionalLoaderProps {
  condition: boolean;
  loader: () => Promise<{ default: React.ComponentType<any> }>;
  fallback?: React.ComponentType;
  children?: React.ReactNode;
}

export const ConditionalLoader: React.FC<ConditionalLoaderProps> = ({
  condition,
  loader,
  fallback: Fallback,
  children
}) => {
  const [Component, setComponent] = useState<React.ComponentType | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (condition && !Component) {
      setLoading(true);
      loader()
        .then(module => {
          setComponent(() => module.default);
        })
        .catch(error => {
          console.error('Dynamic import failed:', error);
          if (Fallback) {
            setComponent(() => Fallback);
          }
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [condition, Component, loader, Fallback]);

  if (!condition) {
    return <>{children}</>;
  }

  if (loading) {
    return <Spinner />;
  }

  if (Component) {
    return <Component />;
  }

  return Fallback ? <Fallback /> : null;
};

// 사용 예시
const AdminPanel = () => (
  <ConditionalLoader
    condition={user?.role === 'admin'}
    loader={() => import('@/features/admin/AdminDashboard')}
    fallback={() => <div>관리자 권한이 필요합니다</div>}
  />
);
```

### 3. 폰트 최적화
```css
/* styles/fonts.css */
@font-face {
  font-family: 'Pretendard';
  font-weight: 400;
  font-style: normal;
  font-display: swap; /* 폰트 로딩 최적화 */
  src: url('/fonts/Pretendard-Regular.woff2') format('woff2'),
       url('/fonts/Pretendard-Regular.woff') format('woff');
}

@font-face {
  font-family: 'Pretendard';
  font-weight: 600;
  font-style: normal;
  font-display: swap;
  src: url('/fonts/Pretendard-SemiBold.woff2') format('woff2'),
       url('/fonts/Pretendard-SemiBold.woff') format('woff');
}

/* 필요한 폰트 웨이트만 로드 */
```

## 렌더링 최적화

### 1. 가상화 (Virtualization)
```typescript
// shared/components/VirtualizedList.tsx
import { FixedSizeList as List } from 'react-window';

interface VirtualizedListProps<T> {
  items: T[];
  itemHeight: number;
  renderItem: (props: { index: number; style: React.CSSProperties; data: T }) => React.ReactNode;
  height: number;
  className?: string;
}

export const VirtualizedList = <T,>({
  items,
  itemHeight,
  renderItem,
  height,
  className
}: VirtualizedListProps<T>) => {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      {renderItem({ index, style, data: items[index] })}
    </div>
  );

  return (
    <List
      className={className}
      height={height}
      itemCount={items.length}
      itemSize={itemHeight}
      itemData={items}
    >
      {Row}
    </List>
  );
};

// 사용 예시 - 대량의 카드 목록
const LargeCardList: React.FC<{ cards: Card[] }> = ({ cards }) => (
  <VirtualizedList
    items={cards}
    itemHeight={200}
    height={600}
    renderItem={({ data: card }) => (
      <CardItem key={card.id} card={card} />
    )}
  />
);
```

### 2. 무한 스크롤 최적화
```typescript
// shared/hooks/useInfiniteScroll.ts
export const useInfiniteScroll = <T>(
  fetchFn: (cursor?: string) => Promise<{ data: T[]; nextCursor?: string; hasMore: boolean }>,
  options: {
    threshold?: number;
    rootMargin?: string;
  } = {}
) => {
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [cursor, setCursor] = useState<string>();

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;

    setLoading(true);
    try {
      const result = await fetchFn(cursor);
      
      setData(prev => [...prev, ...result.data]);
      setCursor(result.nextCursor);
      setHasMore(result.hasMore);
    } catch (error) {
      console.error('Failed to load more:', error);
    } finally {
      setLoading(false);
    }
  }, [fetchFn, cursor, loading, hasMore]);

  // Intersection Observer로 자동 로딩
  const observerRef = useRef<IntersectionObserver>();
  const lastElementRef = useCallback((node: HTMLElement | null) => {
    if (loading) return;
    if (observerRef.current) observerRef.current.disconnect();
    
    observerRef.current = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && hasMore) {
          loadMore();
        }
      },
      {
        threshold: options.threshold || 0.1,
        rootMargin: options.rootMargin || '100px',
      }
    );
    
    if (node) observerRef.current.observe(node);
  }, [loading, hasMore, loadMore, options.threshold, options.rootMargin]);

  return {
    data,
    loading,
    hasMore,
    loadMore,
    lastElementRef,
  };
};
```

## 캐싱 전략

### 1. 브라우저 캐싱
```typescript
// shared/services/cache/browserCache.ts
class BrowserCache {
  private cache = new Map<string, { data: any; expiry: number }>();

  set(key: string, data: any, ttl: number = 5 * 60 * 1000) {
    this.cache.set(key, {
      data,
      expiry: Date.now() + ttl,
    });
  }

  get(key: string) {
    const item = this.cache.get(key);
    if (!item) return null;

    if (Date.now() > item.expiry) {
      this.cache.delete(key);
      return null;
    }

    return item.data;
  }

  clear() {
    this.cache.clear();
  }

  // 메모리 사용량 제한
  private cleanup() {
    if (this.cache.size > 100) {
      const entries = Array.from(this.cache.entries());
      entries.sort((a, b) => a[1].expiry - b[1].expiry);
      
      // 오래된 항목 50개 제거
      entries.slice(0, 50).forEach(([key]) => {
        this.cache.delete(key);
      });
    }
  }
}

export const browserCache = new BrowserCache();
```

### 2. Service Worker 캐싱 (선택사항)
```typescript
// public/sw.js
const CACHE_NAME = 'youtube-app-v1';
const STATIC_ASSETS = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/fonts/Pretendard-Regular.woff2',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
  );
});

self.addEventListener('fetch', (event) => {
  // 이미지 캐싱
  if (event.request.destination === 'image') {
    event.respondWith(
      caches.match(event.request)
        .then(response => {
          if (response) return response;
          
          return fetch(event.request)
            .then(response => {
              const responseClone = response.clone();
              caches.open(CACHE_NAME)
                .then(cache => cache.put(event.request, responseClone));
              return response;
            });
        })
    );
  }
});
```

이 성능 최적화 전략은 초기 로딩 시간 단축, 런타임 성능 향상, 메모리 사용량 최적화를 통해 전반적인 사용자 경험을 개선합니다.
