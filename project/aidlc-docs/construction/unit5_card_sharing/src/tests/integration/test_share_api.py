#!/usr/bin/env python3
"""
Unit5 카드 공유 API 통합 테스트

이 모듈은 Unit5 카드 공유 시스템의 REST API 엔드포인트들을 통합 테스트합니다.
실제 HTTP 요청을 통해 API의 동작을 검증하고, 다양한 시나리오를 테스트합니다.

테스트 대상 API:
- POST /api/cards/{card_id}/share - 공유 링크 생성
- GET /api/shared/{share_token} - 공유 카드 조회
- POST /api/shared/{share_token}/save - 공유 카드 저장

테스트 시나리오:
- 정상 플로우 (생성 → 조회 → 저장)
- 인증 및 권한 검증
- 오류 처리 (만료, 존재하지 않는 링크 등)
- 크롤러 감지 및 HTML 응답
- 표준 응답 형식 검증

실행 방법:
    python tests/integration/test_share_api.py
"""

import asyncio
import aiohttp
import pytest
from uuid import uuid4
import json

from ..test_config import TestConfig, BASE_URL

class TestShareAPI:
    """공유 API 통합 테스트 클래스"""
    
    @pytest.fixture(autouse=True)
    async def setup(self):
        """각 테스트 실행 전 설정"""
        await TestConfig.cleanup_test_data()
        self.token, self.user_id = TestConfig.generate_test_token()
        self.headers = TestConfig.get_auth_headers(self.token)
        self.card_id = str(uuid4())  # 테스트용 카드 ID
    
    async def test_health_check(self):
        """헬스체크 엔드포인트 테스트"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                assert response.status == 200
                data = await response.json()
                assert data["status"] == "healthy"
    
    async def test_create_share_link_success(self):
        """공유 링크 생성 성공 시나리오 테스트"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/api/cards/{self.card_id}/share",
                headers=self.headers
            ) as response:
                assert response.status == 200
                data = await response.json()
                
                assert data["success"] is True
                assert "shareUrl" in data["data"]
                assert "shareToken" in data["data"]
                assert "expiresAt" in data["data"]
                assert data["message"] == "Share link created successfully"
                
                return data["data"]["shareToken"]
    
    async def test_create_share_link_unauthorized(self):
        """인증 없이 공유 링크 생성 시도 테스트"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/api/cards/{self.card_id}/share"
            ) as response:
                assert response.status == 403  # Unauthorized
    
    async def test_create_share_link_invalid_card_id(self):
        """잘못된 카드 ID로 공유 링크 생성 테스트"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/api/cards/invalid-uuid/share",
                headers=self.headers
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is False
                assert data["error"]["code"] == "CARD_009"
    
    async def test_get_shared_card_success(self):
        """공유 카드 조회 성공 시나리오 테스트"""
        # 먼저 공유 링크 생성
        share_token = await self.test_create_share_link_success()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}/api/shared/{share_token}"
            ) as response:
                assert response.status == 200
                data = await response.json()
                
                assert data["success"] is True
                assert "card" in data["data"]
                assert "isExpired" in data["data"]
                assert "expiresAt" in data["data"]
                assert data["data"]["isExpired"] is False
    
    async def test_get_shared_card_not_found(self):
        """존재하지 않는 공유 링크 조회 테스트"""
        fake_token = str(uuid4())
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}/api/shared/{fake_token}"
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is False
                assert data["error"]["code"] == "SHARE_002"
    
    async def test_get_shared_card_invalid_token(self):
        """잘못된 토큰 형식으로 공유 카드 조회 테스트"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}/api/shared/invalid-token"
            ) as response:
                assert response.status == 200
                data = await response.json()
                assert data["success"] is False
                assert data["error"]["code"] == "SHARE_003"
    
    async def test_save_shared_card_success(self):
        """공유 카드 저장 성공 시나리오 테스트"""
        # 먼저 공유 링크 생성
        share_token = await self.test_create_share_link_success()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/api/shared/{share_token}/save",
                headers=self.headers,
                json={}
            ) as response:
                assert response.status == 200
                data = await response.json()
                
                assert data["success"] is True
                if "newCard" in data["data"]:
                    assert "id" in data["data"]["newCard"]
                    assert "title" in data["data"]["newCard"]
                    assert "categoryId" in data["data"]["newCard"]
    
    async def test_save_shared_card_unauthorized(self):
        """인증 없이 공유 카드 저장 시도 테스트"""
        share_token = str(uuid4())
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{BASE_URL}/api/shared/{share_token}/save",
                json={}
            ) as response:
                assert response.status == 403  # Unauthorized
    
    async def test_crawler_request(self):
        """크롤러 요청 시 HTML 응답 테스트"""
        # 먼저 공유 링크 생성
        share_token = await self.test_create_share_link_success()
        
        crawler_headers = {
            "User-Agent": "facebookexternalhit/1.1"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{BASE_URL}/api/shared/{share_token}",
                headers=crawler_headers
            ) as response:
                assert response.status == 200
                content_type = response.headers.get("content-type", "")
                assert "text/html" in content_type
                
                html_content = await response.text()
                assert "og:title" in html_content
                assert "og:description" in html_content
                assert "og:image" in html_content

# 테스트 실행 함수
async def run_tests():
    """모든 통합 테스트 실행"""
    test_instance = TestShareAPI()
    
    tests = [
        test_instance.test_health_check,
        test_instance.test_create_share_link_success,
        test_instance.test_create_share_link_unauthorized,
        test_instance.test_create_share_link_invalid_card_id,
        test_instance.test_get_shared_card_success,
        test_instance.test_get_shared_card_not_found,
        test_instance.test_get_shared_card_invalid_token,
        test_instance.test_save_shared_card_success,
        test_instance.test_save_shared_card_unauthorized,
        test_instance.test_crawler_request
    ]
    
    print("🚀 Unit5 공유 API 통합 테스트 시작...")
    
    for i, test in enumerate(tests, 1):
        try:
            await test_instance.setup()
            await test()
            print(f"✅ {i:2d}. {test.__name__}")
        except Exception as e:
            print(f"❌ {i:2d}. {test.__name__}: {e}")
    
    print("🎉 Unit5 공유 API 통합 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(run_tests())
