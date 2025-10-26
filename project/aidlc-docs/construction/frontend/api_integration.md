# API 통신 및 데이터 처리

## API 클라이언트 설계

### 1. Axios 클라이언트 설정
```typescript
// shared/services/api/client.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { useAuthStore } from '@/app/store/authStore';
import { useUIStore } from '@/app/store/uiStore';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // 요청 인터셉터
    this.client.interceptors.request.use(
      (config) => {
        const { token } = useAuthStore.getState();
        
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }

        // 세션 자동 연장
        if (token) {
          useAuthStore.getState().refreshSession();
        }

        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // 응답 인터셉터
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      (error) => {
        const { status, data } = error.response || {};

        // 인증 에러 처리
        if (status === 401) {
          useAuthStore.getState().logout();
          window.location.href = '/auth/login';
          return Promise.reject(error);
        }

        // 서버 에러 알림
        if (status >= 500) {
          useUIStore.getState().addNotification({
            type: 'error',
            title: '서버 오류',
            message: '잠시 후 다시 시도해주세요.'
          });
        }

        // 클라이언트 에러 처리
        if (status >= 400 && status < 500) {
          const errorMessage = data?.error?.message || '요청 처리 중 오류가 발생했습니다.';
          
          // 특정 에러 코드별 처리
          switch (data?.error?.code) {
            case 'CARD_004':
              useUIStore.getState().addNotification({
                type: 'warning',
                title: '중복 카드',
                message: '이미 저장된 카드입니다.'
              });
              break;
            case 'AUTH_002':
              useAuthStore.getState().logout();
              break;
            default:
              useUIStore.getState().addNotification({
                type: 'error',
                title: '오류',
                message: errorMessage
              });
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // HTTP 메서드들
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }
}

export const apiClient = new ApiClient();
```

### 2. API 엔드포인트 상수
```typescript
// shared/services/api/endpoints.ts
export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    REGISTER: '/auth/register',
    VERIFY_REGISTRATION: '/auth/verify-registration',
    LOGIN: '/auth/login',
    VERIFY_LOGIN: '/auth/verify-login',
    LOGOUT: '/auth/logout',
    REFRESH_SESSION: '/auth/refresh-session',
    DELETE_ACCOUNT: '/auth/account',
  },

  // Profile
  PROFILE: {
    GET: '/profile',
    UPDATE: '/profile',
  },

  // Cards
  CARDS: {
    LIST: '/cards',
    CREATE: '/cards',
    GET: (id: string) => `/cards/${id}`,
    UPDATE: (id: string) => `/cards/${id}`,
    DELETE: (id: string) => `/cards/${id}`,
    FAVORITE: (id: string) => `/cards/${id}/favorite`,
    PUBLIC: (id: string) => `/cards/${id}/public`,
  },

  // Categories
  CATEGORIES: {
    LIST: '/categories',
    CREATE: '/categories',
    UPDATE: (id: string) => `/categories/${id}`,
    DELETE: (id: string) => `/categories/${id}`,
  },

  // Search
  SEARCH: {
    MY_CARDS: '/my-cards',
    FAVORITES: '/my-cards/favorites',
    PUBLIC_CARDS: '/public-cards',
    SUGGESTIONS: '/search/suggestions',
    TAGS: '/tags',
    SAVE_PUBLIC_CARD: (id: string) => `/public-cards/${id}/save`,
  },

  // Sharing
  SHARING: {
    CREATE_SHARE: (id: string) => `/cards/${id}/share`,
    GET_SHARED: (shareId: string) => `/shared/${shareId}`,
    SAVE_SHARED: (shareId: string) => `/shared/${shareId}/save`,
  },

  // YouTube & AI
  YOUTUBE: {
    EXTRACT: '/youtube/extract',
  },
  
  AI: {
    SUMMARIZE: '/ai/summarize',
  },

  // System
  SYSTEM: {
    HEALTH: '/system/health',
    CONFIG: '/system/config',
  },
} as const;
```

## 도메인별 API 서비스

### 1. Auth API
```typescript
// features/auth/services/authApi.ts
interface RegisterData {
  email: string;
  gender?: 'male' | 'female';
  birthYear?: number;
}

interface VerifyData {
  email: string;
  verificationCode: string;
}

interface LoginData {
  email: string;
}

export const authApi = {
  register: async (data: RegisterData): Promise<{ success: boolean; message: string }> => {
    return apiClient.post(API_ENDPOINTS.AUTH.REGISTER, data);
  },

  verifyRegistration: async (data: VerifyData): Promise<{ success: boolean; token: string; user: User }> => {
    return apiClient.post(API_ENDPOINTS.AUTH.VERIFY_REGISTRATION, data);
  },

  login: async (data: LoginData): Promise<{ success: boolean; message: string }> => {
    return apiClient.post(API_ENDPOINTS.AUTH.LOGIN, data);
  },

  verifyLogin: async (data: VerifyData): Promise<{ success: boolean; token: string; user: User }> => {
    return apiClient.post(API_ENDPOINTS.AUTH.VERIFY_LOGIN, data);
  },

  logout: async (): Promise<{ success: boolean }> => {
    return apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
  },

  refreshSession: async (): Promise<{ success: boolean; newToken: string }> => {
    return apiClient.post(API_ENDPOINTS.AUTH.REFRESH_SESSION);
  },

  deleteAccount: async (): Promise<{ success: boolean }> => {
    return apiClient.delete(API_ENDPOINTS.AUTH.DELETE_ACCOUNT);
  },
};
```

### 2. Cards API
```typescript
// features/cards/services/cardApi.ts
interface CardCreateData {
  contentUrl: string;
  categoryId: string;
  memo?: string;
}

interface CardListParams {
  cursor?: string;
  limit?: number;
  categoryId?: string;
  favoritesOnly?: boolean;
}

interface CardListResponse {
  cards: Card[];
  nextCursor?: string;
  hasMore: boolean;
}

export const cardApi = {
  getList: async (params: CardListParams): Promise<CardListResponse> => {
    const searchParams = new URLSearchParams();
    
    if (params.cursor) searchParams.append('cursor', params.cursor);
    if (params.limit) searchParams.append('limit', params.limit.toString());
    if (params.categoryId) searchParams.append('categoryId', params.categoryId);
    if (params.favoritesOnly) searchParams.append('favoritesOnly', 'true');

    const url = `${API_ENDPOINTS.CARDS.LIST}?${searchParams.toString()}`;
    return apiClient.get(url);
  },

  getById: async (id: string): Promise<{ card: Card }> => {
    return apiClient.get(API_ENDPOINTS.CARDS.GET(id));
  },

  create: async (data: CardCreateData): Promise<{ success: boolean; card: Card }> => {
    return apiClient.post(API_ENDPOINTS.CARDS.CREATE, data);
  },

  update: async (id: string, data: Partial<Card>): Promise<{ success: boolean; card: Card }> => {
    return apiClient.put(API_ENDPOINTS.CARDS.UPDATE(id), data);
  },

  delete: async (id: string): Promise<{ success: boolean }> => {
    return apiClient.delete(API_ENDPOINTS.CARDS.DELETE(id));
  },

  toggleFavorite: async (id: string): Promise<{ success: boolean; is_favorite: boolean; message: string }> => {
    return apiClient.post(API_ENDPOINTS.CARDS.FAVORITE(id));
  },

  togglePublic: async (id: string): Promise<{ success: boolean; is_public: boolean; message: string }> => {
    return apiClient.post(API_ENDPOINTS.CARDS.PUBLIC(id));
  },

  getFavorites: async (params: { cursor?: string; limit?: number }): Promise<CardListResponse> => {
    const searchParams = new URLSearchParams();
    if (params.cursor) searchParams.append('cursor', params.cursor);
    if (params.limit) searchParams.append('limit', params.limit.toString());

    const url = `${API_ENDPOINTS.SEARCH.FAVORITES}?${searchParams.toString()}`;
    return apiClient.get(url);
  },
};
```

### 3. Search API
```typescript
// features/search/services/searchApi.ts
interface SearchParams {
  query?: string;
  categoryId?: string;
  tags?: string[];
  cursor?: string;
  limit?: number;
}

interface PublicSearchParams {
  query?: string;
  tag?: string;
  page?: number;
  limit?: number;
}

interface PublicSearchResponse {
  cards: Card[];
  totalCount: number;
  currentPage: number;
  totalPages: number;
}

export const searchApi = {
  searchMyCards: async (params: SearchParams): Promise<CardListResponse> => {
    const searchParams = new URLSearchParams();
    
    if (params.query) searchParams.append('search', params.query);
    if (params.categoryId) searchParams.append('categoryId', params.categoryId);
    if (params.tags?.length) {
      params.tags.forEach(tag => searchParams.append('tag', tag));
    }
    if (params.cursor) searchParams.append('cursor', params.cursor);
    if (params.limit) searchParams.append('limit', params.limit.toString());

    const url = `${API_ENDPOINTS.SEARCH.MY_CARDS}?${searchParams.toString()}`;
    return apiClient.get(url);
  },

  searchPublicCards: async (params: PublicSearchParams): Promise<PublicSearchResponse> => {
    const searchParams = new URLSearchParams();
    
    if (params.query) searchParams.append('search', params.query);
    if (params.tag) searchParams.append('tag', params.tag);
    if (params.page) searchParams.append('page', params.page.toString());
    if (params.limit) searchParams.append('limit', params.limit.toString());

    const url = `${API_ENDPOINTS.SEARCH.PUBLIC_CARDS}?${searchParams.toString()}`;
    return apiClient.get(url);
  },

  getSuggestions: async (query: string, scope: 'my' | 'public' = 'my'): Promise<{ suggestions: SearchSuggestion[] }> => {
    const url = `${API_ENDPOINTS.SEARCH.SUGGESTIONS}?query=${encodeURIComponent(query)}&scope=${scope}`;
    return apiClient.get(url);
  },

  getTags: async (scope: 'my' | 'public' = 'my'): Promise<{ tags: TagInfo[] }> => {
    const url = `${API_ENDPOINTS.SEARCH.TAGS}?scope=${scope}`;
    return apiClient.get(url);
  },

  savePublicCard: async (id: string, categoryId?: string): Promise<{ success: boolean; newCard?: Card; alreadyExists?: boolean }> => {
    return apiClient.post(API_ENDPOINTS.SEARCH.SAVE_PUBLIC_CARD(id), { categoryId });
  },
};
```

## 인증 토큰 관리

### 1. 토큰 저장소
```typescript
// shared/services/auth/tokenManager.ts
class TokenManager {
  private readonly TOKEN_KEY = 'auth_token';
  private readonly REFRESH_KEY = 'refresh_token';

  setToken(token: string): void {
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  removeToken(): void {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_KEY);
  }

  setRefreshToken(refreshToken: string): void {
    localStorage.setItem(this.REFRESH_KEY, refreshToken);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(this.REFRESH_KEY);
  }

  isTokenExpired(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      return Date.now() >= payload.exp * 1000;
    } catch {
      return true;
    }
  }
}

export const tokenManager = new TokenManager();
```

### 2. 자동 토큰 갱신
```typescript
// shared/hooks/useTokenRefresh.ts
export const useTokenRefresh = () => {
  const { token, logout } = useAuthStore();

  useEffect(() => {
    if (!token) return;

    const checkTokenExpiry = () => {
      if (tokenManager.isTokenExpired(token)) {
        // 토큰 만료 시 자동 갱신 시도
        authApi.refreshSession()
          .then(({ newToken }) => {
            tokenManager.setToken(newToken);
            useAuthStore.getState().refreshSession();
          })
          .catch(() => {
            logout();
          });
      }
    };

    // 5분마다 토큰 만료 확인
    const interval = setInterval(checkTokenExpiry, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, [token, logout]);
};
```

## 에러 처리 및 재시도 로직

### 1. 에러 처리 유틸리티
```typescript
// shared/services/utils/errorHandler.ts
interface ApiError {
  code: string;
  message: string;
  details?: any;
}

export class ApiErrorHandler {
  static handle(error: any): ApiError {
    if (error.response?.data?.error) {
      return error.response.data.error;
    }

    if (error.code === 'NETWORK_ERROR') {
      return {
        code: 'NETWORK_ERROR',
        message: '네트워크 연결을 확인해주세요.'
      };
    }

    if (error.code === 'TIMEOUT') {
      return {
        code: 'TIMEOUT',
        message: '요청 시간이 초과되었습니다.'
      };
    }

    return {
      code: 'UNKNOWN_ERROR',
      message: '알 수 없는 오류가 발생했습니다.'
    };
  }

  static shouldRetry(error: ApiError): boolean {
    const retryableCodes = ['NETWORK_ERROR', 'TIMEOUT', 'SERVER_ERROR'];
    return retryableCodes.includes(error.code);
  }
}
```

### 2. 재시도 로직
```typescript
// shared/services/utils/retryLogic.ts
interface RetryOptions {
  maxRetries: number;
  delay: number;
  backoff: boolean;
}

export const withRetry = async <T>(
  fn: () => Promise<T>,
  options: RetryOptions = { maxRetries: 3, delay: 1000, backoff: true }
): Promise<T> => {
  let lastError: any;

  for (let attempt = 0; attempt <= options.maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      
      const apiError = ApiErrorHandler.handle(error);
      
      if (attempt === options.maxRetries || !ApiErrorHandler.shouldRetry(apiError)) {
        throw error;
      }

      // 백오프 지연
      const delay = options.backoff 
        ? options.delay * Math.pow(2, attempt)
        : options.delay;
        
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }

  throw lastError;
};
```

## 데이터 변환 및 검증

### 1. 응답 변환기
```typescript
// shared/services/utils/responseTransformer.ts
export const responseTransformer = {
  card: (data: any): Card => ({
    id: data.id,
    title: data.title,
    thumbnail: data.thumbnail,
    script: data.script,
    summary: data.summary,
    tags: data.tags || [],
    memo: data.memo,
    category: data.category,
    is_favorite: data.is_favorite,
    favorited_at: data.favorited_at,
    is_public: data.is_public,
    status: data.status,
    created_at: data.created_at,
    updated_at: data.updated_at,
  }),

  user: (data: any): User => ({
    id: data.id,
    email: data.email,
    gender: data.gender,
    birthYear: data.birth_year,
    language: data.language,
    created_at: data.created_at,
  }),

  category: (data: any): Category => ({
    id: data.id,
    name: data.name,
    cardCount: data.card_count,
    isDeletable: data.is_deletable,
  }),
};
```

### 2. 요청 데이터 검증
```typescript
// shared/services/utils/validation.ts
import { z } from 'zod';

export const schemas = {
  cardCreate: z.object({
    contentUrl: z.string().url('올바른 URL을 입력해주세요'),
    categoryId: z.string().min(1, '카테고리를 선택해주세요'),
    memo: z.string().max(2000, '메모는 2000자 이하로 입력해주세요').optional(),
  }),

  userRegister: z.object({
    email: z.string().email('올바른 이메일을 입력해주세요'),
    gender: z.enum(['male', 'female']).optional(),
    birthYear: z.number().min(1900).max(new Date().getFullYear()).optional(),
  }),

  search: z.object({
    query: z.string().min(1, '검색어를 입력해주세요').max(100, '검색어는 100자 이하로 입력해주세요'),
    categoryId: z.string().optional(),
    tags: z.array(z.string()).optional(),
  }),
};
```

이 API 통신 시스템은 타입 안전성, 에러 처리, 자동 재시도, 토큰 관리를 포함한 완전한 클라이언트-서버 통신을 제공합니다.
