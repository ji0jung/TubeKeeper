# AIDLC Unit1 Authentication Service - AWS 배포

## 📋 개요

Unit1 Authentication & Profile Management 서비스를 AWS에 배포하기 위한 완전한 CloudFormation 템플릿과 배포 스크립트를 제공합니다.

## 🏗️ 아키텍처

- **컨테이너**: ECS Fargate
- **로드 밸런서**: Application Load Balancer (ALB)
- **데이터베이스**: RDS PostgreSQL (Multi-AZ)
- **캐시**: ElastiCache Redis
- **네트워크**: VPC with Public/Private Subnets
- **보안**: Security Groups, IAM Roles, Secrets Manager
- **모니터링**: CloudWatch Logs, Metrics, Alarms

## 📊 배포 상태

### ✅ 현재 배포 완료
- **환경**: Staging
- **ALB DNS**: `staging-aidlc-alb-809271486.us-east-1.elb.amazonaws.com`
- **상태**: 운영 중 (모든 API 테스트 완료)
- **배포일**: 2025-10-25

### 배포된 스택들
- `aidlc-auth-staging-network` - VPC 및 네트워크
- `aidlc-auth-staging-security-groups` - 보안 그룹
- `aidlc-auth-staging-database` - RDS + ElastiCache
- `aidlc-auth-staging-iam` - IAM 역할
- `aidlc-auth-staging-ecs-alb` - ECS + ALB
- `aidlc-auth-staging-monitoring` - CloudWatch

### 방법 1: 2단계 배포 (권장)

가장 안전하고 체계적인 배포 방법입니다.

```bash
# 실행 권한 부여
chmod +x scripts/deploy-with-bucket.sh

# 배포 실행
./scripts/deploy-with-bucket.sh
```

**배포 단계:**
1. 프라이빗 S3 버킷 생성 (CloudFormation 템플릿 저장용)
2. 모든 템플릿을 S3에 업로드
3. Docker 이미지 빌드 및 ECR 푸시
4. 마스터 스택으로 전체 인프라 배포

### 방법 2: 개별 스택 배포

각 스택을 개별적으로 배포하는 방법입니다.

```bash
# 실행 권한 부여
chmod +x scripts/deploy.sh

# 배포 실행
./scripts/deploy.sh
```

## 📁 CloudFormation 템플릿 구조

```
cloudformation/
├── 00-master-stack.yaml      # 마스터 스택 (모든 스택 통합)
├── 01-network.yaml           # VPC, 서브넷, NAT Gateway
├── 02-security-groups.yaml   # 보안 그룹
├── 03-database.yaml          # RDS PostgreSQL + ElastiCache Redis
├── 04-ecs-alb.yaml          # ECS Cluster + ALB + Service
├── 05-iam-roles.yaml        # IAM 역할 및 정책
├── 06-ecr.yaml              # ECR 리포지토리
├── 07-monitoring.yaml       # CloudWatch 모니터링
└── 08-s3-bucket.yaml        # S3 버킷 (프라이빗, 보안 강화)
```

## 🔧 사전 요구사항

### 필수 도구
- AWS CLI (v2.0+)
- Docker
- jq (JSON 처리)

### AWS 권한
다음 AWS 서비스에 대한 권한이 필요합니다:
- CloudFormation
- EC2 (VPC, Security Groups)
- ECS
- RDS
- ElastiCache
- ECR
- IAM
- S3
- CloudWatch
- Secrets Manager
- Systems Manager (Parameter Store)

### 설정 확인
```bash
# AWS CLI 설정 확인
aws sts get-caller-identity

# Docker 실행 확인
docker --version

# jq 설치 확인
jq --version
```

## 🔒 보안 설정

### 자동 생성되는 보안 요소
- **데이터베이스 비밀번호**: AWS Secrets Manager에서 자동 생성
- **JWT 비밀 키**: AWS Systems Manager Parameter Store에 저장
- **S3 버킷**: 완전 프라이빗, 퍼블릭 액세스 차단
- **보안 그룹**: 최소 권한 원칙 적용

### 환경 변수
애플리케이션에서 사용하는 환경 변수들:
- `DATABASE_URL`: Parameter Store에서 자동 구성
- `REDIS_URL`: Parameter Store에서 자동 구성
- `JWT_SECRET_KEY`: Parameter Store에서 자동 구성
- `SES_SENDER_EMAIL`: jhrhee@amazon.com

## 📊 모니터링

### CloudWatch 대시보드
배포 완료 후 다음 메트릭을 모니터링할 수 있습니다:
- ECS 서비스 CPU/메모리 사용률
- ALB 응답 시간 및 요청 수
- RDS 데이터베이스 성능
- ElastiCache Redis 성능

### 알람 설정
다음 조건에서 알람이 발생합니다:
- ECS CPU 사용률 > 80%
- ECS 메모리 사용률 > 80%
- ALB 응답 시간 > 5초
- RDS CPU 사용률 > 80%

## 🧪 배포 후 테스트

### 헬스 체크
```bash
# 실제 배포된 ALB DNS 사용
curl http://staging-aidlc-alb-809271486.us-east-1.elb.amazonaws.com/health

# API 문서 확인
open http://staging-aidlc-alb-809271486.us-east-1.elb.amazonaws.com/docs
```

### API 테스트
```bash
# ALB DNS 이름 확인 (실제 배포된 DNS)
ALB_DNS="staging-aidlc-alb-809271486.us-east-1.elb.amazonaws.com"

# 헬스 체크
curl http://$ALB_DNS/health

# API 문서 확인
curl http://$ALB_DNS/docs

# 회원가입 테스트
curl -X POST http://$ALB_DNS/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "gender": "male", "birth_year": 1990}'
```

## 🗑️ 리소스 정리

### 전체 스택 삭제
```bash
# 마스터 스택 삭제 (모든 하위 스택 포함)
aws cloudformation delete-stack --stack-name aidlc-auth-staging-master

# S3 버킷 스택 삭제 (별도)
aws cloudformation delete-stack --stack-name aidlc-auth-staging-s3-bucket
```

### ECR 이미지 정리
```bash
# ECR 리포지토리의 모든 이미지 삭제
aws ecr batch-delete-image \
  --repository-name aidlc-auth-staging \
  --image-ids imageTag=latest
```

## 💰 예상 비용

### 스테이징 환경 (월간)
- ECS Fargate (0.25 vCPU, 0.5GB): ~$15
- RDS db.t3.micro: ~$15
- ElastiCache cache.t3.micro: ~$12
- ALB: ~$20
- NAT Gateway: ~$45
- **총 예상 비용**: ~$107/월

## 🔄 업데이트 및 롤백

### 애플리케이션 업데이트
```bash
# 실제 배포된 클러스터와 서비스 이름 사용
aws ecs update-service \
  --cluster staging-aidlc-cluster \
  --service staging-aidlc-auth-service \
  --force-new-deployment
```

### 롤백
```bash
# CloudFormation 스택 롤백
aws cloudformation cancel-update-stack \
  --stack-name aidlc-auth-staging-ecs-alb
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. CloudFormation 스택 이벤트
2. ECS 서비스 로그: `aws logs describe-log-streams --log-group-name "/ecs/staging-aidlc-auth"`
3. 실시간 로그: `aws logs tail /ecs/staging-aidlc-auth --follow`

---

**작성일**: 2025-10-25  
**버전**: 1.1  
**상태**: 배포 완료 및 운영 중
