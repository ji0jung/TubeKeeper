#!/bin/bash

# Unit 1 Authentication Service - Production Ready 배포 스크립트
# 모든 트러블슈팅 경험을 반영한 완전한 배포 프로세스

set -e

# 설정
REGION="us-east-1"
STACK_PREFIX="aidlc-auth-staging"
ECR_REPO="147997118879.dkr.ecr.us-east-1.amazonaws.com/aidlc-auth-staging"
PROJECT_ROOT="/Users/jhrhee/Documents/private/project"
CF_ROOT="../../operation/unit1_authentication/cloudformation"

echo "🚀 Unit 1 Authentication Service - Production Ready 배포 시작..."
echo "📍 Region: $REGION"
echo "📦 Stack Prefix: $STACK_PREFIX"
echo "🐳 ECR Repository: $ECR_REPO"

# 함수 정의
check_stack_status() {
    local stack_name=$1
    local status=$(aws cloudformation describe-stacks --stack-name $stack_name --region $REGION --query 'Stacks[0].StackStatus' --output text 2>/dev/null || echo "NOT_EXISTS")
    echo $status
}

wait_for_stack() {
    local stack_name=$1
    local expected_status=$2
    echo "⏳ $stack_name 스택 상태 대기 중..."
    
    while true; do
        local status=$(check_stack_status $stack_name)
        echo "   현재 상태: $status"
        
        if [[ "$status" == "$expected_status" ]]; then
            echo "✅ $stack_name 스택 배포 완료"
            break
        elif [[ "$status" == *"FAILED"* ]] || [[ "$status" == *"ROLLBACK"* ]]; then
            echo "❌ $stack_name 스택 배포 실패: $status"
            exit 1
        fi
        
        sleep 30
    done
}

# 1. VPC 인프라 배포
echo "📡 1. VPC 인프라 배포..."
aws cloudformation deploy \
  --template-file $CF_ROOT/01-vpc-infrastructure.yaml \
  --stack-name ${STACK_PREFIX}-vpc \
  --region $REGION \
  --no-fail-on-empty-changeset

wait_for_stack "${STACK_PREFIX}-vpc" "CREATE_COMPLETE"

# 2. 보안 그룹 배포
echo "🔒 2. 보안 그룹 배포..."
aws cloudformation deploy \
  --template-file $CF_ROOT/02-security-groups.yaml \
  --stack-name ${STACK_PREFIX}-security-groups \
  --region $REGION \
  --no-fail-on-empty-changeset

wait_for_stack "${STACK_PREFIX}-security-groups" "CREATE_COMPLETE"

# 3. 데이터베이스 배포 (RDS + ElastiCache)
echo "🗄️ 3. 데이터베이스 배포..."
aws cloudformation deploy \
  --template-file $CF_ROOT/03-database.yaml \
  --stack-name ${STACK_PREFIX}-database \
  --region $REGION \
  --no-fail-on-empty-changeset

wait_for_stack "${STACK_PREFIX}-database" "CREATE_COMPLETE"

# 4. IAM 역할 배포
echo "👤 4. IAM 역할 배포..."
aws cloudformation deploy \
  --template-file $CF_ROOT/05-iam-roles.yaml \
  --stack-name ${STACK_PREFIX}-iam \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION \
  --no-fail-on-empty-changeset

wait_for_stack "${STACK_PREFIX}-iam" "CREATE_COMPLETE"

# 5. VPC 엔드포인트 배포 (ECR 연결용)
echo "🔗 5. VPC 엔드포인트 배포..."
aws cloudformation deploy \
  --template-file $CF_ROOT/09-vpc-endpoints.yaml \
  --stack-name ${STACK_PREFIX}-vpc-endpoints \
  --region $REGION \
  --no-fail-on-empty-changeset

wait_for_stack "${STACK_PREFIX}-vpc-endpoints" "CREATE_COMPLETE"

# 6. S3 Gateway 엔드포인트 배포
echo "🪣 6. S3 Gateway 엔드포인트 배포..."
aws cloudformation deploy \
  --template-file $CF_ROOT/11-s3-gateway-endpoint.yaml \
  --stack-name ${STACK_PREFIX}-s3-endpoint \
  --region $REGION \
  --no-fail-on-empty-changeset

wait_for_stack "${STACK_PREFIX}-s3-endpoint" "CREATE_COMPLETE"

# 7. Docker 이미지 빌드 및 푸시 (트러블슈팅 반영)
echo "🐳 7. Docker 이미지 빌드 및 푸시..."
cd $PROJECT_ROOT/aidlc-docs/construction/unit1_authentication

# ECR 로그인
echo "🔐 ECR 로그인..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_REPO

# 의존성 확인
echo "📦 의존성 확인..."
if ! grep -q "email-validator" requirements.txt; then
    echo "❌ email-validator 의존성이 누락되었습니다!"
    exit 1
fi

if ! grep -q "asyncpg" requirements.txt; then
    echo "❌ asyncpg 의존성이 누락되었습니다!"
    exit 1
fi

if ! grep -q "redis" requirements.txt; then
    echo "❌ redis 의존성이 누락되었습니다!"
    exit 1
fi

echo "✅ 모든 의존성 확인 완료"

# 멀티 플랫폼 이미지 빌드 및 푸시 (AMD64 플랫폼 명시)
echo "🔨 Docker 이미지 빌드 중..."
docker buildx build --platform linux/amd64 -t ${ECR_REPO}:latest --push .

echo "✅ Docker 이미지 푸시 완료"

cd $PROJECT_ROOT

# 8. ECS 클러스터 및 서비스 배포
echo "🚢 8. ECS 클러스터 및 서비스 배포..."
aws cloudformation deploy \
  --template-file $CF_ROOT/10-ecs-service.yaml \
  --stack-name ${STACK_PREFIX}-ecs \
  --capabilities CAPABILITY_NAMED_IAM \
  --region $REGION \
  --no-fail-on-empty-changeset

wait_for_stack "${STACK_PREFIX}-ecs" "CREATE_COMPLETE"

# 9. 모니터링 배포
echo "📊 9. 모니터링 배포..."
if [ -f "$PROJECT_ROOT/aidlc-docs/construction/unit1_authentication/monitoring.yaml" ]; then
    aws cloudformation deploy \
      --template-file $CF_ROOT/07-monitoring.yaml \
      --stack-name ${STACK_PREFIX}-monitoring \
      --region $REGION \
      --no-fail-on-empty-changeset
    
    wait_for_stack "${STACK_PREFIX}-monitoring" "CREATE_COMPLETE"
else
    echo "⚠️ 모니터링 템플릿을 찾을 수 없습니다. 건너뜁니다."
fi

# 10. 배포 후 검증
echo "🔍 10. 배포 후 검증..."

# ECS 서비스 상태 확인
echo "📋 ECS 서비스 상태 확인..."
ECS_STATUS=$(aws ecs describe-services \
  --cluster ${STACK_PREFIX}-cluster \
  --services ${STACK_PREFIX}-auth-service \
  --region $REGION \
  --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount,Pending:pendingCount}' \
  --output table)

echo "$ECS_STATUS"

# ALB DNS 이름 가져오기
echo "🌐 ALB DNS 이름 확인..."
ALB_DNS=$(aws cloudformation describe-stacks \
  --stack-name ${STACK_PREFIX}-ecs \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
  --output text)

echo "🔗 ALB DNS: http://$ALB_DNS"

# 헬스 체크
echo "❤️ 헬스 체크 수행..."
sleep 30  # 서비스 시작 대기

HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" "http://$ALB_DNS/health" || echo "000")

if [ "$HEALTH_CHECK" = "200" ]; then
    echo "✅ 헬스 체크 성공"
else
    echo "❌ 헬스 체크 실패 (HTTP $HEALTH_CHECK)"
    echo "🔍 ECS 태스크 로그를 확인하세요:"
    echo "aws logs describe-log-streams --log-group-name '/ecs/staging-aidlc-auth' --region $REGION"
fi

# Redis 연결 확인
echo "🔴 Redis 연결 확인..."
REDIS_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name ${STACK_PREFIX}-database \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`RedisEndpoint`].OutputValue' \
  --output text)

echo "📍 Redis Endpoint: $REDIS_ENDPOINT"

# PostgreSQL 연결 확인
echo "🐘 PostgreSQL 연결 확인..."
DB_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name ${STACK_PREFIX}-database \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
  --output text)

echo "📍 Database Endpoint: $DB_ENDPOINT"

# 11. 배포 완료 요약
echo ""
echo "🎉 Unit 1 Authentication Service 배포 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 ALB DNS: http://$ALB_DNS"
echo "📋 API 문서: http://$ALB_DNS/docs"
echo "❤️ 헬스 체크: http://$ALB_DNS/health"
echo "🔴 Redis: $REDIS_ENDPOINT:6379"
echo "🐘 PostgreSQL: $DB_ENDPOINT:5432"
echo ""
echo "📊 주요 엔드포인트:"
echo "  - POST /api/auth/register - 회원가입"
echo "  - POST /api/auth/verify-registration - 회원가입 인증"
echo "  - POST /api/auth/login - 로그인"
echo "  - POST /api/auth/verify-login - 로그인 인증"
echo ""
echo "🔍 모니터링:"
echo "  - CloudWatch 로그: /ecs/staging-aidlc-auth"
echo "  - ECS 클러스터: ${STACK_PREFIX}-cluster"
echo "  - ECS 서비스: ${STACK_PREFIX}-auth-service"
echo ""
echo "🚨 트러블슈팅 가이드: ./TROUBLESHOOTING.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
