# 접근성 및 사용성 가이드라인

## 웹 접근성 가이드라인 (WCAG 2.1 AA)

### 1. 인식 가능성 (Perceivable)

#### 대체 텍스트
```typescript
// shared/components/ui/AccessibleImage.tsx
interface AccessibleImageProps {
  src: string;
  alt: string;
  decorative?: boolean;
  longDesc?: string;
}

export const AccessibleImage: React.FC<AccessibleImageProps> = ({
  src,
  alt,
  decorative = false,
  longDesc,
  ...props
}) => {
  return (
    <>
      <img
        src={src}
        alt={decorative ? '' : alt}
        aria-describedby={longDesc ? 'long-desc' : undefined}
        role={decorative ? 'presentation' : undefined}
        {...props}
      />
      {longDesc && (
        <div id="long-desc" className="sr-only">
          {longDesc}
        </div>
      )}
    </>
  );
};

// 사용 예시
<AccessibleImage
  src={card.thumbnail}
  alt={`${card.title} 영상 썸네일`}
  longDesc={card.summary ? `영상 요약: ${card.summary}` : undefined}
/>
```

#### 색상 대비 및 시각적 표시
```css
/* styles/accessibility.css */

/* 고대비 모드 지원 */
@media (prefers-contrast: high) {
  .card {
    border: 2px solid #000;
  }
  
  .button-primary {
    background-color: #000;
    color: #fff;
    border: 2px solid #fff;
  }
}

/* 색상에만 의존하지 않는 상태 표시 */
.favorite-button {
  position: relative;
}

.favorite-button[aria-pressed="true"]::after {
  content: "★";
  position: absolute;
  top: -2px;
  right: -2px;
  font-size: 12px;
  color: #fbbf24;
}

/* 포커스 표시 강화 */
.focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
  border-radius: 4px;
}

/* 움직임 감소 설정 */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### 2. 운용 가능성 (Operable)

#### 키보드 네비게이션
```typescript
// shared/hooks/useKeyboardNavigation.ts
export const useKeyboardNavigation = (
  items: any[],
  onSelect: (item: any, index: number) => void
) => {
  const [focusedIndex, setFocusedIndex] = useState(-1);

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        setFocusedIndex(prev => 
          prev < items.length - 1 ? prev + 1 : 0
        );
        break;
        
      case 'ArrowUp':
        event.preventDefault();
        setFocusedIndex(prev => 
          prev > 0 ? prev - 1 : items.length - 1
        );
        break;
        
      case 'Enter':
      case ' ':
        event.preventDefault();
        if (focusedIndex >= 0) {
          onSelect(items[focusedIndex], focusedIndex);
        }
        break;
        
      case 'Escape':
        setFocusedIndex(-1);
        break;
    }
  }, [items, focusedIndex, onSelect]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return { focusedIndex, setFocusedIndex };
};

// 사용 예시 - 카드 목록 키보드 네비게이션
const CardList: React.FC<{ cards: Card[] }> = ({ cards }) => {
  const { focusedIndex } = useKeyboardNavigation(cards, (card) => {
    navigate(`/cards/${card.id}`);
  });

  return (
    <div role="grid" aria-label="카드 목록">
      {cards.map((card, index) => (
        <CardItem
          key={card.id}
          card={card}
          tabIndex={index === focusedIndex ? 0 : -1}
          aria-selected={index === focusedIndex}
          role="gridcell"
        />
      ))}
    </div>
  );
};
```

#### Skip Links
```typescript
// shared/components/navigation/SkipLinks.tsx
export const SkipLinks: React.FC = () => {
  return (
    <div className="skip-links">
      <a 
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-primary-500 text-white px-4 py-2 rounded z-50"
      >
        메인 콘텐츠로 바로가기
      </a>
      <a 
        href="#navigation"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-32 bg-primary-500 text-white px-4 py-2 rounded z-50"
      >
        네비게이션으로 바로가기
      </a>
    </div>
  );
};
```

### 3. 이해 가능성 (Understandable)

#### 폼 접근성
```typescript
// shared/components/forms/AccessibleForm.tsx
interface AccessibleFormProps {
  onSubmit: (data: any) => void;
  children: React.ReactNode;
  title: string;
  description?: string;
}

export const AccessibleForm: React.FC<AccessibleFormProps> = ({
  onSubmit,
  children,
  title,
  description
}) => {
  const formId = useId();
  const descriptionId = useId();

  return (
    <form
      id={formId}
      onSubmit={onSubmit}
      aria-labelledby={`${formId}-title`}
      aria-describedby={description ? descriptionId : undefined}
      noValidate // 커스텀 검증 사용
    >
      <h2 id={`${formId}-title`} className="text-xl font-semibold mb-4">
        {title}
      </h2>
      
      {description && (
        <p id={descriptionId} className="text-neutral-600 mb-6">
          {description}
        </p>
      )}
      
      {children}
    </form>
  );
};

// 접근성 강화된 Input 컴포넌트
interface AccessibleInputProps extends InputProps {
  required?: boolean;
  describedBy?: string;
  invalid?: boolean;
}

export const AccessibleInput: React.FC<AccessibleInputProps> = ({
  label,
  error,
  helperText,
  required = false,
  describedBy,
  invalid,
  ...props
}) => {
  const inputId = useId();
  const errorId = useId();
  const helperId = useId();

  const ariaDescribedBy = [
    error ? errorId : null,
    helperText ? helperId : null,
    describedBy
  ].filter(Boolean).join(' ') || undefined;

  return (
    <div className="form-field">
      <label 
        htmlFor={inputId}
        className="block text-sm font-medium text-neutral-700 mb-1"
      >
        {label}
        {required && (
          <span className="text-error-500 ml-1" aria-label="필수 입력">
            *
          </span>
        )}
      </label>
      
      <input
        id={inputId}
        required={required}
        aria-invalid={invalid || !!error}
        aria-describedby={ariaDescribedBy}
        className={`
          block w-full px-3 py-2 border rounded-lg
          ${error ? 'border-error-300' : 'border-neutral-300'}
          focus:ring-2 focus:ring-primary-500 focus:border-primary-500
        `}
        {...props}
      />
      
      {error && (
        <div 
          id={errorId}
          role="alert"
          aria-live="polite"
          className="mt-1 text-sm text-error-600"
        >
          {error}
        </div>
      )}
      
      {helperText && !error && (
        <div 
          id={helperId}
          className="mt-1 text-sm text-neutral-500"
        >
          {helperText}
        </div>
      )}
    </div>
  );
};
```

#### 에러 메시지 및 상태 알림
```typescript
// shared/components/feedback/AccessibleAlert.tsx
interface AccessibleAlertProps {
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message: string;
  dismissible?: boolean;
  onDismiss?: () => void;
}

export const AccessibleAlert: React.FC<AccessibleAlertProps> = ({
  type,
  title,
  message,
  dismissible = false,
  onDismiss
}) => {
  const alertId = useId();

  const roleMap = {
    error: 'alert',
    warning: 'alert',
    success: 'status',
    info: 'status'
  };

  const iconMap = {
    error: ExclamationTriangleIcon,
    warning: ExclamationTriangleIcon,
    success: CheckCircleIcon,
    info: InformationCircleIcon
  };

  const Icon = iconMap[type];

  return (
    <div
      id={alertId}
      role={roleMap[type]}
      aria-live="polite"
      aria-atomic="true"
      className={`
        flex items-start p-4 rounded-lg border
        ${type === 'error' ? 'bg-error-50 border-error-200' : ''}
        ${type === 'warning' ? 'bg-warning-50 border-warning-200' : ''}
        ${type === 'success' ? 'bg-success-50 border-success-200' : ''}
        ${type === 'info' ? 'bg-info-50 border-info-200' : ''}
      `}
    >
      <Icon className="w-5 h-5 mt-0.5 mr-3 flex-shrink-0" />
      
      <div className="flex-1">
        <h3 className="text-sm font-medium">
          {title}
        </h3>
        <p className="mt-1 text-sm">
          {message}
        </p>
      </div>
      
      {dismissible && (
        <button
          onClick={onDismiss}
          aria-label={`${title} 알림 닫기`}
          className="ml-3 flex-shrink-0 p-1 rounded hover:bg-black hover:bg-opacity-10"
        >
          <XMarkIcon className="w-4 h-4" />
        </button>
      )}
    </div>
  );
};
```

### 4. 견고성 (Robust)

#### 스크린 리더 지원
```typescript
// shared/components/ui/ScreenReaderOnly.tsx
export const ScreenReaderOnly: React.FC<{ children: React.ReactNode }> = ({ 
  children 
}) => (
  <span className="sr-only">
    {children}
  </span>
);

// 사용 예시
const CardItem: React.FC<{ card: Card }> = ({ card }) => (
  <div className="card">
    <img src={card.thumbnail} alt={card.title} />
    
    <button onClick={toggleFavorite} aria-pressed={card.is_favorite}>
      <StarIcon />
      <ScreenReaderOnly>
        {card.is_favorite ? '즐겨찾기에서 제거' : '즐겨찾기에 추가'}
      </ScreenReaderOnly>
    </button>
    
    <div>
      <h3>{card.title}</h3>
      <ScreenReaderOnly>
        생성일: {formatDate(card.created_at)}
      </ScreenReaderOnly>
      <ScreenReaderOnly>
        카테고리: {card.category?.name}
      </ScreenReaderOnly>
    </div>
  </div>
);
```

#### ARIA 라이브 영역
```typescript
// shared/components/feedback/LiveRegion.tsx
interface LiveRegionProps {
  message: string;
  politeness?: 'polite' | 'assertive' | 'off';
  atomic?: boolean;
}

export const LiveRegion: React.FC<LiveRegionProps> = ({
  message,
  politeness = 'polite',
  atomic = true
}) => {
  return (
    <div
      aria-live={politeness}
      aria-atomic={atomic}
      className="sr-only"
    >
      {message}
    </div>
  );
};

// 사용 예시 - 검색 결과 알림
const SearchResults: React.FC = () => {
  const [searchMessage, setSearchMessage] = useState('');
  
  useEffect(() => {
    if (results.length > 0) {
      setSearchMessage(`${results.length}개의 검색 결과를 찾았습니다.`);
    } else if (query && results.length === 0) {
      setSearchMessage('검색 결과가 없습니다.');
    }
  }, [results, query]);

  return (
    <>
      <LiveRegion message={searchMessage} />
      {/* 검색 결과 렌더링 */}
    </>
  );
};
```

## 키보드 단축키

### 1. 전역 단축키
```typescript
// shared/hooks/useGlobalShortcuts.ts
export const useGlobalShortcuts = () => {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      // Ctrl/Cmd + K: 검색 포커스
      if ((event.ctrlKey || event.metaKey) && event.key === 'k') {
        event.preventDefault();
        const searchInput = document.querySelector('[data-search-input]') as HTMLInputElement;
        searchInput?.focus();
      }

      // Ctrl/Cmd + N: 새 카드 생성
      if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
        event.preventDefault();
        navigate('/cards/create');
      }

      // ESC: 모달 닫기
      if (event.key === 'Escape') {
        const modal = document.querySelector('[role="dialog"]');
        if (modal) {
          const closeButton = modal.querySelector('[data-close-modal]') as HTMLButtonElement;
          closeButton?.click();
        }
      }

      // F: 즐겨찾기 토글 (카드 상세 페이지에서)
      if (event.key === 'f' && !event.ctrlKey && !event.metaKey) {
        const favoriteButton = document.querySelector('[data-favorite-button]') as HTMLButtonElement;
        if (favoriteButton && document.activeElement !== favoriteButton) {
          favoriteButton?.click();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);
};
```

### 2. 단축키 도움말
```typescript
// shared/components/help/ShortcutHelp.tsx
const shortcuts = [
  { key: 'Ctrl + K', description: '검색창 포커스' },
  { key: 'Ctrl + N', description: '새 카드 생성' },
  { key: 'F', description: '즐겨찾기 토글' },
  { key: 'ESC', description: '모달 닫기' },
  { key: '↑↓', description: '목록 네비게이션' },
  { key: 'Enter', description: '선택/실행' },
];

export const ShortcutHelp: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        aria-label="키보드 단축키 도움말"
        className="p-2 text-neutral-500 hover:text-neutral-700"
      >
        <QuestionMarkCircleIcon className="w-5 h-5" />
      </button>

      <Modal
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        title="키보드 단축키"
      >
        <div className="space-y-3">
          {shortcuts.map((shortcut, index) => (
            <div key={index} className="flex justify-between items-center">
              <span className="text-sm text-neutral-600">
                {shortcut.description}
              </span>
              <kbd className="px-2 py-1 text-xs bg-neutral-100 border border-neutral-300 rounded">
                {shortcut.key}
              </kbd>
            </div>
          ))}
        </div>
      </Modal>
    </>
  );
};
```

## 포커스 관리

### 1. 포커스 트랩
```typescript
// shared/hooks/useFocusTrap.ts
export const useFocusTrap = (isActive: boolean) => {
  const containerRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!isActive || !containerRef.current) return;

    const container = containerRef.current;
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0] as HTMLElement;
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;

    const handleTabKey = (event: KeyboardEvent) => {
      if (event.key !== 'Tab') return;

      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          event.preventDefault();
          lastElement?.focus();
        }
      } else {
        if (document.activeElement === lastElement) {
          event.preventDefault();
          firstElement?.focus();
        }
      }
    };

    // 첫 번째 요소에 포커스
    firstElement?.focus();

    container.addEventListener('keydown', handleTabKey);
    return () => container.removeEventListener('keydown', handleTabKey);
  }, [isActive]);

  return containerRef;
};

// 사용 예시 - 모달
const Modal: React.FC<ModalProps> = ({ isOpen, children }) => {
  const focusTrapRef = useFocusTrap(isOpen);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div 
        ref={focusTrapRef}
        role="dialog"
        aria-modal="true"
        className="modal-content"
      >
        {children}
      </div>
    </div>
  );
};
```

### 2. 포커스 복원
```typescript
// shared/hooks/useFocusRestore.ts
export const useFocusRestore = (isActive: boolean) => {
  const previousActiveElement = useRef<HTMLElement | null>(null);

  useEffect(() => {
    if (isActive) {
      previousActiveElement.current = document.activeElement as HTMLElement;
    } else if (previousActiveElement.current) {
      previousActiveElement.current.focus();
      previousActiveElement.current = null;
    }
  }, [isActive]);
};
```

이 접근성 가이드라인은 WCAG 2.1 AA 기준을 충족하며, 모든 사용자가 애플리케이션을 효과적으로 사용할 수 있도록 보장합니다.
