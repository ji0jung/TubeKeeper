# 상태 관리 설계

## 상태 분류 및 전략

### 1. 클라이언트 상태 (Zustand)
- **사용자 설정**: 언어, 테마, 레이아웃 설정
- **UI 상태**: 모달, 사이드바, 알림 상태
- **임시 데이터**: 폼 임시 저장, 검색 필터

### 2. 서버 상태 (React Query)
- **API 데이터**: 카드, 카테고리, 사용자 정보
- **캐싱**: 자동 캐싱 및 무효화
- **동기화**: 백그라운드 업데이트

### 3. 폼 상태 (React Hook Form)
- **폼 데이터**: 입력값, 검증, 에러
- **제출 상태**: 로딩, 성공, 실패

## Zustand 스토어 설계

### 1. Auth Store
```typescript
// app/store/authStore.ts
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  sessionExpiry: Date | null;
}

interface AuthActions {
  login: (token: string, user: User) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
  refreshSession: () => void;
  checkSession: () => boolean;
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      isAuthenticated: false,
      sessionExpiry: null,

      // Actions
      login: (token, user) => {
        const expiry = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000); // 7일
        set({
          user,
          token,
          isAuthenticated: true,
          sessionExpiry: expiry
        });
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          sessionExpiry: null
        });
      },

      updateUser: (userData) => {
        set((state) => ({
          user: state.user ? { ...state.user, ...userData } : null
        }));
      },

      refreshSession: () => {
        const expiry = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
        set({ sessionExpiry: expiry });
      },

      checkSession: () => {
        const { sessionExpiry } = get();
        if (!sessionExpiry) return false;
        return new Date() < sessionExpiry;
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
        sessionExpiry: state.sessionExpiry
      })
    }
  )
);
```

### 2. UI Store
```typescript
// app/store/uiStore.ts
interface UIState {
  sidebarOpen: boolean;
  currentModal: string | null;
  notifications: Notification[];
  theme: 'light' | 'dark';
  language: 'ko' | 'en';
}

interface UIActions {
  toggleSidebar: () => void;
  openModal: (modalId: string) => void;
  closeModal: () => void;
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setLanguage: (language: 'ko' | 'en') => void;
}

export const useUIStore = create<UIState & UIActions>()(
  persist(
    (set, get) => ({
      // State
      sidebarOpen: false,
      currentModal: null,
      notifications: [],
      theme: 'light',
      language: 'ko',

      // Actions
      toggleSidebar: () => {
        set((state) => ({ sidebarOpen: !state.sidebarOpen }));
      },

      openModal: (modalId) => {
        set({ currentModal: modalId });
      },

      closeModal: () => {
        set({ currentModal: null });
      },

      addNotification: (notification) => {
        const id = Date.now().toString();
        set((state) => ({
          notifications: [...state.notifications, { ...notification, id }]
        }));

        // 자동 제거 (5초 후)
        setTimeout(() => {
          get().removeNotification(id);
        }, 5000);
      },

      removeNotification: (id) => {
        set((state) => ({
          notifications: state.notifications.filter(n => n.id !== id)
        }));
      },

      setTheme: (theme) => {
        set({ theme });
      },

      setLanguage: (language) => {
        set({ language });
      }
    }),
    {
      name: 'ui-storage',
      partialize: (state) => ({
        theme: state.theme,
        language: state.language
      })
    }
  )
);
```

### 3. Search Store
```typescript
// app/store/searchStore.ts
interface SearchState {
  query: string;
  filters: SearchFilters;
  recentSearches: string[];
  searchHistory: SearchHistoryItem[];
}

interface SearchActions {
  setQuery: (query: string) => void;
  setFilters: (filters: Partial<SearchFilters>) => void;
  addToHistory: (query: string) => void;
  clearHistory: () => void;
  removeFromHistory: (query: string) => void;
}

export const useSearchStore = create<SearchState & SearchActions>()(
  persist(
    (set, get) => ({
      // State
      query: '',
      filters: {
        category: null,
        tags: [],
        dateRange: null,
        sortBy: 'created_at',
        sortOrder: 'desc'
      },
      recentSearches: [],
      searchHistory: [],

      // Actions
      setQuery: (query) => {
        set({ query });
      },

      setFilters: (newFilters) => {
        set((state) => ({
          filters: { ...state.filters, ...newFilters }
        }));
      },

      addToHistory: (query) => {
        if (!query.trim()) return;

        set((state) => {
          const filtered = state.recentSearches.filter(s => s !== query);
          return {
            recentSearches: [query, ...filtered].slice(0, 10), // 최대 10개
            searchHistory: [
              { query, timestamp: new Date() },
              ...state.searchHistory.filter(h => h.query !== query)
            ].slice(0, 50) // 최대 50개
          };
        });
      },

      clearHistory: () => {
        set({ recentSearches: [], searchHistory: [] });
      },

      removeFromHistory: (query) => {
        set((state) => ({
          recentSearches: state.recentSearches.filter(s => s !== query),
          searchHistory: state.searchHistory.filter(h => h.query !== query)
        }));
      }
    }),
    {
      name: 'search-storage'
    }
  )
);
```

## React Query 설정

### 1. Query Client 설정
```typescript
// app/providers/QueryProvider.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5분
      cacheTime: 10 * 60 * 1000, // 10분
      retry: (failureCount, error) => {
        // 인증 에러는 재시도 안함
        if (error?.status === 401) return false;
        return failureCount < 3;
      },
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 1,
    },
  },
});

export const QueryProvider: React.FC<{ children: React.ReactNode }> = ({ 
  children 
}) => {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
};
```

### 2. API 훅 설계

#### Cards API 훅
```typescript
// features/cards/hooks/useCards.ts
export const useCards = (params?: CardListParams) => {
  return useInfiniteQuery({
    queryKey: ['cards', params],
    queryFn: ({ pageParam }) => cardApi.getList({ ...params, cursor: pageParam }),
    getNextPageParam: (lastPage) => lastPage.nextCursor,
    enabled: !!params,
  });
};

export const useCard = (id: string) => {
  return useQuery({
    queryKey: ['card', id],
    queryFn: () => cardApi.getById(id),
    enabled: !!id,
  });
};

export const useCreateCard = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: cardApi.create,
    onSuccess: (newCard) => {
      // 카드 목록 무효화
      queryClient.invalidateQueries({ queryKey: ['cards'] });
      
      // 새 카드를 캐시에 추가
      queryClient.setQueryData(['card', newCard.id], newCard);
      
      // 성공 알림
      useUIStore.getState().addNotification({
        type: 'success',
        title: '카드가 생성되었습니다',
        message: '새로운 카드가 성공적으로 저장되었습니다.'
      });
    },
    onError: (error) => {
      useUIStore.getState().addNotification({
        type: 'error',
        title: '카드 생성 실패',
        message: error.message || '카드 생성 중 오류가 발생했습니다.'
      });
    }
  });
};

export const useUpdateCard = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Card> }) => 
      cardApi.update(id, data),
    onSuccess: (updatedCard) => {
      // 특정 카드 캐시 업데이트
      queryClient.setQueryData(['card', updatedCard.id], updatedCard);
      
      // 카드 목록에서도 업데이트
      queryClient.setQueriesData(
        { queryKey: ['cards'] },
        (oldData: any) => {
          if (!oldData) return oldData;
          
          return {
            ...oldData,
            pages: oldData.pages.map((page: any) => ({
              ...page,
              data: page.data.map((card: Card) =>
                card.id === updatedCard.id ? updatedCard : card
              )
            }))
          };
        }
      );
    }
  });
};

export const useFavoriteToggle = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: cardApi.toggleFavorite,
    onMutate: async (cardId) => {
      // 낙관적 업데이트
      await queryClient.cancelQueries({ queryKey: ['card', cardId] });
      
      const previousCard = queryClient.getQueryData(['card', cardId]);
      
      queryClient.setQueryData(['card', cardId], (old: Card) => ({
        ...old,
        is_favorite: !old.is_favorite,
        favorited_at: !old.is_favorite ? new Date().toISOString() : null
      }));
      
      return { previousCard };
    },
    onError: (err, cardId, context) => {
      // 에러 시 롤백
      queryClient.setQueryData(['card', cardId], context?.previousCard);
    },
    onSettled: (data, error, cardId) => {
      // 최종 동기화
      queryClient.invalidateQueries({ queryKey: ['card', cardId] });
    }
  });
};
```

#### Categories API 훅
```typescript
// features/categories/hooks/useCategories.ts
export const useCategories = () => {
  return useQuery({
    queryKey: ['categories'],
    queryFn: categoryApi.getList,
    staleTime: 10 * 60 * 1000, // 10분간 fresh
  });
};

export const useCreateCategory = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: categoryApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['categories'] });
    }
  });
};
```

## 폼 상태 관리

### 1. 카드 생성 폼
```typescript
// features/cards/components/CardForm.tsx
interface CardFormData {
  contentUrl: string;
  categoryId: string;
  memo?: string;
}

export const CardForm: React.FC = () => {
  const { control, handleSubmit, formState: { errors, isSubmitting } } = useForm<CardFormData>({
    resolver: zodResolver(cardFormSchema),
    defaultValues: {
      contentUrl: '',
      categoryId: '',
      memo: ''
    }
  });

  const createCard = useCreateCard();
  const { data: categories } = useCategories();

  const onSubmit = async (data: CardFormData) => {
    try {
      await createCard.mutateAsync(data);
      // 성공 시 폼 리셋 또는 리다이렉트
    } catch (error) {
      // 에러는 useMutation에서 처리
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <Controller
        name="contentUrl"
        control={control}
        render={({ field }) => (
          <Input
            label="YouTube URL"
            placeholder="https://www.youtube.com/watch?v=..."
            error={errors.contentUrl?.message}
            {...field}
          />
        )}
      />

      <Controller
        name="categoryId"
        control={control}
        render={({ field }) => (
          <Select
            label="카테고리"
            options={categories?.map(cat => ({ value: cat.id, label: cat.name }))}
            error={errors.categoryId?.message}
            {...field}
          />
        )}
      />

      <Controller
        name="memo"
        control={control}
        render={({ field }) => (
          <Textarea
            label="메모 (선택사항)"
            placeholder="이 영상에 대한 메모를 입력하세요..."
            {...field}
          />
        )}
      />

      <Button
        type="submit"
        loading={isSubmitting || createCard.isLoading}
        fullWidth
      >
        카드 저장
      </Button>
    </form>
  );
};
```

### 2. 검색 폼
```typescript
// features/search/components/SearchForm.tsx
export const SearchForm: React.FC = () => {
  const { query, filters, setQuery, setFilters } = useSearchStore();
  const { data: categories } = useCategories();

  const { control, watch } = useForm({
    defaultValues: {
      query,
      categoryId: filters.category,
      tags: filters.tags,
      sortBy: filters.sortBy
    }
  });

  // 실시간 검색
  const watchedQuery = watch('query');
  const debouncedQuery = useDebounce(watchedQuery, 300);

  useEffect(() => {
    setQuery(debouncedQuery);
  }, [debouncedQuery, setQuery]);

  return (
    <div className="space-y-4">
      <Controller
        name="query"
        control={control}
        render={({ field }) => (
          <SearchBar
            placeholder="카드 검색..."
            {...field}
          />
        )}
      />

      <div className="flex flex-wrap gap-2">
        <Controller
          name="categoryId"
          control={control}
          render={({ field }) => (
            <Select
              placeholder="카테고리"
              options={categories?.map(cat => ({ value: cat.id, label: cat.name }))}
              onChange={(value) => {
                field.onChange(value);
                setFilters({ category: value });
              }}
              {...field}
            />
          )}
        />

        <Controller
          name="sortBy"
          control={control}
          render={({ field }) => (
            <Select
              placeholder="정렬"
              options={[
                { value: 'created_at', label: '최신순' },
                { value: 'title', label: '제목순' },
                { value: 'favorited_at', label: '즐겨찾기순' }
              ]}
              onChange={(value) => {
                field.onChange(value);
                setFilters({ sortBy: value });
              }}
              {...field}
            />
          )}
        />
      </div>
    </div>
  );
};
```

## 상태 동기화 및 최적화

### 1. 자동 세션 연장
```typescript
// shared/hooks/useSessionManager.ts
export const useSessionManager = () => {
  const { checkSession, refreshSession, logout } = useAuthStore();
  const queryClient = useQueryClient();

  useEffect(() => {
    const interval = setInterval(() => {
      if (!checkSession()) {
        logout();
        queryClient.clear(); // 모든 캐시 클리어
        window.location.href = '/auth/login';
      } else {
        // 활동이 있으면 세션 연장
        refreshSession();
      }
    }, 60 * 1000); // 1분마다 체크

    return () => clearInterval(interval);
  }, [checkSession, refreshSession, logout, queryClient]);
};
```

### 2. 오프라인 상태 처리
```typescript
// shared/hooks/useOnlineStatus.ts
export const useOnlineStatus = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const queryClient = useQueryClient();

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      // 온라인 복구 시 모든 쿼리 재실행
      queryClient.resumePausedMutations();
      queryClient.invalidateQueries();
    };

    const handleOffline = () => {
      setIsOnline(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [queryClient]);

  return isOnline;
};
```

이 상태 관리 시스템은 클라이언트 상태와 서버 상태를 명확히 분리하고, 최적화된 캐싱과 동기화를 제공합니다.
