# Unit1 Authentication API 명세서

## 📋 개요

**서비스명**: AIDLC Authentication & Profile Management  
**버전**: v0.1.0  
**베이스 URL**: `https://auth.aidlc.com` (배포 후)  
**로컬 개발**: `http://localhost:8001`  
**인증 방식**: JWT Bearer Token  

## 🔐 인증 플로우

### 1. 회원가입 플로우
```mermaid
sequenceDiagram
    Client->>API: POST /api/auth/register
    API->>Email: 인증 코드 발송
    API->>Client: 성공 응답
    Client->>API: POST /api/auth/verify-registration
    API->>DB: 사용자 생성
    API->>Client: 토큰 발급
```

### 2. 로그인 플로우
```mermaid
sequenceDiagram
    Client->>API: POST /api/auth/login
    API->>Email: 인증 코드 발송
    API->>Client: 성공 응답
    Client->>API: POST /api/auth/verify-login
    API->>Client: 토큰 발급
```

## 📡 API 엔드포인트

### 1. 회원가입 요청

**POST** `/api/auth/register`

이메일 기반 회원가입을 요청하고 인증 코드를 발송합니다.

#### Request Body
```json
{
  "email": "user@example.com",
  "gender": "male",           // optional: "male", "female", "other"
  "birth_year": 1990          // optional: 1900-2025
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "message": "인증 코드가 이메일로 발송되었습니다."
}
```

#### Response (400 Bad Request)
```json
{
  "success": false,
  "message": "이미 존재하는 이메일입니다."
}
```

---

### 2. 회원가입 인증

**POST** `/api/auth/verify-registration`

회원가입 인증 코드를 검증하고 계정을 생성합니다.

#### Request Body
```json
{
  "email": "user@example.com",
  "verification_code": "123456"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "message": "회원가입이 완료되었습니다.",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
  }
}
```

#### Response (400 Bad Request)
```json
{
  "success": false,
  "message": "잘못된 인증 코드입니다."
}
```

---

### 3. 로그인 요청

**POST** `/api/auth/login`

이메일 기반 로그인을 요청하고 인증 코드를 발송합니다.

#### Request Body
```json
{
  "email": "user@example.com"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "message": "인증 코드가 이메일로 발송되었습니다."
}
```

#### Response (400 Bad Request)
```json
{
  "success": false,
  "message": "존재하지 않거나 비활성화된 계정입니다."
}
```

---

### 4. 로그인 인증

**POST** `/api/auth/verify-login`

로그인 인증 코드를 검증하고 JWT 토큰을 발급합니다.

#### Request Body
```json
{
  "email": "user@example.com",
  "verification_code": "123456"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "message": "로그인이 완료되었습니다.",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
  }
}
```

#### Response (400 Bad Request)
```json
{
  "success": false,
  "message": "잘못된 인증 코드입니다."
}
```

---

### 5. 헬스 체크

**GET** `/health`

서비스 상태를 확인합니다.

#### Response (200 OK)
```json
{
  "status": "healthy"
}
```

---

## 🔒 인증 헤더

보호된 엔드포인트 접근 시 JWT 토큰을 헤더에 포함해야 합니다.

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## ❌ 오류 코드

### HTTP 상태 코드
- `200` - 성공
- `400` - 잘못된 요청
- `401` - 인증 실패
- `404` - 리소스 없음
- `422` - 유효성 검사 실패
- `500` - 서버 오류

### 비즈니스 오류 코드
| 코드 | 설명 |
|------|------|
| `AUTH_001` | 잘못된 자격 증명 |
| `AUTH_002` | 토큰 만료 |
| `AUTH_003` | 계정을 찾을 수 없음 |
| `AUTH_004` | 이메일이 이미 존재함 |

### 오류 응답 형식
```json
{
  "success": false,
  "error": {
    "code": "AUTH_001",
    "message": "잘못된 자격 증명입니다.",
    "details": {
      "field": "email",
      "reason": "Invalid format"
    }
  }
}
```

## 📝 요청/응답 예시

### cURL 예시

#### 회원가입
```bash
curl -X POST "https://auth.aidlc.com/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "gender": "male",
    "birth_year": 1990
  }'
```

#### 로그인
```bash
curl -X POST "https://auth.aidlc.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com"
  }'
```

### JavaScript 예시

```javascript
// 회원가입
const registerResponse = await fetch('/api/auth/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'john@example.com',
    gender: 'male',
    birth_year: 1990
  })
});

const registerData = await registerResponse.json();

// 인증 코드 검증
const verifyResponse = await fetch('/api/auth/verify-registration', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'john@example.com',
    verification_code: '123456'
  })
});

const verifyData = await verifyResponse.json();
const token = verifyData.token;

// 토큰 저장
localStorage.setItem('authToken', token);
```

## 🔄 레이트 리미팅

### 제한 사항
- 인증 코드 요청: 1분당 1회
- API 호출: 분당 100회
- 로그인 시도: 5분당 5회

### 헤더
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1635724800
```

## 📊 모니터링

### 메트릭
- 응답 시간: 평균 < 200ms
- 성공률: > 99.9%
- 가용성: > 99.95%

### 로그 형식
```json
{
  "timestamp": "2025-10-23T14:30:00Z",
  "level": "INFO",
  "endpoint": "/api/auth/register",
  "method": "POST",
  "status_code": 200,
  "response_time_ms": 150,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "ip_address": "192.168.1.100"
}
```

---

**문서 버전**: v1.0  
**최종 업데이트**: 2025-10-23  
**담당자**: AIDLC 개발팀
