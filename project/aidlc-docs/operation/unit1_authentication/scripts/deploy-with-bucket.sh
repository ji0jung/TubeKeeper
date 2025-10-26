#!/bin/bash

# AIDLC Unit1 Authentication Service - 2단계 배포 스크립트
# 1단계: S3 버킷 생성 및 템플릿 업로드
# 2단계: 마스터 스택으로 전체 인프라 배포

set -e

# 설정 변수
PROJECT_NAME="aidlc-auth"
ENVIRONMENT="staging"
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

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

# 1단계: S3 버킷 생성
create_s3_bucket() {
    local bucket_stack_name="$PROJECT_NAME-$ENVIRONMENT-s3-bucket"
    
    print_status "Step 1: Creating S3 bucket for CloudFormation templates..."
    
    cd "$(dirname "$0")/../cloudformation"
    
    # S3 버킷 스택 배포
    aws cloudformation deploy \
        --template-file "08-s3-bucket.yaml" \
        --stack-name $bucket_stack_name \
        --parameter-overrides \
            Environment=$ENVIRONMENT \
            ProjectName=$PROJECT_NAME \
        --region $AWS_REGION
    
    # 버킷 이름 가져오기
    local bucket_name=$(aws cloudformation describe-stacks \
        --stack-name $bucket_stack_name \
        --query 'Stacks[0].Outputs[?OutputKey==`TemplatesBucketName`].OutputValue' \
        --output text --region $AWS_REGION)
    
    if [ -z "$bucket_name" ]; then
        print_error "Failed to get bucket name from stack output"
        exit 1
    fi
    
    print_success "S3 bucket created: $bucket_name"
    echo $bucket_name
}

# 2단계: 템플릿 업로드
upload_templates() {
    local bucket_name=$1
    
    print_status "Step 2: Uploading CloudFormation templates to S3..."
    
    cd "$(dirname "$0")/../cloudformation"
    
    # 마스터 스택과 S3 버킷 템플릿 제외하고 업로드
    for template in *.yaml; do
        if [[ "$template" != "00-master-stack.yaml" && "$template" != "08-s3-bucket.yaml" ]]; then
            aws s3 cp $template s3://$bucket_name/ --region $AWS_REGION
            print_status "Uploaded: $template"
        fi
    done
    
    print_success "All templates uploaded to S3"
}

# 3단계: Docker 이미지 빌드 및 ECR 푸시 (ECR 리포지토리가 생성된 후)
build_and_push_image() {
    local repo_name="$PROJECT_NAME-$ENVIRONMENT"
    
    print_status "Step 3: Building and pushing Docker image..."
    
    # ECR 리포지토리 생성 (임시로, 나중에 CloudFormation으로 관리됨)
    aws ecr create-repository --repository-name $repo_name --region $AWS_REGION 2>/dev/null || true
    
    # ECR 로그인
    aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
    
    # Docker 이미지 빌드
    cd ../../construction/unit1_authentication
    docker build -t $repo_name .
    
    # 이미지 태그 및 푸시
    local image_uri="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$repo_name:latest"
    docker tag $repo_name:latest $image_uri
    docker push $image_uri
    
    print_success "Docker image pushed to ECR"
    cd - >/dev/null
    
    echo $image_uri
}

# 4단계: 마스터 스택 배포
deploy_master_stack() {
    local bucket_name=$1
    local image_uri=$2
    
    print_status "Step 4: Deploying master stack..."
    
    cd "$(dirname "$0")/../cloudformation"
    
    aws cloudformation deploy \
        --template-file "00-master-stack.yaml" \
        --stack-name "$PROJECT_NAME-$ENVIRONMENT-master" \
        --parameter-overrides \
            Environment=$ENVIRONMENT \
            ProjectName=$PROJECT_NAME \
            ImageURI=$image_uri \
            TemplatesBucketName=$bucket_name \
        --capabilities CAPABILITY_NAMED_IAM \
        --region $AWS_REGION
    
    print_success "Master stack deployed successfully"
}

# 배포 결과 출력
show_deployment_results() {
    print_status "Deployment Results:"
    
    # 마스터 스택 출력 가져오기
    local outputs=$(aws cloudformation describe-stacks \
        --stack-name "$PROJECT_NAME-$ENVIRONMENT-master" \
        --query 'Stacks[0].Outputs' \
        --region $AWS_REGION)
    
    echo "$outputs" | jq -r '.[] | "\(.OutputKey): \(.OutputValue)"'
    
    print_success "Deployment completed successfully!"
}

# 메인 함수
main() {
    print_status "Starting 2-stage deployment for AIDLC Unit1 Authentication Service..."
    print_status "Environment: $ENVIRONMENT"
    print_status "Region: $AWS_REGION"
    print_status "Account ID: $AWS_ACCOUNT_ID"
    
    # 1단계: S3 버킷 생성
    bucket_name=$(create_s3_bucket)
    
    # 2단계: 템플릿 업로드
    upload_templates $bucket_name
    
    # 3단계: Docker 이미지 빌드 및 푸시
    image_uri=$(build_and_push_image)
    
    # 4단계: 마스터 스택 배포
    deploy_master_stack $bucket_name $image_uri
    
    # 결과 출력
    show_deployment_results
}

# 사용법 출력
usage() {
    echo "Usage: $0"
    echo ""
    echo "This script performs a 2-stage deployment:"
    echo "1. Creates a private S3 bucket for CloudFormation templates"
    echo "2. Uploads all templates to the bucket"
    echo "3. Builds and pushes Docker image to ECR"
    echo "4. Deploys the complete infrastructure using master stack"
    echo ""
    echo "Prerequisites:"
    echo "- AWS CLI configured with appropriate permissions"
    echo "- Docker installed and running"
    echo "- jq installed for JSON parsing"
}

# 인수 확인
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    usage
    exit 0
fi

# 필수 도구 확인
command -v aws >/dev/null 2>&1 || { print_error "AWS CLI is required but not installed."; exit 1; }
command -v docker >/dev/null 2>&1 || { print_error "Docker is required but not installed."; exit 1; }
command -v jq >/dev/null 2>&1 || { print_error "jq is required but not installed."; exit 1; }

# 스크립트 실행
main "$@"
