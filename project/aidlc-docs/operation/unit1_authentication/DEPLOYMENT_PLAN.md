# Unit1 Authentication Service - AWS 배포 계획

## 📋 배포 개요

**서비스명**: AIDLC Authentication & Profile Management  
**아키텍처**: 헥사고날 아키텍처 + FastAPI + PostgreSQL + Redis  
**배포 방식**: AWS ECS Fargate + CloudFormation  
**환경**: 개발(dev), 스테이징(staging), 프로덕션(prod)

## 🏗️ AWS 인프라 아키텍처

```
Internet Gateway
    │
Application Load Balancer (ALB)
    │
ECS Fargate Service (Auto Scaling)
    │
┌─────────────────┬─────────────────┐
│   RDS PostgreSQL   │   ElastiCache Redis   │
│   (Multi-AZ)       │   (Cluster Mode)      │
└─────────────────┴─────────────────┘
```

## 🔧 필요한 AWS 리소스

### 1. 네트워크 인프라
- **VPC**: 격리된 네트워크 환경
- **Public Subnets**: ALB 배치용 (2개 AZ)
- **Private Subnets**: ECS, RDS, Redis 배치용 (2개 AZ)
- **Internet Gateway**: 인터넷 연결
- **NAT Gateway**: Private 서브넷 아웃바운드 연결
- **Route Tables**: 라우팅 설정

### 2. 보안 그룹
- **ALB Security Group**: HTTP(80), HTTPS(443) 허용
- **ECS Security Group**: ALB에서만 접근 허용
- **RDS Security Group**: ECS에서만 접근 허용 (5432)
- **Redis Security Group**: ECS에서만 접근 허용 (6379)

### 3. 데이터베이스
- **RDS PostgreSQL**: 
  - 인스턴스 클래스: db.t3.micro (개발), db.t3.small (프로덕션)
  - Multi-AZ 배포 (고가용성)
  - 자동 백업 활성화
  - 암호화 활성화

### 4. 캐시
- **ElastiCache Redis**:
  - 노드 타입: cache.t3.micro (개발), cache.t3.small (프로덕션)
  - 클러스터 모드 비활성화 (단순 구성)
  - 암호화 활성화

### 5. 컨테이너 서비스
- **ECS Cluster**: Fargate 타입
- **Task Definition**: FastAPI 애플리케이션
- **ECS Service**: Auto Scaling 활성화
- **Application Load Balancer**: 트래픽 분산

### 6. IAM 역할
- **ECS Task Role**: 애플리케이션 권한
- **ECS Execution Role**: 컨테이너 실행 권한
- **CloudWatch Logs 권한**: 로그 수집

### 7. 모니터링
- **CloudWatch Logs**: 애플리케이션 로그
- **CloudWatch Metrics**: 성능 메트릭
- **CloudWatch Alarms**: 알람 설정

## ❓ 배포 전 확인 사항

### [Question] AWS 계정 및 리전 설정
**AWS 계정 ID**: _______________  
**배포 리전**: us-east-1 (기본값) 또는 다른 리전?  
**Answer**: us-east-1

### [Question] 도메인 및 SSL 설정
**도메인 이름**: auth.aidlc.com (예시) 또는 다른 도메인?  
**SSL 인증서**: AWS Certificate Manager 사용 또는 기존 인증서?  
**Answer**: ssl은 사용하지 않을래. domain name은 없어도 됨.

### [Question] 환경별 구성
**배포할 환경**: dev, staging, prod 중 어떤 환경부터 시작?  
**환경별 리소스 크기**: 개발환경은 최소 사양, 프로덕션은 확장 가능한 사양?  
**Answer**: 이건 행사 데모용 어플리케이션이야 스테이징 수준이면 충분할 것 같아. 모든 기능이 aws 내에서 정상 동작하면 됨.

### [Question] 데이터베이스 설정
**RDS 인스턴스 클래스**: db.t3.micro (개발용) 또는 더 큰 사양?  
**데이터베이스 이름**: aidlc_auth (기본값) 또는 다른 이름?  
**마스터 사용자명**: aidlc_user (기본값) 또는 다른 이름?  
**Answer**: 알아서 제안해줘.

### [Question] 보안 설정
**JWT 비밀 키**: AWS Systems Manager Parameter Store 사용?  
**데이터베이스 비밀번호**: AWS Secrets Manager 사용?  
**Answer**: 추천해줘

### [Question] 모니터링 및 알람
**CloudWatch 알람**: CPU, 메모리, 응답 시간 기준 알람 설정?  
**SNS 알림**: 알람 발생 시 이메일 또는 Slack 알림?  
**Answer**: 추천해줘. SNS 알림까지는 필요없어.

### [Question] CI/CD 파이프라인
**소스 코드 저장소**: GitHub, CodeCommit 등?  
**자동 배포**: CodePipeline + CodeBuild 사용?  
**Answer**: github

## 📦 배포 단계

### Phase 1: 기본 인프라 구축
1. VPC 및 네트워크 설정
2. 보안 그룹 생성
3. RDS PostgreSQL 생성
4. ElastiCache Redis 생성

### Phase 2: 컨테이너 인프라 구축
1. ECR 리포지토리 생성
2. ECS 클러스터 생성
3. Task Definition 생성
4. ALB 및 Target Group 생성

### Phase 3: 애플리케이션 배포
1. Docker 이미지 빌드 및 푸시
2. ECS 서비스 생성
3. 데이터베이스 마이그레이션
4. 헬스 체크 및 테스트

### Phase 4: 모니터링 및 최적화
1. CloudWatch 대시보드 설정
2. 알람 및 알림 설정
3. Auto Scaling 정책 설정
4. 성능 튜닝

## 💰 예상 비용 (월간, us-east-1 기준)

### 개발 환경
- **ECS Fargate**: ~$15 (0.25 vCPU, 0.5GB RAM)
- **RDS db.t3.micro**: ~$15
- **ElastiCache cache.t3.micro**: ~$12
- **ALB**: ~$20
- **NAT Gateway**: ~$45
- **총 예상 비용**: ~$107/월

### 프로덕션 환경
- **ECS Fargate**: ~$60 (1 vCPU, 2GB RAM, Auto Scaling)
- **RDS db.t3.small**: ~$30
- **ElastiCache cache.t3.small**: ~$25
- **ALB**: ~$20
- **NAT Gateway**: ~$45
- **총 예상 비용**: ~$180/월

## 🔄 롤백 계획

1. **CloudFormation 스택 롤백**: 이전 버전으로 자동 롤백
2. **ECS 서비스 롤백**: 이전 Task Definition으로 롤백
3. **데이터베이스 복원**: RDS 자동 백업에서 복원
4. **DNS 전환**: Route 53을 통한 트래픽 전환

---

**작성일**: 2025-10-23  
**작성자**: DevOps 팀  
**검토 필요**: 보안팀, 인프라팀, 개발팀
