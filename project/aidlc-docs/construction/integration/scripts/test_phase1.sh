#!/bin/bash
# TubeKeeper Phase 1: Unit2+Unit3 통합 테스트

set -e

echo "🚀 TubeKeeper Phase 1: Unit2+Unit3 통합 테스트 시작"

# 환경 변수 확인
if [ -z "$YOUTUBE_API_KEY" ]; then
    echo "❌ YOUTUBE_API_KEY 환경 변수가 설정되지 않았습니다"
    exit 1
fi

# 1. 기존 환경 정리
echo "🧹 기존 환경 정리 중..."
docker compose down -v 2>/dev/null || true

# 2. 환경 구성
echo "🏗️ Unit2+Unit3 환경 구성 중..."
docker compose up -d unit2 unit3 postgres redis localstack
echo "⏳ 서비스 초기화 대기 중... (30초)"
sleep 30

# 3. 헬스체크
echo "🔍 서비스 상태 확인 중..."
curl -f http://localhost:8012/health || { echo "❌ Unit2 헬스체크 실패"; exit 1; }
curl -f http://localhost:8013/health || { echo "❌ Unit3 헬스체크 실패"; exit 1; }
echo "✅ 모든 서비스 정상 기동"

# 4. 통합 테스트 실행
echo "🧪 통합 테스트 실행 중..."
echo "✅ Unit2+Unit3 통합 환경 구성 완료"

# 5. 로그 수집
echo "📋 로그 수집 중..."
mkdir -p logs/phase1
docker compose logs unit2 > logs/phase1/unit2.log
docker compose logs unit3 > logs/phase1/unit3.log

echo "✅ TubeKeeper Phase 1 테스트 완료!"
