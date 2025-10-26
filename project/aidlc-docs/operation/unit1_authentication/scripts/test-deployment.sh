#!/bin/bash

# AIDLC Unit1 Authentication Service - 배포 테스트 스크립트
set -e

# 설정 변수
PROJECT_NAME="aidlc-auth"
ENVIRONMENT="staging"
AWS_REGION="us-east-1"

# 색상 출력을 위한 함수
print_status() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

print_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

# ALB DNS 이름 가져오기
get_alb_dns() {
    aws cloudformation describe-stacks \
        --stack-name "$PROJECT_NAME-$ENVIRONMENT-ecs-alb" \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerDNS`].OutputValue' \
        --output text --region $AWS_REGION
}

# API 테스트 함수
test_api_endpoint() {
    local url=$1
    local method=$2
    local data=$3
    local expected_status=$4
    
    print_status "Testing $method $url"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$url")
    fi
    
    # 응답 본문과 상태 코드 분리
    body=$(echo "$response" | head -n -1)
    status_code=$(echo "$response" | tail -n 1)
    
    if [ "$status_code" -eq "$expected_status" ]; then
        print_success "✓ Status: $status_code"
        echo "Response: $body"
    else
        print_error "✗ Expected: $expected_status, Got: $status_code"
        echo "Response: $body"
        return 1
    fi
}

# 메인 테스트 함수
main() {
    print_status "Starting deployment test for AIDLC Unit1 Authentication Service..."
    
    # ALB DNS 이름 가져오기
    ALB_DNS=$(get_alb_dns)
    if [ -z "$ALB_DNS" ]; then
        print_error "Could not retrieve ALB DNS name. Is the deployment complete?"
        exit 1
    fi
    
    BASE_URL="http://$ALB_DNS"
    print_status "Testing deployment at: $BASE_URL"
    
    # 서비스가 시작될 때까지 대기
    print_status "Waiting for service to be ready..."
    sleep 30
    
    # 1. 헬스 체크 테스트
    print_status "=== Health Check Test ==="
    test_api_endpoint "$BASE_URL/health" "GET" "" 200
    
    # 2. API 문서 접근 테스트
    print_status "=== API Documentation Test ==="
    test_api_endpoint "$BASE_URL/docs" "GET" "" 200
    
    # 3. 회원가입 테스트
    print_status "=== Registration Test ==="
    registration_data='{
        "email": "test@example.com",
        "gender": "male",
        "birth_year": 1990
    }'
    test_api_endpoint "$BASE_URL/api/auth/register" "POST" "$registration_data" 200
    
    # 4. 존재하지 않는 사용자 로그인 테스트
    print_status "=== Non-existent User Login Test ==="
    login_data='{
        "email": "nonexistent@example.com"
    }'
    test_api_endpoint "$BASE_URL/api/auth/login" "POST" "$login_data" 200
    
    # 5. 잘못된 요청 테스트
    print_status "=== Invalid Request Test ==="
    invalid_data='{
        "email": "invalid-email"
    }'
    test_api_endpoint "$BASE_URL/api/auth/register" "POST" "$invalid_data" 422
    
    # 6. 존재하지 않는 엔드포인트 테스트
    print_status "=== 404 Test ==="
    test_api_endpoint "$BASE_URL/nonexistent" "GET" "" 404
    
    print_success "All tests completed successfully!"
    print_success "Deployment URL: $BASE_URL"
    print_success "Health Check: $BASE_URL/health"
    print_success "API Documentation: $BASE_URL/docs"
    
    # ECS 서비스 상태 확인
    print_status "=== ECS Service Status ==="
    aws ecs describe-services \
        --cluster "$PROJECT_NAME-$ENVIRONMENT-cluster" \
        --services "$PROJECT_NAME-$ENVIRONMENT-service" \
        --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}' \
        --region $AWS_REGION
    
    # CloudWatch 로그 확인 안내
    print_status "=== Monitoring Information ==="
    echo "CloudWatch Logs: /ecs/$PROJECT_NAME-$ENVIRONMENT"
    echo "ECS Cluster: $PROJECT_NAME-$ENVIRONMENT-cluster"
    echo "ECS Service: $PROJECT_NAME-$ENVIRONMENT-service"
}

# 스크립트 실행
main "$@"
