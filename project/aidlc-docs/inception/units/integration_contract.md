# Integration Contract

## 개요
각 단위(Unit) 간의 통합을 위한 API 엔드포인트와 메소드를 정의합니다.

## Unit 1: User Authentication & Profile Management

### Authentication Service API
```
POST /api/auth/register
- 이메일 회원가입 요청
- Body: { email, gender?, birthYear? }
- Response: { success, message }

POST /api/auth/verify-registration
- 회원가입 인증 코드 확인
- Body: { email, verificationCode }
- Response: { success, token, user }

POST /api/auth/login
- 로그인 요청 (인증 코드 발송)
- Body: { email }
- Response: { success, message }

POST /api/auth/verify-login
- 로그인 인증 코드 확인
- Body: { email, verificationCode }
- Response: { success, token, user }

POST /api/auth/logout
- 로그아웃
- Headers: { Authorization: Bearer token }
- Response: { success }

POST /api/auth/refresh-session
- 세션 자동 연장
- Headers: { Authorization: Bearer token }
- Response: { success, newToken }

DELETE /api/auth/account
- 회원 탈퇴
- Headers: { Authorization: Bearer token }
- Response: { success }
```

### Profile Service API
```
GET /api/profile
- 프로필 정보 조회
- Headers: { Authorization: Bearer token }
- Response: { user: { email, gender, birthYear, language } }

PUT /api/profile
- 프로필 정보 수정
- Headers: { Authorization: Bearer token }
- Body: { gender?, birthYear?, language? }
- Response: { success, user }
```

## Unit 2: Category Management

### Category Service API
```
GET /api/categories
- 사용자 카테고리 목록 조회
- Headers: { Authorization: Bearer token }
- Response: { 
    success: true, 
    data: { 
      categories: [
        {
          id: UUID,
          name: string,
          card_count: number,
          is_deletable: boolean,
          category_type: "regular" | "shared_cards" | "temporary",
          parent_id: UUID | null,
          hierarchy_level: 1 | 2 | 3,
          created_at: ISO timestamp
        }
      ]
    }, 
    message: string 
  }

GET /api/categories/:id
- 개별 카테고리 조회
- Headers: { Authorization: Bearer token }
- Response: { 
    success: true, 
    data: { 
      category: {
        id: UUID,
        name: string,
        card_count: number,
        is_deletable: boolean,
        category_type: "regular" | "shared_cards" | "temporary",
        parent_id: UUID | null,
        hierarchy_level: 1 | 2 | 3,
        created_at: ISO timestamp
      }
    }, 
    message: string 
  }
- Errors:
  * 404: 카테고리를 찾을 수 없음 또는 접근 권한 없음

POST /api/categories
- 새 카테고리 생성
- Headers: { Authorization: Bearer token }
- Body: { name: string, parent_id?: UUID }
- Response: { 
    success: true, 
    data: { 
      category: {
        id: UUID,
        name: string,
        card_count: 0,
        is_deletable: true,
        category_type: "regular",
        parent_id: UUID | null,
        hierarchy_level: 1 | 2 | 3,
        created_at: ISO timestamp
      }
    }, 
    message: string 
  }
- Errors:
  * 400: 비즈니스 규칙 위반 (계층 제한, 중복 이름, 카테고리 수 제한 등)
  * 422: 입력 검증 실패 (이름 형식, 길이 등)

PUT /api/categories/:id
- 카테고리 이름 수정
- Headers: { Authorization: Bearer token }
- Body: { name: string }
- Response: { 
    success: true, 
    data: { 
      category: {
        id: UUID,
        name: string,
        card_count: number,
        is_deletable: boolean,
        category_type: string,
        parent_id: UUID | null,
        hierarchy_level: number,
        created_at: ISO timestamp
      }
    }, 
    message: string 
  }
- Errors:
  * 404: 카테고리를 찾을 수 없음 또는 접근 권한 없음
  * 400: 시스템 카테고리 수정 시도 또는 중복 이름

GET /api/categories/:id/deletion-preview
- 카테고리 삭제 미리보기
- Headers: { Authorization: Bearer token }
- Response: { 
    success: true, 
    data: {
      category_id: UUID,
      category_name: string,
      card_count: number,
      subcategory_count: number,
      subcategories: [{ id: UUID, name: string }],
      can_delete: boolean,
      requires_card_migration: boolean,
      requires_subcategory_migration: boolean
    }, 
    message: string 
  }
- Errors:
  * 404: 카테고리를 찾을 수 없음 또는 접근 권한 없음

DELETE /api/categories/:id
- 카테고리 삭제
- Headers: { Authorization: Bearer token }
- Response: { success: true, data: {}, message: string }
- Errors:
  * 404: 카테고리를 찾을 수 없음 또는 접근 권한 없음
  * 400: 시스템 카테고리 삭제 시도 또는 하위 카테고리/카드 존재
```

## Unit 3: Card Creation & Management

### Card Service API
```
POST /api/cards
- 새 카드 생성
- Headers: { Authorization: Bearer token }
- Body: { contentUrl, categoryId, memo?, tags? }
- Response: { success: true, data: { card_id, status }, message }
- Errors:
  * 422: 필수 필드 누락 또는 잘못된 UUID 형식
  * 200 + success:true + status:"ERROR": 잘못된 YouTube URL 형식
  * 200 + success:true + status:"DUPLICATE": 동일한 URL의 카드가 이미 존재
  * 500: 카드 생성 중 내부 오류 발생

GET /api/cards/:id
- 카드 상세 조회
- Headers: { Authorization: Bearer token }
- Response: { success: true, data: { card: {...} }, message }
- Errors:
  * 404: 카드를 찾을 수 없음 또는 접근 권한 없음
  * 422: 잘못된 UUID 형식

PUT /api/cards/:id
- 카드 정보 수정
- Headers: { Authorization: Bearer token }
- Body: { memo?, tags?, categoryId?, isPublic? }
- Response: { success: true, data: { card: {...} }, message }
- Errors:
  * 404: 카드를 찾을 수 없음 또는 수정 권한 없음
  * 400: 수정 실패 (잘못된 데이터)

POST /api/cards/:id/favorite
- 카드 즐겨찾기 토글
- Headers: { Authorization: Bearer token }
- Response: { success: true, data: { is_favorite }, message }
- Errors:
  * 404: 카드를 찾을 수 없음 또는 접근 권한 없음

POST /api/cards/:id/public
- 카드 공개 설정 토글
- Headers: { Authorization: Bearer token }
- Response: { success, is_public, message }
- Errors:
  * 404: 카드를 찾을 수 없음 또는 접근 권한 없음

DELETE /api/cards/:id
- 카드 삭제
- Headers: { Authorization: Bearer token }
- Response: { success: true, data: {}, message }
- Errors:
  * 404: 카드를 찾을 수 없음 또는 삭제 권한 없음
  * 400: 삭제 실패

GET /api/cards
- 사용자 카드 목록 조회 (커서 기반 페이지네이션)
- Headers: { Authorization: Bearer token }
- Query: { categoryId?, favorites_only?, cursor?, limit? }
- Response: { success: true, data: { cards: [...], nextCursor?, hasMore }, message }
- Errors:
  * 403: 인증되지 않은 접근
  * 422: 잘못된 페이지네이션 파라미터
```

### YouTube Integration API
```
POST /api/youtube/extract
- 유튜브 메타데이터 추출
- Headers: { Authorization: Bearer token }
- Body: { youtubeUrl }
- Response: { 
    success, 
    metadata: { 
      title, 
      thumbnail, 
      tags,
      duration,
      publishedAt
    } 
  }
- Errors:
  * 400: 잘못된 YouTube URL 형식
  * 500: YouTube API 호출 실패
  * 503: 서비스 일시적 사용 불가
```

### System Health API
```
GET /health
- 시스템 헬스체크
- Response: { status: "healthy", database: "connected", message: "All systems operational" }
- Errors:
  * 503: { status: "unhealthy", database: "disconnected", error: "..." }

GET /
- 서비스 정보
- Response: { service: "Unit3 Card Management System", version: "1.0.0", status: "running" }
```
## Unit 4: Card Search & Display

### My Cards Service API (커서 기반 페이징)
```
GET /api/my-cards
- 내 카드 목록 조회 (커서 기반 페이징)
- Headers: { Authorization: Bearer token }
- Query: { cursor?, limit?, categoryId?, search?, tag? }
- Response: { 
    success: true, 
    data: { 
      cards: [...], 
      nextCursor?, 
      hasMore 
    }, 
    message: "Success" 
  }
- Errors:
  * 400: 잘못된 검색 조건 (SEARCH_001, SEARCH_002, SEARCH_003)
  * 401: 인증 실패 (AUTH_002)
  * 422: 잘못된 페이징 파라미터 (SEARCH_010)

GET /api/my-cards/favorites
- 내 즐겨찾기 카드 목록 조회
- Headers: { Authorization: Bearer token }
- Query: { cursor?, limit? }
- Response: { 
    success: true, 
    data: { 
      cards: [...], 
      nextCursor?, 
      hasMore 
    }, 
    message: "Success" 
  }
```

### Public Cards Service API (오프셋 기반 페이징)
```
GET /api/public-cards
- 공개 카드 검색 (오프셋 기반 페이징)
- Headers: { Authorization: Bearer token }
- Query: { page?, limit?, search?, tag? }
- Note: search와 tag는 동시 사용 불가
- Response: { 
    success: true, 
    data: { 
      cards: [...], 
      totalCount, 
      currentPage, 
      totalPages 
    }, 
    message: "Success" 
  }
- Errors:
  * 400: 잘못된 검색 조건 (SEARCH_001, SEARCH_004)
  * 401: 인증 실패 (AUTH_002)
  * 422: 잘못된 페이징 파라미터 (SEARCH_010)

POST /api/public-cards/:id/save
- 공개 카드를 내 계정에 독립적으로 복사 저장
- Headers: { Authorization: Bearer token }
- Body: { categoryId? } // 미제공 시 "공유받은 카드" 카테고리 기본 사용
- Response: { 
    success: true, 
    data: { 
      newCard?, 
      alreadyExists 
    }, 
    message: "Card saved successfully" 
  }
- Errors:
  * 404: 공개 카드를 찾을 수 없음 (SEARCH_006)
  * 409: 이미 저장된 카드 (SEARCH_007)
  * 403: 저장 권한 없음 (SEARCH_008)
- Note: 원본과 완전히 독립된 새 카드로 생성, 원본 변경사항 반영 안됨
```

### Search Suggestions API
```
GET /api/search/suggestions
- 검색 자동완성 제안
- Headers: { Authorization: Bearer token }
- Query: { query, scope? } // scope: 'my' | 'public'
- Response: { 
    success: true, 
    data: { 
      suggestions: [{ type, value }] 
    }, 
    message: "Success" 
  }
- Errors:
  * 400: 잘못된 쿼리 (SEARCH_002, SEARCH_003)
  * 503: 검색 서비스 사용 불가 (SEARCH_009)

GET /api/tags
- 태그 목록 (내 카드 또는 공개 카드)
- Headers: { Authorization: Bearer token }
- Query: { scope? } // scope: 'my' | 'public'
- Response: { 
    success: true, 
    data: { 
      tags: [{ name, count }] 
    }, 
    message: "Success" 
  }
```

## Unit 5: Card Sharing

### Sharing Service API
```
POST /api/cards/:id/share
- 카드 공유 링크 생성
- Headers: { Authorization: Bearer token }
- Response: { 
    success: true, 
    data: { 
      shareUrl: string,
      shareToken: string, 
      expiresAt: string (ISO 8601)
    }, 
    message: string 
  }
- Errors:
  * 404: { success: false, error: { code: "CARD_001", message: "Card not found" } }
  * 403: { success: false, error: { code: "CARD_008", message: "Card access denied" } }
  * 429: { success: false, error: { code: "SHARE_011", message: "Rate limit exceeded" } }
  * 500: { success: false, error: { code: "SHARE_007", message: "Share link creation failed" } }

GET /api/shared/:shareId
- 공유 카드 조회 (인증 불필요)
- Headers: { User-Agent: string } (크롤러 감지용)
- Response (일반 사용자): { 
    success: true, 
    data: {
      card: { title, thumbnail, youtubeUrl, summary?, tags? },
      isExpired: false,
      expiresAt: string,
      accessCount?: number
    }, 
    message: string 
  }
- Response (크롤러): HTML with Open Graph meta tags
- Errors:
  * 404: { success: false, error: { code: "SHARE_002", message: "Share link not found" } }
  * 410: { success: false, error: { code: "SHARE_001", message: "Share link expired" } }
  * 422: { success: false, error: { code: "SHARE_003", message: "Invalid share token format" } }

POST /api/shared/:shareId/save
- 공유 카드를 내 계정에 독립적으로 복사 저장
- Headers: { Authorization: Bearer token }
- Body: { categoryId?: string } // 미제공 시 "공유받은 카드" 카테고리 사용
- Response: { 
    success: true, 
    data: { 
      newCard?: {
        id: string,
        title: string,
        categoryId: string,
        categoryName: string
      },
      alreadyExists?: boolean
    }, 
    message: string 
  }
- Errors:
  * 404: { success: false, error: { code: "SHARE_002", message: "Share link not found" } }
  * 410: { success: false, error: { code: "SHARE_001", message: "Share link expired" } }
  * 409: { success: false, error: { code: "SHARE_013", message: "Card already exists" } }
  * 422: { success: false, error: { code: "CATEGORY_001", message: "Category not found" } }
- Note: 원본과 완전히 독립된 새 카드로 생성
```

## Unit 6: User Experience & UI

### System Service API
```
GET /api/system/health
- 시스템 상태 확인
- Response: { status, services: { auth, database, youtube } }

GET /api/system/config
- 클라이언트 설정 정보
- Response: { 
    supportedLanguages: ['ko', 'en'],
    maxFileSize,
    sessionTimeout 
  }
```

## 공통 응답 형식

### 성공 응답
```json
{
  "success": true,
  "data": { ... },
  "message": "Success message"
}
```

### 오류 응답
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": { ... }
  }
}
```

## 인증 및 권한

- 모든 보호된 엔드포인트는 `Authorization: Bearer <token>` 헤더 필요
- JWT 토큰 기반 인증
- 토큰 만료 시간: 7일 (활동 시 자동 연장)
- 세션 만료 시 401 Unauthorized 응답

## 오류 코드

```
AUTH_001: Invalid credentials
AUTH_002: Token expired
AUTH_003: Account not found
AUTH_004: Email already exists
CARD_001: Card not found
CARD_002: Invalid YouTube URL
CARD_003: YouTube API error
CARD_004: Duplicate card exists
CARD_005: Thumbnail processing failed
CARD_006: Card creation in progress
CARD_007: Invalid card status transition
CARD_008: Card access denied (권한 없음)
CARD_009: Invalid card data format
CARD_010: Card update failed
CARD_011: Card deletion failed
CARD_012: Invalid pagination parameters
CARD_013: Metadata collection failed
CARD_014: Card not accessible by user
CATEGORY_001: Category not found
CATEGORY_002: Category not empty
CATEGORY_003: Category name already exists
CATEGORY_004: Category limit exceeded
CATEGORY_005: Invalid category name format
CATEGORY_006: Cannot delete system category
CATEGORY_007: Cannot move to descendant category
CATEGORY_008: Maximum hierarchy level exceeded
CATEGORY_009: Cannot delete category with subcategories
SEARCH_001: Invalid search criteria
SEARCH_002: Search query too short
SEARCH_003: Search query too long
SEARCH_004: Invalid tag format
SEARCH_005: Category not accessible
SEARCH_006: Public card not found
SEARCH_007: Card already saved
SEARCH_008: Save permission denied
SEARCH_009: Search service unavailable
SEARCH_010: Invalid pagination parameters
SHARE_001: Share link expired
SHARE_002: Share link not found
SHARE_003: Invalid share token format
SHARE_004: Invalid expiration date
SHARE_005: Invalid share URL format
SHARE_006: Invalid metadata format
SHARE_007: Share link creation failed
SHARE_008: Card not shareable
SHARE_009: Share link access denied
SHARE_010: Metadata generation failed
SHARE_011: Rate limit exceeded for share link creation
SHARE_012: Shared category not found
SHARE_013: Card already exists in user collection
```
