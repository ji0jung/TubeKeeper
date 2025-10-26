# 컴포넌트 라이브러리 설계

## 컴포넌트 계층 구조

```
UI Components (기본 컴포넌트)
├── Button, Input, Modal 등
├── Spinner, ProgressBar, Skeleton
└── Toast, ErrorBoundary

Layout Components (레이아웃)
├── Header, Sidebar, Footer
├── PageLayout, Container
└── Grid, Stack

Feature Components (도메인별)
├── Auth: LoginForm, RegisterForm
├── Cards: CardList, CardForm, CardDetail
├── Categories: CategorySelector
├── Search: SearchBar, SearchResults
└── Sharing: ShareButton, SharedCardView
```

## 1. 공통 UI 컴포넌트

### Button 컴포넌트
```typescript
// shared/components/ui/Button/Button.tsx
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline' | 'ghost';
  size: 'sm' | 'md' | 'lg';
  loading?: boolean;
  disabled?: boolean;
  fullWidth?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  fullWidth = false,
  leftIcon,
  rightIcon,
  children,
  onClick,
  type = 'button',
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';
  
  const variants = {
    primary: 'bg-primary-500 text-white hover:bg-primary-600 focus:ring-primary-500',
    secondary: 'bg-neutral-100 text-neutral-900 hover:bg-neutral-200 focus:ring-neutral-500',
    outline: 'border border-neutral-300 text-neutral-700 hover:bg-neutral-50 focus:ring-neutral-500',
    ghost: 'text-neutral-700 hover:bg-neutral-100 focus:ring-neutral-500'
  };

  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  };

  return (
    <button
      type={type}
      disabled={disabled || loading}
      onClick={onClick}
      className={`
        ${baseClasses}
        ${variants[variant]}
        ${sizes[size]}
        ${fullWidth ? 'w-full' : ''}
        ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
      `}
      {...props}
    >
      {loading && <Spinner size="sm" className="mr-2" />}
      {!loading && leftIcon && <span className="mr-2">{leftIcon}</span>}
      {children}
      {!loading && rightIcon && <span className="ml-2">{rightIcon}</span>}
    </button>
  );
};
```

### Input 컴포넌트
```typescript
// shared/components/ui/Input/Input.tsx
interface InputProps {
  label?: string;
  placeholder?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  type?: 'text' | 'email' | 'password' | 'url';
  required?: boolean;
  disabled?: boolean;
  value?: string;
  onChange?: (value: string) => void;
}

export const Input: React.FC<InputProps> = ({
  label,
  placeholder,
  error,
  helperText,
  leftIcon,
  rightIcon,
  type = 'text',
  required = false,
  disabled = false,
  value,
  onChange,
  ...props
}) => {
  const inputId = useId();

  return (
    <div className="w-full">
      {label && (
        <label 
          htmlFor={inputId}
          className="block text-sm font-medium text-neutral-700 mb-1"
        >
          {label}
          {required && <span className="text-error-500 ml-1">*</span>}
        </label>
      )}
      
      <div className="relative">
        {leftIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {leftIcon}
          </div>
        )}
        
        <input
          id={inputId}
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          disabled={disabled}
          className={`
            block w-full px-3 py-2 border rounded-lg text-sm
            placeholder-neutral-400 focus:outline-none focus:ring-2 focus:ring-offset-2
            ${leftIcon ? 'pl-10' : ''}
            ${rightIcon ? 'pr-10' : ''}
            ${error 
              ? 'border-error-300 focus:ring-error-500 focus:border-error-500' 
              : 'border-neutral-300 focus:ring-primary-500 focus:border-primary-500'
            }
            ${disabled ? 'bg-neutral-50 cursor-not-allowed' : 'bg-white'}
          `}
          {...props}
        />
        
        {rightIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            {rightIcon}
          </div>
        )}
      </div>
      
      {error && (
        <p className="mt-1 text-sm text-error-600">{error}</p>
      )}
      
      {helperText && !error && (
        <p className="mt-1 text-sm text-neutral-500">{helperText}</p>
      )}
    </div>
  );
};
```

### Modal 컴포넌트
```typescript
// shared/components/ui/Modal/Modal.tsx
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  size = 'md',
  children
}) => {
  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* 배경 오버레이 */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* 모달 컨테이너 */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div 
          className={`
            relative w-full ${sizes[size]} bg-white rounded-lg shadow-xl
            transform transition-all
          `}
          onClick={(e) => e.stopPropagation()}
        >
          {/* 헤더 */}
          {title && (
            <div className="flex items-center justify-between p-6 border-b border-neutral-200">
              <h3 className="text-lg font-semibold text-neutral-900">
                {title}
              </h3>
              <button
                onClick={onClose}
                className="text-neutral-400 hover:text-neutral-600"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>
          )}
          
          {/* 콘텐츠 */}
          <div className="p-6">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};
```

## 2. 레이아웃 컴포넌트

### Header 컴포넌트
```typescript
// shared/components/layout/Header.tsx
interface HeaderProps {
  user?: User;
  onMenuClick?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ user, onMenuClick }) => {
  return (
    <header className="bg-white border-b border-neutral-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* 로고 및 메뉴 */}
          <div className="flex items-center">
            <button
              onClick={onMenuClick}
              className="md:hidden p-2 rounded-md text-neutral-400 hover:text-neutral-500"
            >
              <Bars3Icon className="w-6 h-6" />
            </button>
            
            <Link to="/" className="flex items-center ml-2 md:ml-0">
              <img src="/logo.svg" alt="YouTube Link App" className="h-8 w-auto" />
            </Link>
          </div>

          {/* 검색바 (데스크톱) */}
          <div className="hidden md:block flex-1 max-w-lg mx-8">
            <SearchBar />
          </div>

          {/* 사용자 메뉴 */}
          <div className="flex items-center space-x-4">
            {user ? (
              <UserMenu user={user} />
            ) : (
              <div className="flex space-x-2">
                <Button variant="ghost" size="sm">
                  <Link to="/auth/login">로그인</Link>
                </Button>
                <Button variant="primary" size="sm">
                  <Link to="/auth/register">회원가입</Link>
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
```

### PageLayout 컴포넌트
```typescript
// shared/components/layout/PageLayout.tsx
interface PageLayoutProps {
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
}

export const PageLayout: React.FC<PageLayoutProps> = ({
  title,
  subtitle,
  actions,
  children
}) => {
  return (
    <div className="min-h-screen bg-neutral-50">
      <Header />
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 페이지 헤더 */}
        {(title || actions) && (
          <div className="mb-8">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
              <div>
                {title && (
                  <h1 className="text-2xl font-bold text-neutral-900">
                    {title}
                  </h1>
                )}
                {subtitle && (
                  <p className="mt-1 text-sm text-neutral-500">
                    {subtitle}
                  </p>
                )}
              </div>
              {actions && (
                <div className="mt-4 sm:mt-0">
                  {actions}
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* 페이지 콘텐츠 */}
        {children}
      </main>
    </div>
  );
};
```

## 3. 도메인별 컴포넌트

### CardList 컴포넌트 (features/cards)
```typescript
// features/cards/components/CardList.tsx
interface CardListProps {
  cards: Card[];
  loading?: boolean;
  onCardClick?: (card: Card) => void;
  onFavoriteToggle?: (cardId: string) => void;
  showSkeleton?: boolean;
}

export const CardList: React.FC<CardListProps> = ({
  cards,
  loading = false,
  onCardClick,
  onFavoriteToggle,
  showSkeleton = false
}) => {
  if (showSkeleton || loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Skeleton variant="card" count={6} />
      </div>
    );
  }

  if (cards.length === 0) {
    return (
      <div className="text-center py-12">
        <VideoCameraIcon className="mx-auto h-12 w-12 text-neutral-400" />
        <h3 className="mt-2 text-sm font-medium text-neutral-900">
          저장된 카드가 없습니다
        </h3>
        <p className="mt-1 text-sm text-neutral-500">
          첫 번째 YouTube 링크를 저장해보세요.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {cards.map((card) => (
        <CardItem
          key={card.id}
          card={card}
          onClick={() => onCardClick?.(card)}
          onFavoriteToggle={() => onFavoriteToggle?.(card.id)}
        />
      ))}
    </div>
  );
};
```

### CardItem 컴포넌트
```typescript
// features/cards/components/CardItem.tsx
interface CardItemProps {
  card: Card;
  onClick?: () => void;
  onFavoriteToggle?: () => void;
}

export const CardItem: React.FC<CardItemProps> = ({
  card,
  onClick,
  onFavoriteToggle
}) => {
  return (
    <div 
      className="bg-white rounded-lg shadow-sm border border-neutral-200 overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
      onClick={onClick}
    >
      {/* 썸네일 */}
      <div className="relative aspect-video">
        <img
          src={card.thumbnail}
          alt={card.title}
          className="w-full h-full object-cover"
        />
        
        {/* 상태 표시 */}
        {card.status !== 'COMPLETED' && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            {card.status === 'SUMMARY_GENERATING' ? (
              <div className="text-white text-center">
                <Spinner size="md" color="white" />
                <p className="mt-2 text-sm">AI 요약 생성 중...</p>
              </div>
            ) : (
              <Spinner size="md" color="white" />
            )}
          </div>
        )}
        
        {/* 즐겨찾기 버튼 */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onFavoriteToggle?.();
          }}
          className="absolute top-2 right-2 p-2 rounded-full bg-black bg-opacity-50 text-white hover:bg-opacity-70"
        >
          <StarIcon 
            className={`w-5 h-5 ${card.is_favorite ? 'fill-yellow-400 text-yellow-400' : ''}`}
          />
        </button>
      </div>
      
      {/* 카드 정보 */}
      <div className="p-4">
        <h3 className="font-medium text-neutral-900 line-clamp-2 mb-2">
          {card.title}
        </h3>
        
        {card.summary && (
          <p className="text-sm text-neutral-600 line-clamp-3 mb-3">
            {card.summary}
          </p>
        )}
        
        {/* 태그 */}
        {card.tags && card.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {card.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="inline-block px-2 py-1 text-xs bg-neutral-100 text-neutral-600 rounded"
              >
                #{tag}
              </span>
            ))}
            {card.tags.length > 3 && (
              <span className="text-xs text-neutral-400">
                +{card.tags.length - 3}
              </span>
            )}
          </div>
        )}
        
        {/* 메타 정보 */}
        <div className="flex items-center justify-between text-xs text-neutral-500">
          <span>{card.category?.name}</span>
          <span>{formatDate(card.created_at)}</span>
        </div>
      </div>
    </div>
  );
};
```

### SearchBar 컴포넌트 (features/search)
```typescript
// features/search/components/SearchBar.tsx
interface SearchBarProps {
  placeholder?: string;
  onSearch?: (query: string) => void;
  suggestions?: SearchSuggestion[];
}

export const SearchBar: React.FC<SearchBarProps> = ({
  placeholder = "카드 검색...",
  onSearch,
  suggestions = []
}) => {
  const [query, setQuery] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const debouncedQuery = useDebounce(query, 300);

  useEffect(() => {
    if (debouncedQuery) {
      onSearch?.(debouncedQuery);
    }
  }, [debouncedQuery, onSearch]);

  return (
    <div className="relative">
      <Input
        placeholder={placeholder}
        value={query}
        onChange={setQuery}
        leftIcon={<MagnifyingGlassIcon className="w-5 h-5 text-neutral-400" />}
        onFocus={() => setShowSuggestions(true)}
        onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
      />
      
      {/* 검색 제안 */}
      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-neutral-200 rounded-lg shadow-lg z-10">
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => {
                setQuery(suggestion.value);
                setShowSuggestions(false);
              }}
              className="w-full px-4 py-2 text-left hover:bg-neutral-50 first:rounded-t-lg last:rounded-b-lg"
            >
              <div className="flex items-center">
                {suggestion.type === 'tag' && (
                  <HashtagIcon className="w-4 h-4 text-neutral-400 mr-2" />
                )}
                <span className="text-sm">{suggestion.value}</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
```

## 4. 컴포넌트 Props 인터페이스

### 공통 Props 패턴
```typescript
// shared/types/component.types.ts

// 기본 컴포넌트 Props
interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

// 크기 관련 Props
interface SizeProps {
  size?: 'sm' | 'md' | 'lg';
}

// 상태 관련 Props
interface StateProps {
  loading?: boolean;
  disabled?: boolean;
  error?: string;
}

// 이벤트 관련 Props
interface EventProps {
  onClick?: () => void;
  onChange?: (value: any) => void;
  onSubmit?: () => void;
}

// 조합된 Props 타입
export type ComponentProps = BaseComponentProps & SizeProps & StateProps & EventProps;
```

## 5. 컴포넌트 테스트 전략

### 단위 테스트 예시
```typescript
// shared/components/ui/Button/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button')).toHaveTextContent('Click me');
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('shows loading state', () => {
    render(<Button loading>Loading</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
    expect(screen.getByLabelText('로딩 중')).toBeInTheDocument();
  });
});
```

이 컴포넌트 라이브러리는 재사용성, 접근성, 타입 안정성을 고려하여 설계되었으며, 전체 애플리케이션에서 일관된 UI를 제공합니다.
