#!/usr/bin/env python3
"""
Unit5 Docker 환경 통합 테스트

이 모듈은 Unit5 카드 공유 시스템의 Docker 환경에서 전체 시스템을 테스트합니다.
실제 운영 환경과 유사한 조건에서 모든 컴포넌트의 통합 동작을 검증합니다.

테스트 환경:
- PostgreSQL 데이터베이스 (포트 5435)
- Redis 캐시 서버 (포트 6381)
- FastAPI 애플리케이션 (포트 8005)

테스트 기능:
- 서비스 헬스체크 및 준비 상태 확인
- 전체 API 플로우 테스트 (생성 → 조회 → 저장)
- 오류 시나리오 처리 검증
- 크롤러 HTML 응답 테스트
- 자동 데이터 정리 (성공 시에만)

데이터 관리:
- 테스트 시작 전: 기존 데이터 정리
- 테스트 성공 시: 생성된 데이터 자동 삭제
- 테스트 실패 시: 디버깅을 위해 데이터 보존

실행 방법:
    python test_docker.py
    또는
    ./docker_test.sh
"""

import asyncio
import aiohttp
import asyncpg
import redis.asyncio as redis
from tests.test_config import TestConfig

BASE_URL = "http://localhost:8005"
DB_URL = "postgresql://postgres:password@localhost:5435/unit5_sharing"
REDIS_URL = "redis://localhost:6381/0"

class TestDataManager:
    """테스트 데이터 관리 클래스"""
    
    @staticmethod
    async def cleanup_database():
        """데이터베이스 정리"""
        try:
            conn = await asyncpg.connect(DB_URL)
            await conn.execute("DELETE FROM share_link_access_logs")
            await conn.execute("DELETE FROM share_links")
            await conn.close()
            print("✅ 데이터베이스 정리 완료")
        except Exception as e:
            print(f"⚠️ 데이터베이스 정리 실패: {e}")
    
    @staticmethod
    async def cleanup_redis():
        """Redis 캐시 정리"""
        try:
            redis_client = redis.from_url(REDIS_URL)
            await redis_client.flushdb()
            await redis_client.close()
            print("✅ Redis 캐시 정리 완료")
        except Exception as e:
            print(f"⚠️ Redis 정리 실패: {e}")
    
    @staticmethod
    async def cleanup_all():
        """모든 테스트 데이터 정리"""
        print("🧹 테스트 데이터 정리 중...")
        await TestDataManager.cleanup_database()
        await TestDataManager.cleanup_redis()

async def wait_for_service(url: str, timeout: int = 60):
    """서비스가 준비될 때까지 대기"""
    print(f"⏳ 서비스 대기 중: {url}")
    
    for i in range(timeout):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{url}/health", timeout=5) as response:
                    if response.status == 200:
                        print(f"✅ 서비스 준비 완료: {url}")
                        return True
        except:
            pass
        
        await asyncio.sleep(1)
        if i % 10 == 0:
            print(f"   대기 중... ({i}/{timeout}초)")
    
    return False

async def test_health_check():
    """헬스체크 테스트"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/health") as response:
            assert response.status == 200
            data = await response.json()
            assert data["status"] == "healthy"
            print("✅ 헬스체크 통과")

async def test_basic_flow():
    """기본 플로우 테스트 (공유 링크 생성 → 조회 → 저장)"""
    token, user_id = TestConfig.generate_test_token()
    headers = TestConfig.get_auth_headers(token)
    created_tokens = []
    
    try:
        async with aiohttp.ClientSession() as session:
            # 1. 공유 링크 생성
            card_id = "550e8400-e29b-41d4-a716-446655440000"
            async with session.post(
                f"{BASE_URL}/api/cards/{card_id}/share",
                headers=headers
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                share_token = data["data"]["shareToken"]
                created_tokens.append(share_token)
                print("✅ 공유 링크 생성 성공")
            
            # 2. 공유 카드 조회
            async with session.get(
                f"{BASE_URL}/api/shared/{share_token}"
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                print("✅ 공유 카드 조회 성공")
            
            # 3. 공유 카드 저장
            async with session.post(
                f"{BASE_URL}/api/shared/{share_token}/save",
                headers=headers,
                json={}
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is True
                print("✅ 공유 카드 저장 성공")
        
        return created_tokens
        
    except Exception as e:
        print(f"❌ 기본 플로우 테스트 실패: {e}")
        raise

async def test_error_cases():
    """오류 케이스 테스트"""
    async with aiohttp.ClientSession() as session:
        # 1. 인증 없이 공유 링크 생성
        async with session.post(
            f"{BASE_URL}/api/cards/test-id/share"
        ) as response:
            assert response.status == 403
            print("✅ 인증 오류 처리 성공")
        
        # 2. 존재하지 않는 공유 링크 조회
        async with session.get(
            f"{BASE_URL}/api/shared/nonexistent-token"
        ) as response:
            assert response.status == 200
            data = await response.json()
            assert data["success"] is False
            print("✅ 존재하지 않는 링크 오류 처리 성공")

async def test_crawler_response():
    """크롤러 응답 테스트"""
    token, user_id = TestConfig.generate_test_token()
    headers = TestConfig.get_auth_headers(token)
    created_tokens = []
    
    try:
        async with aiohttp.ClientSession() as session:
            # 공유 링크 생성
            card_id = "550e8400-e29b-41d4-a716-446655440001"
            async with session.post(
                f"{BASE_URL}/api/cards/{card_id}/share",
                headers=headers
            ) as response:
                data = await response.json()
                share_token = data["data"]["shareToken"]
                created_tokens.append(share_token)
            
            # 크롤러로 접근
            crawler_headers = {"User-Agent": "facebookexternalhit/1.1"}
            async with session.get(
                f"{BASE_URL}/api/shared/{share_token}",
                headers=crawler_headers
            ) as response:
                assert response.status == 200
                content_type = response.headers.get("content-type", "")
                assert "text/html" in content_type
                print("✅ 크롤러 HTML 응답 성공")
        
        return created_tokens
        
    except Exception as e:
        print(f"❌ 크롤러 테스트 실패: {e}")
        raise

async def run_docker_tests():
    """Docker 환경 테스트 실행"""
    print("🐳 Unit5 Docker 테스트 시작")
    
    # 1. 기존 데이터 정리
    await TestDataManager.cleanup_all()
    
    # 2. 서비스 대기
    if not await wait_for_service(BASE_URL):
        print("❌ 서비스 시작 실패")
        return False
    
    test_success = False
    created_data = []
    
    try:
        # 3. 테스트 실행
        await test_health_check()
        
        tokens1 = await test_basic_flow()
        created_data.extend(tokens1)
        
        await test_error_cases()
        
        tokens2 = await test_crawler_response()
        created_data.extend(tokens2)
        
        print("🎉 모든 Docker 테스트 통과!")
        test_success = True
        
    except Exception as e:
        print(f"❌ Docker 테스트 실패: {e}")
        test_success = False
    
    finally:
        # 4. 테스트 성공 시에만 데이터 정리
        if test_success:
            print("🧹 테스트 성공 - 생성된 데이터 정리 중...")
            await TestDataManager.cleanup_all()
        else:
            print("⚠️ 테스트 실패 - 디버깅을 위해 데이터 보존")
            if created_data:
                print(f"생성된 토큰들: {created_data}")
    
    return test_success

if __name__ == "__main__":
    success = asyncio.run(run_docker_tests())
    exit(0 if success else 1)
