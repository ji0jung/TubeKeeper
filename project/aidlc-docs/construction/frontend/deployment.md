# 배포 및 빌드 최적화

## 프로덕션 빌드 설정

### 1. Vite 프로덕션 설정
```typescript
// vite.config.prod.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { resolve } from 'path';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react({
      // 프로덕션에서 React DevTools 제거
      babel: {
        plugins: [
          ['babel-plugin-react-remove-properties', { properties: ['data-testid'] }]
        ]
      }
    }),
    visualizer({
      filename: 'dist/stats.html',
      open: false,
      gzipSize: true,
    }),
  ],

  build: {
    // 소스맵 생성 (에러 추적용)
    sourcemap: true,
    
    // 청크 크기 경고 임계값
    chunkSizeWarningLimit: 1000,
    
    // 빌드 최적화
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // console.log 제거
        drop_debugger: true, // debugger 제거
      },
    },

    rollupOptions: {
      output: {
        // 청크 분할 전략
        manualChunks: {
          // 벤더 라이브러리
          'react-vendor': ['react', 'react-dom'],
          'router-vendor': ['react-router-dom'],
          'query-vendor': ['@tanstack/react-query'],
          'ui-vendor': ['@headlessui/react', '@heroicons/react'],
          
          // 기능별 청크
          'auth-feature': ['./src/features/auth'],
          'cards-feature': ['./src/features/cards'],
          'search-feature': ['./src/features/search'],
          'categories-feature': ['./src/features/categories'],
          'sharing-feature': ['./src/features/sharing'],
        },
        
        // 파일명 패턴
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name.split('.');
          const ext = info[info.length - 1];
          
          if (/\.(css)$/.test(assetInfo.name)) {
            return 'assets/css/[name]-[hash].[ext]';
          }
          if (/\.(png|jpe?g|svg|gif|tiff|bmp|ico)$/i.test(assetInfo.name)) {
            return 'assets/images/[name]-[hash].[ext]';
          }
          if (/\.(woff2?|eot|ttf|otf)$/i.test(assetInfo.name)) {
            return 'assets/fonts/[name]-[hash].[ext]';
          }
          
          return 'assets/[name]-[hash].[ext]';
        },
      },
    },
  },

  // CSS 최적화
  css: {
    postcss: {
      plugins: [
        require('tailwindcss'),
        require('autoprefixer'),
        require('cssnano')({
          preset: 'default',
        }),
      ],
    },
  },
});
```

### 2. 환경별 빌드 스크립트
```json
// package.json
{
  "scripts": {
    "build:dev": "vite build --mode development",
    "build:staging": "vite build --mode staging",
    "build:prod": "vite build --mode production --config vite.config.prod.ts",
    "build:analyze": "npm run build:prod && npx vite-bundle-analyzer dist/stats.html",
    "preview:prod": "vite preview --port 4173"
  }
}
```

## 환경변수 관리

### 1. 환경별 설정 파일
```bash
# .env.development
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_ENV=development
VITE_DEBUG=true
VITE_LOG_LEVEL=debug
VITE_ENABLE_MOCK=true
VITE_SENTRY_DSN=
```

```bash
# .env.staging
VITE_API_BASE_URL=https://staging-api.youtubeapp.com/api
VITE_APP_ENV=staging
VITE_DEBUG=true
VITE_LOG_LEVEL=info
VITE_ENABLE_MOCK=false
VITE_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

```bash
# .env.production
VITE_API_BASE_URL=https://api.youtubeapp.com/api
VITE_APP_ENV=production
VITE_DEBUG=false
VITE_LOG_LEVEL=error
VITE_ENABLE_MOCK=false
VITE_SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
VITE_GA_TRACKING_ID=G-XXXXXXXXXX
```

### 2. 환경 설정 타입 정의
```typescript
// src/shared/config/env.ts
interface Environment {
  API_BASE_URL: string;
  APP_ENV: 'development' | 'staging' | 'production';
  DEBUG: boolean;
  LOG_LEVEL: 'debug' | 'info' | 'warn' | 'error';
  ENABLE_MOCK: boolean;
  SENTRY_DSN?: string;
  GA_TRACKING_ID?: string;
}

const getEnvVar = (key: string, defaultValue?: string): string => {
  const value = import.meta.env[key] || defaultValue;
  if (!value) {
    throw new Error(`Environment variable ${key} is required`);
  }
  return value;
};

export const env: Environment = {
  API_BASE_URL: getEnvVar('VITE_API_BASE_URL'),
  APP_ENV: getEnvVar('VITE_APP_ENV', 'development') as Environment['APP_ENV'],
  DEBUG: getEnvVar('VITE_DEBUG', 'false') === 'true',
  LOG_LEVEL: getEnvVar('VITE_LOG_LEVEL', 'info') as Environment['LOG_LEVEL'],
  ENABLE_MOCK: getEnvVar('VITE_ENABLE_MOCK', 'false') === 'true',
  SENTRY_DSN: import.meta.env.VITE_SENTRY_DSN,
  GA_TRACKING_ID: import.meta.env.VITE_GA_TRACKING_ID,
};

// 환경별 설정 검증
if (env.APP_ENV === 'production' && env.DEBUG) {
  console.warn('DEBUG mode is enabled in production');
}
```

## CDN 및 정적 자산 최적화

### 1. 이미지 최적화
```typescript
// src/shared/utils/imageOptimization.ts
interface ImageOptimizationOptions {
  width?: number;
  height?: number;
  quality?: number;
  format?: 'webp' | 'jpg' | 'png';
}

export const optimizeImageUrl = (
  originalUrl: string,
  options: ImageOptimizationOptions = {}
): string => {
  const { width, height, quality = 80, format = 'webp' } = options;

  // YouTube 썸네일 최적화
  if (originalUrl.includes('ytimg.com') || originalUrl.includes('youtube.com')) {
    if (width && width <= 320) {
      return originalUrl.replace(/maxresdefault|hqdefault/, 'mqdefault');
    }
    if (width && width <= 480) {
      return originalUrl.replace(/maxresdefault/, 'hqdefault');
    }
    return originalUrl;
  }

  // CDN을 통한 이미지 최적화 (예: Cloudinary, ImageKit 등)
  if (env.CDN_BASE_URL && originalUrl.startsWith(env.CDN_BASE_URL)) {
    const params = new URLSearchParams();
    if (width) params.append('w', width.toString());
    if (height) params.append('h', height.toString());
    params.append('q', quality.toString());
    params.append('f', format);
    
    return `${originalUrl}?${params.toString()}`;
  }

  return originalUrl;
};
```

### 2. 폰트 최적화
```css
/* src/styles/fonts.css */

/* 폰트 프리로드 */
@font-face {
  font-family: 'Pretendard';
  font-weight: 400;
  font-style: normal;
  font-display: swap; /* 폰트 로딩 최적화 */
  src: url('/fonts/Pretendard-Regular.woff2') format('woff2');
  unicode-range: U+AC00-D7AF, U+1100-11FF, U+3130-318F, U+A960-A97F, U+D7B0-D7FF;
}

@font-face {
  font-family: 'Pretendard';
  font-weight: 600;
  font-style: normal;
  font-display: swap;
  src: url('/fonts/Pretendard-SemiBold.woff2') format('woff2');
  unicode-range: U+AC00-D7AF, U+1100-11FF, U+3130-318F, U+A960-A97F, U+D7B0-D7FF;
}

/* 영문 폰트 fallback */
@font-face {
  font-family: 'Pretendard';
  font-weight: 400;
  font-style: normal;
  font-display: swap;
  src: url('/fonts/Pretendard-Regular-Latin.woff2') format('woff2');
  unicode-range: U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+2074, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD;
}
```

### 3. 정적 자산 캐싱 전략
```html
<!-- public/index.html -->
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  
  <!-- 폰트 프리로드 -->
  <link rel="preload" href="/fonts/Pretendard-Regular.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/fonts/Pretendard-SemiBold.woff2" as="font" type="font/woff2" crossorigin>
  
  <!-- DNS 프리페치 -->
  <link rel="dns-prefetch" href="//api.youtubeapp.com">
  <link rel="dns-prefetch" href="//ytimg.com">
  
  <!-- 중요한 CSS 인라인 -->
  <style>
    /* Critical CSS - 첫 화면 렌더링에 필요한 최소 스타일 */
    body { margin: 0; font-family: 'Pretendard', sans-serif; }
    .loading-screen { 
      position: fixed; 
      inset: 0; 
      display: flex; 
      align-items: center; 
      justify-content: center; 
      background: white; 
    }
  </style>
  
  <title>YouTube Link App</title>
</head>
<body>
  <div id="root">
    <div class="loading-screen">
      <div>로딩 중...</div>
    </div>
  </div>
  <script type="module" src="/src/main.tsx"></script>
</body>
</html>
```

## PWA 설정 (선택사항)

### 1. 매니페스트 파일
```json
// public/manifest.json
{
  "name": "YouTube Link App",
  "short_name": "YT Links",
  "description": "YouTube 링크를 체계적으로 저장하고 관리하는 앱",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#3b82f6",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "/icons/icon-72x72.png",
      "sizes": "72x72",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-96x96.png",
      "sizes": "96x96",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-128x128.png",
      "sizes": "128x128",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-144x144.png",
      "sizes": "144x144",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-152x152.png",
      "sizes": "152x152",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-384x384.png",
      "sizes": "384x384",
      "type": "image/png",
      "purpose": "maskable any"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "maskable any"
    }
  ]
}
```

### 2. Service Worker (기본)
```typescript
// public/sw.js
const CACHE_NAME = 'youtube-app-v1';
const STATIC_ASSETS = [
  '/',
  '/manifest.json',
  '/fonts/Pretendard-Regular.woff2',
  '/fonts/Pretendard-SemiBold.woff2',
];

// 설치 이벤트
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// 활성화 이벤트
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then(cacheNames => {
        return Promise.all(
          cacheNames
            .filter(cacheName => cacheName !== CACHE_NAME)
            .map(cacheName => caches.delete(cacheName))
        );
      })
      .then(() => self.clients.claim())
  );
});

// 네트워크 요청 처리
self.addEventListener('fetch', (event) => {
  // 정적 자산 캐싱
  if (event.request.destination === 'image') {
    event.respondWith(
      caches.match(event.request)
        .then(response => {
          if (response) return response;
          
          return fetch(event.request)
            .then(response => {
              if (response.status === 200) {
                const responseClone = response.clone();
                caches.open(CACHE_NAME)
                  .then(cache => cache.put(event.request, responseClone));
              }
              return response;
            });
        })
    );
  }
});
```

## 배포 자동화

### 1. GitHub Actions 워크플로우
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm run test:run
      
      - name: Build application
        run: npm run build:prod
        env:
          VITE_API_BASE_URL: ${{ secrets.VITE_API_BASE_URL }}
          VITE_SENTRY_DSN: ${{ secrets.VITE_SENTRY_DSN }}
          VITE_GA_TRACKING_ID: ${{ secrets.VITE_GA_TRACKING_ID }}
      
      - name: Deploy to S3
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Sync to S3
        run: |
          aws s3 sync dist/ s3://${{ secrets.S3_BUCKET_NAME }} --delete
          aws s3 cp dist/index.html s3://${{ secrets.S3_BUCKET_NAME }}/index.html --cache-control "no-cache"
      
      - name: Invalidate CloudFront
        run: |
          aws cloudfront create-invalidation --distribution-id ${{ secrets.CLOUDFRONT_DISTRIBUTION_ID }} --paths "/*"
      
      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          channel: '#deployments'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
        if: always()
```

### 2. Docker 배포 (선택사항)
```dockerfile
# Dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build:prod

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;
        
        # SPA 라우팅 지원
        location / {
            try_files $uri $uri/ /index.html;
        }
        
        # 정적 자산 캐싱
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
        
        # HTML 파일 캐싱 방지
        location ~* \.html$ {
            expires -1;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
        }
    }
}
```

이 배포 설정은 최적화된 프로덕션 빌드, 효율적인 자산 관리, 자동화된 배포 파이프라인을 제공합니다.
