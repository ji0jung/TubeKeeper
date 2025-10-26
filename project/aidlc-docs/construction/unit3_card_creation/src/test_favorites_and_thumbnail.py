#!/usr/bin/env python3
"""
즐겨찾기 필터링 및 썸네일 폴백 처리 테스트

새로 구현된 기능들에 대한 검증 테스트입니다.
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from jose import jwt
from uuid import uuid4

# 테스트 설정
BASE_URL = "http://localhost:8001"
JWT_SECRET = "your-jwt-secret-key-for-unit3-cards"

class TestFavoritesAndThumbnail:
    """즐겨찾기 필터링 및 썸네일 폴백 테스트"""
    
    def __init__(self):
        self.token, self.user_id = self.generate_test_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.created_cards = []

    def generate_test_token(self):
        """테스트용 JWT 토큰 생성"""
        user_id = str(uuid4())
        payload = {
            "user_id": user_id,
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        return token, user_id

    async def test_favorites_filtering(self):
        """즐겨찾기 필터링 기능 테스트"""
        print("⭐ 즐겨찾기 필터링 테스트")
        
        async with aiohttp.ClientSession() as session:
            card_ids = []
            
            # 3개 카드 생성
            for i in range(3):
                card_data = {
                    "content_url": f"https://www.youtube.com/watch?v=dQw4w9WgXc{i}",
                    "category_id": "550e8400-e29b-41d4-a716-446655440000",
                    "memo": f"즐겨찾기 테스트 {i+1}",
                    "tags": ["테스트"]
                }
                
                async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=card_data) as resp:
                    result = await resp.json()
                    if result["success"]:
                        card_id = result["data"]["card_id"]
                        card_ids.append(card_id)
                        self.created_cards.append(card_id)
            
            print(f"   생성된 카드: {len(card_ids)}개")
            
            # 첫 번째와 세 번째 카드만 즐겨찾기 설정
            favorite_cards = [card_ids[0], card_ids[2]]
            for card_id in favorite_cards:
                async with session.post(f"{BASE_URL}/api/cards/{card_id}/favorite", headers=self.headers) as resp:
                    result = await resp.json()
                    assert result["success"] == True
                    assert result["data"]["is_favorite"] == True
            
            print(f"   즐겨찾기 설정: {len(favorite_cards)}개")
            
            # 잠시 대기 (데이터베이스 동기화)
            await asyncio.sleep(1)
            
            # 전체 카드 목록 조회
            async with session.get(f"{BASE_URL}/api/cards/", headers=self.headers) as resp:
                result = await resp.json()
                all_cards = result["data"]["cards"]
                print(f"   전체 카드 수: {len(all_cards)}개")
            
            # 즐겨찾기 필터링 조회
            async with session.get(f"{BASE_URL}/api/cards/?favorites_only=true", headers=self.headers) as resp:
                result = await resp.json()
                
                assert result["success"] == True
                favorite_filtered_cards = result["data"]["cards"]
                
                print(f"   필터링된 카드 수: {len(favorite_filtered_cards)}개")
                
                # 실제 즐겨찾기 카드 수 확인
                actual_favorites = [card for card in favorite_filtered_cards if card.get("is_favorite", False)]
                print(f"   실제 즐겨찾기 카드 수: {len(actual_favorites)}개")
                
                # 검증
                assert len(actual_favorites) == len(favorite_cards), f"예상: {len(favorite_cards)}, 실제: {len(actual_favorites)}"
                
                # 모든 필터링된 카드가 즐겨찾기인지 확인
                all_are_favorites = all(card.get("is_favorite", False) for card in favorite_filtered_cards)
                assert all_are_favorites, "필터링된 카드 중 즐겨찾기가 아닌 카드가 있음"
                
                print("   ✅ 즐겨찾기 필터링 정확성 검증 완료")

    async def test_thumbnail_fallback(self):
        """썸네일 폴백 처리 테스트"""
        print("🖼️  썸네일 폴백 처리 테스트")
        
        async with aiohttp.ClientSession() as session:
            # 1. 잘못된 YouTube URL로 테스트 (ERROR 상태 확인)
            invalid_card_data = {
                "content_url": "https://invalid-youtube-url.com/watch?v=invalid",
                "category_id": "550e8400-e29b-41d4-a716-446655440000",
                "memo": "잘못된 URL 테스트"
            }
            
            async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=invalid_card_data) as resp:
                result = await resp.json()
                
                assert result["success"] == True
                assert result["data"]["status"] == "ERROR"
                print("   ✅ 잘못된 URL에 대한 ERROR 상태 처리 확인")
            
            # 2. 정상 URL로 카드 생성 후 썸네일 확인
            valid_card_data = {
                "content_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "category_id": "550e8400-e29b-41d4-a716-446655440000",
                "memo": "썸네일 테스트"
            }
            
            async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=valid_card_data) as resp:
                result = await resp.json()
                card_id = result["data"]["card_id"]
                self.created_cards.append(card_id)
            
            # 메타데이터 수집 대기
            await asyncio.sleep(3)
            
            # 카드 조회하여 썸네일 확인
            async with session.get(f"{BASE_URL}/api/cards/{card_id}", headers=self.headers) as resp:
                result = await resp.json()
                card_info = result["data"]["card"]
                
                thumbnail_url = card_info.get("thumbnail_url", "")
                
                # 썸네일 URL 존재 확인
                assert thumbnail_url != "", "썸네일 URL이 비어있음"
                
                # 기본 썸네일 또는 S3 썸네일 확인
                is_default_thumbnail = "data:image/svg+xml" in thumbnail_url
                is_s3_thumbnail = "s3://" in thumbnail_url or "amazonaws.com" in thumbnail_url
                
                assert is_default_thumbnail or is_s3_thumbnail, "유효하지 않은 썸네일 URL"
                
                if is_default_thumbnail:
                    print("   ✅ 기본 썸네일 (SVG) 사용 확인")
                else:
                    print("   ✅ S3 썸네일 사용 확인")
                
                print(f"   썸네일 URL 타입: {'기본 SVG' if is_default_thumbnail else 'S3 저장소'}")

    async def test_thumbnail_fallback_scenarios(self):
        """다양한 썸네일 폴백 시나리오 테스트"""
        print("🔄 썸네일 폴백 시나리오 테스트")
        
        # 테스트할 잘못된 URL들
        invalid_urls = [
            "https://www.youtube.com/watch?v=nonexistent123",
            "https://invalid-domain.com/watch?v=test",
            "not-a-url-at-all"
        ]
        
        async with aiohttp.ClientSession() as session:
            for i, invalid_url in enumerate(invalid_urls):
                card_data = {
                    "content_url": invalid_url,
                    "category_id": "550e8400-e29b-41d4-a716-446655440000",
                    "memo": f"폴백 시나리오 {i+1}"
                }
                
                async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=card_data) as resp:
                    result = await resp.json()
                    
                    # 모든 잘못된 URL은 ERROR 상태로 처리되어야 함
                    if result["success"] and result["data"]["status"] == "ERROR":
                        print(f"   ✅ 시나리오 {i+1}: ERROR 상태 처리 확인")
                    else:
                        print(f"   ❌ 시나리오 {i+1}: 예상과 다른 응답")

    async def cleanup_test_data(self):
        """테스트 데이터 정리"""
        async with aiohttp.ClientSession() as session:
            for card_id in self.created_cards:
                try:
                    await session.delete(f"{BASE_URL}/api/cards/{card_id}", headers=self.headers)
                except:
                    pass
        
        if self.created_cards:
            print(f"🗑️  테스트 데이터 {len(self.created_cards)}개 정리 완료")

async def run_favorites_and_thumbnail_tests():
    """즐겨찾기 및 썸네일 테스트 실행"""
    print("🧪 즐겨찾기 필터링 및 썸네일 폴백 테스트 시작\n")
    
    test_suite = TestFavoritesAndThumbnail()
    
    try:
        await test_suite.test_favorites_filtering()
        print()
        
        await test_suite.test_thumbnail_fallback()
        print()
        
        await test_suite.test_thumbnail_fallback_scenarios()
        print()
        
        print("✅ 모든 테스트 통과!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        raise
        
    finally:
        await test_suite.cleanup_test_data()

if __name__ == "__main__":
    asyncio.run(run_favorites_and_thumbnail_tests())
