#!/bin/bash

# AIDLC Unit1 Authentication Service - API 테스트 스크립트
set -e

# 설정 변수
PROJECT_NAME="aidlc-auth"
ENVIRONMENT="staging"
AWS_REGION="us-east-1"

# 색상 출력
print_status() { echo -e "\033[1;34m[INFO]\033[0m $1"; }
print_success() { echo -e "\033[1;32m[SUCCESS]\033[0m $1"; }
print_error() { echo -e "\033[1;31m[ERROR]\033[0m $1"; }

# ALB URL 가져오기
get_alb_url() {
    aws cloudformation describe-stacks \
        --stack-name "$PROJECT_NAME-$ENVIRONMENT-master" \
        --query 'Stacks[0].Outputs[?OutputKey==`ApplicationURL`].OutputValue' \
        --output text --region $AWS_REGION 2>/dev/null || \
    aws cloudformation describe-stacks \
        --stack-name "$PROJECT_NAME-$ENVIRONMENT-ecs-alb" \
        --query 'Stacks[0].Outputs[?OutputKey==`LoadBalancerURL`].OutputValue' \
        --output text --region $AWS_REGION
}

# API 테스트 함수
test_api() {
    local base_url=$1
    local test_email="test-$(date +%s)@example.com"
    
    print_status "Testing API endpoints at: $base_url"
    
    # 1. 헬스 체크
    print_status "1. Health Check"
    if curl -s -f "$base_url/health" > /dev/null; then
        print_success "Health check passed"
    else
        print_error "Health check failed"
        return 1
    fi
    
    # 2. API 문서 확인
    print_status "2. API Documentation"
    if curl -s -f "$base_url/docs" > /dev/null; then
        print_success "API docs accessible"
    else
        print_error "API docs not accessible"
    fi
    
    # 3. 회원가입 테스트
    print_status "3. User Registration"
    local register_response=$(curl -s -X POST "$base_url/api/v1/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"$test_email\"}")
    
    if echo "$register_response" | jq -e '.user_id' > /dev/null 2>&1; then
        print_success "User registration successful"
        local user_id=$(echo "$register_response" | jq -r '.user_id')
        echo "User ID: $user_id"
    else
        print_error "User registration failed"
        echo "Response: $register_response"
    fi
    
    # 4. 이메일 인증 코드 생성 테스트
    print_status "4. Email Verification Code Generation"
    local verify_response=$(curl -s -X POST "$base_url/api/v1/auth/send-verification" \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"$test_email\"}")
    
    if echo "$verify_response" | jq -e '.message' > /dev/null 2>&1; then
        print_success "Verification code sent"
    else
        print_error "Verification code generation failed"
        echo "Response: $verify_response"
    fi
    
    # 5. 프로필 조회 테스트 (인증 없이)
    print_status "5. Profile Access (should fail without auth)"
    local profile_response=$(curl -s -w "%{http_code}" "$base_url/api/v1/profile/me")
    local http_code="${profile_response: -3}"
    
    if [ "$http_code" = "401" ] || [ "$http_code" = "403" ]; then
        print_success "Profile protection working (HTTP $http_code)"
    else
        print_error "Profile protection not working (HTTP $http_code)"
    fi
    
    print_success "API tests completed"
}

# 메인 함수
main() {
    print_status "Starting API tests for AIDLC Unit1 Authentication Service"
    
    # ALB URL 가져오기
    local alb_url=$(get_alb_url)
    
    if [ -z "$alb_url" ]; then
        print_error "Could not retrieve ALB URL. Is the stack deployed?"
        exit 1
    fi
    
    print_status "ALB URL: $alb_url"
    
    # API 테스트 실행
    test_api "$alb_url"
}

# 필수 도구 확인
command -v aws >/dev/null 2>&1 || { print_error "AWS CLI is required"; exit 1; }
command -v curl >/dev/null 2>&1 || { print_error "curl is required"; exit 1; }
command -v jq >/dev/null 2>&1 || { print_error "jq is required"; exit 1; }

# 스크립트 실행
main "$@"
