#!/bin/bash

echo "🐳 Unit5 Docker 테스트 시작"

# Docker Compose 실행
echo "📦 Docker 컨테이너 시작 중..."
docker-compose up -d

# 서비스 준비 대기
echo "⏳ 서비스 준비 대기 중..."
sleep 10

# 테스트 실행
echo "🧪 테스트 실행 중..."
python test_docker.py

# 테스트 결과 저장
TEST_RESULT=$?

# Docker Compose 정리
echo "🧹 Docker 컨테이너 정리 중..."
docker-compose down

# 결과 출력
if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ Unit5 Docker 테스트 성공!"
else
    echo "❌ Unit5 Docker 테스트 실패!"
fi

exit $TEST_RESULT
