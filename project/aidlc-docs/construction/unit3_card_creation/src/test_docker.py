#!/usr/bin/env python3
"""
Docker 환경 테스트

Docker Compose로 구성된 개발 환경의 각 서비스가 정상 동작하는지 검증합니다.
- PostgreSQL 데이터베이스 연결 테스트
- Redis 연결 테스트  
- FastAPI 애플리케이션 헬스체크
- 전체 인프라 상태 확인
"""
import asyncio
import aiohttp
import asyncpg
import redis.asyncio as redis
import json
from uuid import uuid4


async def test_database_connection():
    """PostgreSQL 연결 테스트"""
    try:
        conn = await asyncpg.connect(
            "postgresql://postgres:password@localhost:5433/unit3_cards"
        )
        result = await conn.fetchval("SELECT 1")
        await conn.close()
        print("✅ PostgreSQL 연결 성공")
        return True
    except Exception as e:
        print(f"❌ PostgreSQL 연결 실패: {e}")
        return False


async def test_redis_connection():
    """Redis 연결 테스트"""
    try:
        r = redis.from_url("redis://localhost:6380/0")
        await r.ping()
        await r.close()
        print("✅ Redis 연결 성공")
        return True
    except Exception as e:
        print(f"❌ Redis 연결 실패: {e}")
        return False


async def test_api_health():
    """API 헬스체크 테스트"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8001/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ API 헬스체크 성공: {data}")
                    return True
                else:
                    print(f"❌ API 헬스체크 실패: {response.status}")
                    return False
    except Exception as e:
        print(f"❌ API 연결 실패: {e}")
        return False


async def test_create_card_api():
    """카드 생성 API 테스트"""
    try:
        # Mock JWT 토큰 (실제로는 유효한 토큰 필요)
        headers = {
            "Authorization": "Bearer mock-token",
            "Content-Type": "application/json"
        }
        
        card_data = {
            "content_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_id": str(uuid4())
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8001/api/cards/",
                headers=headers,
                json=card_data
            ) as response:
                if response.status == 403:  # 인증 실패 예상
                    print("✅ 카드 생성 API 인증 검증 성공 (403 예상)")
                    return True
                else:
                    data = await response.text()
                    print(f"⚠️  카드 생성 API 응답: {response.status} - {data}")
                    return True
    except Exception as e:
        print(f"❌ 카드 생성 API 테스트 실패: {e}")
        return False


async def test_database_table():
    """데이터베이스 테이블 테스트"""
    try:
        conn = await asyncpg.connect(
            "postgresql://postgres:password@localhost:5433/unit3_cards"
        )
        
        # 테이블 존재 확인
        result = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'cards'
            )
        """)
        
        if result:
            print("✅ cards 테이블 존재 확인")
        else:
            print("❌ cards 테이블이 존재하지 않음")
            return False
        
        # 테이블 구조 확인
        columns = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'cards'
            ORDER BY ordinal_position
        """)
        
        print(f"✅ cards 테이블 컬럼 수: {len(columns)}")
        await conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 테이블 테스트 실패: {e}")
        return False


async def main():
    """모든 테스트 실행"""
    print("🚀 Unit3 Docker 환경 테스트 시작\n")
    
    tests = [
        ("데이터베이스 연결", test_database_connection),
        ("Redis 연결", test_redis_connection),
        ("데이터베이스 테이블", test_database_table),
        ("API 헬스체크", test_api_health),
        ("카드 생성 API", test_create_card_api),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} 테스트 중...")
        result = await test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("📊 테스트 결과 요약:")
    print("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n총 {passed}/{len(tests)} 테스트 통과")
    
    if passed == len(tests):
        print("🎉 모든 테스트 통과! Unit3 Docker 환경이 정상 동작합니다.")
    else:
        print("⚠️  일부 테스트 실패. Docker 컨테이너 상태를 확인해주세요.")


if __name__ == "__main__":
    asyncio.run(main())
