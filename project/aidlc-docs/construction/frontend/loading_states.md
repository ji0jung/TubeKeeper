# 로딩 상태 관리 시스템 (US-014)

## 로딩 상태 분류

### 1. 즉시 로딩 (0-3초)
**사용 사례**: 로그인, 간단한 API 호출, 페이지 전환
**UI 컴포넌트**: 스피너 (Spinner)
```typescript
interface SpinnerProps {
  size: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'neutral';
  className?: string;
}
```

### 2. 진행률 로딩 (3초 이상)
**사용 사례**: AI 요약 생성, 대용량 검색, 파일 업로드
**UI 컴포넌트**: 진행률 바 + 예상 시간
```typescript
interface ProgressBarProps {
  progress: number; // 0-100
  estimatedTime?: string; // "약 30초 남음"
  message?: string; // "AI 요약 생성 중..."
  onCancel?: () => void;
}
```

### 3. 스켈레톤 로딩 (콘텐츠 구조 표시)
**사용 사례**: 카드 목록, 검색 결과, 페이지 초기 로드
**UI 컴포넌트**: 스켈레톤 UI
```typescript
interface SkeletonProps {
  variant: 'card' | 'list' | 'text' | 'avatar';
  count?: number;
  className?: string;
}
```

## 로딩 컴포넌트 설계

### Spinner 컴포넌트
```typescript
// shared/components/ui/Spinner/Spinner.tsx
export const Spinner: React.FC<SpinnerProps> = ({ 
  size = 'md', 
  color = 'primary',
  className 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6', 
    lg: 'w-8 h-8'
  };

  const colorClasses = {
    primary: 'text-primary-500',
    neutral: 'text-neutral-500'
  };

  return (
    <div 
      className={`animate-spin ${sizeClasses[size]} ${colorClasses[color]} ${className}`}
      role="status"
      aria-label="로딩 중"
    >
      <svg className="w-full h-full" viewBox="0 0 24 24">
        {/* SVG 스피너 패스 */}
      </svg>
    </div>
  );
};
```

### ProgressBar 컴포넌트
```typescript
// shared/components/ui/ProgressBar/ProgressBar.tsx
export const ProgressBar: React.FC<ProgressBarProps> = ({
  progress,
  estimatedTime,
  message,
  onCancel
}) => {
  return (
    <div className="w-full max-w-md mx-auto p-6">
      {/* 메시지 */}
      {message && (
        <p className="text-sm text-neutral-600 mb-2">{message}</p>
      )}
      
      {/* 진행률 바 */}
      <div className="w-full bg-neutral-200 rounded-full h-2 mb-2">
        <div 
          className="bg-primary-500 h-2 rounded-full transition-all duration-300"
          style={{ width: `${progress}%` }}
          role="progressbar"
          aria-valuenow={progress}
          aria-valuemin={0}
          aria-valuemax={100}
        />
      </div>
      
      {/* 진행률 텍스트 */}
      <div className="flex justify-between text-xs text-neutral-500">
        <span>{progress}%</span>
        {estimatedTime && <span>{estimatedTime}</span>}
      </div>
      
      {/* 취소 버튼 */}
      {onCancel && (
        <button 
          onClick={onCancel}
          className="mt-4 text-sm text-neutral-500 hover:text-neutral-700"
        >
          취소
        </button>
      )}
    </div>
  );
};
```

### Skeleton 컴포넌트
```typescript
// shared/components/ui/Skeleton/Skeleton.tsx
export const Skeleton: React.FC<SkeletonProps> = ({ 
  variant, 
  count = 1,
  className 
}) => {
  const variants = {
    card: 'h-48 rounded-lg',
    list: 'h-16 rounded',
    text: 'h-4 rounded',
    avatar: 'w-10 h-10 rounded-full'
  };

  return (
    <>
      {Array.from({ length: count }).map((_, index) => (
        <div
          key={index}
          className={`
            animate-pulse bg-neutral-200 
            ${variants[variant]} 
            ${className}
          `}
          role="status"
          aria-label="콘텐츠 로딩 중"
        />
      ))}
    </>
  );
};
```

## 로딩 상태 훅 설계

### useLoadingState 훅
```typescript
// shared/hooks/useLoadingState.ts
interface LoadingState {
  isLoading: boolean;
  progress?: number;
  message?: string;
  estimatedTime?: string;
  error?: string;
}

export const useLoadingState = () => {
  const [state, setState] = useState<LoadingState>({
    isLoading: false
  });

  const startLoading = (message?: string) => {
    setState({ isLoading: true, message, progress: 0 });
  };

  const updateProgress = (progress: number, estimatedTime?: string) => {
    setState(prev => ({ ...prev, progress, estimatedTime }));
  };

  const finishLoading = () => {
    setState({ isLoading: false });
  };

  const setError = (error: string) => {
    setState({ isLoading: false, error });
  };

  return {
    ...state,
    startLoading,
    updateProgress, 
    finishLoading,
    setError
  };
};
```

### useProgressEstimation 훅
```typescript
// shared/hooks/useProgressEstimation.ts
export const useProgressEstimation = (
  estimatedDuration: number // 예상 소요 시간 (초)
) => {
  const [progress, setProgress] = useState(0);
  const [timeRemaining, setTimeRemaining] = useState(estimatedDuration);

  useEffect(() => {
    if (progress >= 100) return;

    const interval = setInterval(() => {
      setProgress(prev => {
        const increment = 100 / (estimatedDuration * 10); // 0.1초마다 업데이트
        const newProgress = Math.min(prev + increment, 95); // 95%까지만
        
        const remaining = Math.ceil((100 - newProgress) / 100 * estimatedDuration);
        setTimeRemaining(remaining);
        
        return newProgress;
      });
    }, 100);

    return () => clearInterval(interval);
  }, [estimatedDuration, progress]);

  const complete = () => {
    setProgress(100);
    setTimeRemaining(0);
  };

  return {
    progress,
    timeRemaining: timeRemaining > 0 ? `약 ${timeRemaining}초 남음` : null,
    complete
  };
};
```

## API별 로딩 전략

### 1. 카드 생성 (AI 요약 포함)
```typescript
// features/cards/hooks/useCardCreation.ts
export const useCardCreation = () => {
  const { startLoading, updateProgress, finishLoading } = useLoadingState();
  const { progress, timeRemaining, complete } = useProgressEstimation(45); // 45초 예상

  const createCard = async (data: CardCreateData) => {
    try {
      // 1단계: 즉시 로딩 (메타데이터 추출)
      startLoading('YouTube 정보를 가져오는 중...');
      
      const card = await cardApi.create(data);
      
      // 2단계: AI 요약 생성 (3초 후 진행률 표시)
      if (card.status === 'SUMMARY_GENERATING') {
        setTimeout(() => {
          startLoading('AI 요약을 생성하는 중...');
        }, 3000);
        
        // 폴링으로 상태 확인
        const pollStatus = setInterval(async () => {
          const updated = await cardApi.getById(card.id);
          
          if (updated.status === 'COMPLETED') {
            complete();
            finishLoading();
            clearInterval(pollStatus);
          }
        }, 2000);
      }
      
    } catch (error) {
      setError('카드 생성에 실패했습니다.');
    }
  };

  return {
    createCard,
    isLoading,
    progress: progress > 0 ? progress : undefined,
    timeRemaining
  };
};
```

### 2. 검색 결과 로딩
```typescript
// features/search/hooks/useSearch.ts
export const useSearch = () => {
  const [isLoading, setIsLoading] = useState(false);
  
  const search = async (query: string) => {
    setIsLoading(true);
    
    try {
      // 디바운스된 검색
      await new Promise(resolve => setTimeout(resolve, 300));
      const results = await searchApi.search(query);
      return results;
    } finally {
      setIsLoading(false);
    }
  };

  return { search, isLoading };
};
```

### 3. 무한 스크롤 로딩
```typescript
// shared/hooks/useInfiniteScroll.ts
export const useInfiniteScroll = <T>(
  fetchFn: (cursor?: string) => Promise<{ data: T[]; nextCursor?: string }>
) => {
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  
  const loadMore = async () => {
    setIsLoadingMore(true);
    try {
      // 추가 데이터 로드
    } finally {
      setIsLoadingMore(false);
    }
  };

  return {
    isLoading,
    isLoadingMore,
    loadMore
  };
};
```

## 에러 상태 처리

### ErrorState 컴포넌트
```typescript
// shared/components/feedback/ErrorState.tsx
interface ErrorStateProps {
  title: string;
  message: string;
  onRetry?: () => void;
  onCancel?: () => void;
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title,
  message,
  onRetry,
  onCancel
}) => {
  return (
    <div className="text-center p-6">
      <div className="text-error-500 mb-4">
        {/* 에러 아이콘 */}
      </div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-neutral-600 mb-4">{message}</p>
      
      <div className="flex gap-2 justify-center">
        {onRetry && (
          <button 
            onClick={onRetry}
            className="px-4 py-2 bg-primary-500 text-white rounded"
          >
            다시 시도
          </button>
        )}
        {onCancel && (
          <button 
            onClick={onCancel}
            className="px-4 py-2 bg-neutral-200 text-neutral-700 rounded"
          >
            취소
          </button>
        )}
      </div>
    </div>
  );
};
```

## 성능 최적화

### 1. 로딩 상태 최적화
- **디바운싱**: 검색 입력 시 불필요한 API 호출 방지
- **메모이제이션**: 로딩 컴포넌트 리렌더링 최소화
- **가상화**: 긴 목록의 스켈레톤 UI 최적화

### 2. 사용자 경험 최적화
- **낙관적 업데이트**: 즉시 UI 업데이트 후 서버 동기화
- **백그라운드 로딩**: 사용자가 인지하지 못하는 사전 로딩
- **점진적 로딩**: 중요한 콘텐츠부터 우선 표시

## 접근성 고려사항

### ARIA 속성
```typescript
// 로딩 상태 접근성
<div 
  role="status" 
  aria-live="polite"
  aria-label="콘텐츠 로딩 중"
>
  <Spinner />
</div>

// 진행률 접근성
<div
  role="progressbar"
  aria-valuenow={progress}
  aria-valuemin={0}
  aria-valuemax={100}
  aria-label={`진행률 ${progress}%`}
>
```

### 스크린 리더 지원
- **상태 변경 알림**: aria-live로 로딩 상태 변경 알림
- **대체 텍스트**: 시각적 로딩 표시의 텍스트 대안 제공
- **키보드 접근**: 취소 버튼 등 키보드로 접근 가능

이 로딩 상태 관리 시스템은 US-014 요구사항을 충족하며, 사용자에게 명확한 피드백을 제공합니다.
