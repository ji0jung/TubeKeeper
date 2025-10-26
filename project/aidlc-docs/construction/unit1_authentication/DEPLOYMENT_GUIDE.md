# Unit1 Authentication Service - 배포 가이드

## 🚀 배포 준비 체크리스트

### 1. 환경 설정
- [ ] AWS 계정 및 자격 증명 설정
- [ ] PostgreSQL 데이터베이스 준비
- [ ] Redis 캐시 서버 준비
- [ ] AWS SES 이메일 서비스 설정
- [ ] 도메인 및 SSL 인증서 준비

### 2. 코드 준비
- [x] 소스 코드 완성
- [x] 의존성 정의 (requirements.txt)
- [ ] 환경별 설정 파일 분리
- [ ] Docker 이미지 빌드
- [ ] 보안 설정 강화

## 📋 배포 옵션

### Option 1: AWS ECS + Fargate (추천)
**장점**: 서버리스, 자동 스케일링, 관리 부담 적음

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  auth-service:
    build: .
    ports:
      - "80:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
```

### Option 2: AWS Lambda + API Gateway
**장점**: 완전 서버리스, 비용 효율적

### Option 3: EC2 + Docker
**장점**: 완전한 제어, 커스터마이징 가능

## 🔧 필수 환경 변수

```bash
# 데이터베이스
DATABASE_URL=postgresql://user:password@host:5432/dbname
DB_HOST=your-rds-endpoint
DB_PORT=5432
DB_NAME=aidlc_auth
DB_USER=aidlc_user
DB_PASSWORD=secure_password

# Redis
REDIS_URL=redis://your-elasticache-endpoint:6379/0
REDIS_HOST=your-elasticache-endpoint
REDIS_PORT=6379

# JWT
JWT_SECRET_KEY=your-super-secure-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_DAYS=7

# AWS SES
AWS_REGION=us-east-1
SES_SENDER_EMAIL=jhrhee@amazon.com
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key

# 애플리케이션
APP_NAME=AIDLC Authentication Service
DEBUG=false
LOG_LEVEL=INFO
```

## 🐳 Docker 설정

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### .dockerignore
```
venv/
__pycache__/
*.pyc
.env
.git/
README.md
demo_*.py
test_*.py
```

## 🗄️ 데이터베이스 설정

### 1. RDS PostgreSQL 생성
```bash
# AWS CLI로 RDS 인스턴스 생성
aws rds create-db-instance \
  --db-instance-identifier aidlc-auth-db \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username aidlc_user \
  --master-user-password your_secure_password \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxxxxxx
```

### 2. 데이터베이스 마이그레이션
```bash
# Alembic 초기화 (필요시)
alembic init alembic

# 마이그레이션 생성
alembic revision --autogenerate -m "Initial tables"

# 마이그레이션 실행
alembic upgrade head
```

## 📧 AWS SES 설정

### 1. 이메일 주소 검증
```bash
# AWS CLI로 이메일 주소 검증
aws ses verify-email-identity --email-address jhrhee@amazon.com
```

### 2. 샌드박스 모드 해제 (프로덕션용)
- AWS 콘솔에서 SES 서비스로 이동
- "Sending statistics" → "Request a sending quota increase"

## 🔐 보안 설정

### 1. IAM 역할 생성
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*"
    }
  ]
}
```

### 2. 보안 그룹 설정
- 인바운드: HTTP(80), HTTPS(443)
- 아웃바운드: PostgreSQL(5432), Redis(6379)

## 📊 모니터링 설정

### 1. CloudWatch 로그
```python
# logging 설정 추가
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 2. 헬스 체크
- ELB 헬스 체크: `GET /health`
- 응답 코드: 200
- 체크 간격: 30초

## 🚀 배포 스크립트

### deploy.sh
```bash
#!/bin/bash
set -e

echo "🚀 AIDLC Authentication Service 배포 시작"

# 1. Docker 이미지 빌드
echo "📦 Docker 이미지 빌드 중..."
docker build -t aidlc-auth:latest .

# 2. ECR에 푸시
echo "📤 ECR에 이미지 푸시 중..."
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin your-account.dkr.ecr.us-east-1.amazonaws.com
docker tag aidlc-auth:latest your-account.dkr.ecr.us-east-1.amazonaws.com/aidlc-auth:latest
docker push your-account.dkr.ecr.us-east-1.amazonaws.com/aidlc-auth:latest

# 3. ECS 서비스 업데이트
echo "🔄 ECS 서비스 업데이트 중..."
aws ecs update-service --cluster aidlc-cluster --service aidlc-auth-service --force-new-deployment

echo "✅ 배포 완료!"
```

## 🧪 배포 후 테스트

### 1. 헬스 체크
```bash
curl https://your-domain.com/health
```

### 2. API 테스트
```bash
# 회원가입 테스트
curl -X POST "https://your-domain.com/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### 3. 로그 확인
```bash
# CloudWatch 로그 확인
aws logs tail /aws/ecs/aidlc-auth --follow
```

## 🔄 롤백 계획

### 1. 이전 버전으로 롤백
```bash
# ECS 서비스 이전 태스크 정의로 롤백
aws ecs update-service --cluster aidlc-cluster --service aidlc-auth-service --task-definition aidlc-auth:previous-version
```

### 2. 데이터베이스 롤백
```bash
# Alembic으로 마이그레이션 롤백
alembic downgrade -1
```

## 📈 성능 최적화

### 1. 캐싱 전략
- Redis를 활용한 세션 캐싱
- 인증 코드 임시 저장

### 2. 데이터베이스 최적화
- 인덱스 추가
- 커넥션 풀 설정

### 3. 로드 밸런싱
- ALB 설정
- 다중 AZ 배포

---

**배포 담당자**: DevOps 팀  
**검토 필요**: 보안팀, 인프라팀  
**예상 배포 시간**: 2-3시간
