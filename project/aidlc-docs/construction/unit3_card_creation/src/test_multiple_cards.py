#!/usr/bin/env python3
"""
다중 카드 생성 및 목록 조회 테스트

로컬 환경에서 JWT 토큰을 생성하여 Unit3 카드 API만 단독으로 테스트하는 스크립트입니다.
Unit1 인증 서비스 없이 독립적으로 카드 CRUD 기능을 검증합니다.
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from jose import jwt
from uuid import uuid4

# 설정
BASE_URL = "http://localhost:8001"
JWT_SECRET = "your-jwt-secret-key-for-unit3-cards"
JWT_ALGORITHM = "HS256"

def generate_test_token():
    """테스트용 JWT 토큰 생성 (Unit1 없이 로컬에서 생성)"""
    user_id = str(uuid4())
    payload = {
        "user_id": user_id,
        "email": "test@example.com",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, user_id

async def cleanup_existing_test_data():
    """테스트 시작 전 기존 테스트 데이터 정리"""
    print("🧹 기존 테스트 데이터 정리 중...")
    
    try:
        import asyncpg
        conn = await asyncpg.connect("postgresql://postgres:password@localhost:5433/unit3_cards")
        
        # 모든 카드 삭제
        result = await conn.execute("DELETE FROM cards")
        deleted_count = int(result.split()[-1]) if result.split() else 0
        
        await conn.close()
        
        if deleted_count > 0:
            print(f"   ✅ 기존 카드 {deleted_count}개 삭제 완료")
        else:
            print("   ✅ 삭제할 기존 카드 없음")
            
    except Exception as e:
        print(f"   ⚠️  기존 데이터 정리 실패: {e}")

async def test_multiple_cards():
    """다중 카드 테스트 실행"""
    token, user_id = generate_test_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print(f"🚀 다중 카드 테스트 시작 (User ID: {user_id})")
    
    async with aiohttp.ClientSession() as session:
        created_cards = []
        
        # 1. 카드 4개 생성
        test_cards = [
            {
                "content_url": "https://www.youtube.com/watch?v=Qs0ul6YuXYc",
                "category_id": "550e8400-e29b-41d4-a716-446655440000",
                "memo": "JWT 토큰 테스트용 카드",
                "tags": ["테스트", "JWT", "인증"],
                "is_public": False
            },
            {
                "content_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "category_id": "550e8400-e29b-41d4-a716-446655440000",
                "memo": "Rick Astley - Never Gonna Give You Up",
                "tags": ["음악", "클래식", "meme"],
                "is_public": True
            },
            {
                "content_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
                "category_id": "550e8400-e29b-41d4-a716-446655440000",
                "memo": "Me at the zoo - 첫 번째 YouTube 영상",
                "tags": ["역사", "YouTube", "첫영상"],
                "is_public": False
            },
            {
                "content_url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
                "category_id": "550e8400-e29b-41d4-a716-446655440000",
                "memo": "PSY - GANGNAM STYLE",
                "tags": ["K-POP", "PSY", "강남스타일", "한국"],
                "is_public": True
            }
        ]
        
        print("\n📝 카드 생성 중...")
        for i, card_data in enumerate(test_cards, 1):
            async with session.post(f"{BASE_URL}/api/cards/", headers=headers, json=card_data) as resp:
                result = await resp.json()
                created_cards.append(result["card_id"])
                print(f"   ✅ 카드 {i} 생성: {result['card_id']}")
        
        # 2. 전체 목록 조회
        print("\n📋 전체 카드 목록 조회...")
        async with session.get(f"{BASE_URL}/api/cards/", headers=headers) as resp:
            cards = await resp.json()
            print(f"   📊 총 {len(cards['cards'])}개 카드 조회")
            for card in cards["cards"]:
                print(f"   - {card['card_id']}: {card['content_url']}")
        
        # 3. 즐겨찾기 토글 (첫 번째, 세 번째 카드)
        print("\n⭐ 즐겨찾기 설정...")
        for i in [0, 2]:
            card_id = created_cards[i]
            async with session.post(f"{BASE_URL}/api/cards/{card_id}/favorite", headers=headers) as resp:
                result = await resp.json()
                print(f"   ✅ 카드 {i+1} 즐겨찾기: {result['is_favorite']}")
        
        # 4. 즐겨찾기만 조회
        print("\n⭐ 즐겨찾기 카드만 조회...")
        async with session.get(f"{BASE_URL}/api/cards/?favorites_only=true", headers=headers) as resp:
            favorites = await resp.json()
            print(f"   📊 즐겨찾기 {len(favorites['cards'])}개 조회")
            for card in favorites["cards"]:
                print(f"   - {card['card_id']}: 즐겨찾기 ⭐")
        
        # 5. 페이지네이션 테스트
        print("\n📄 페이지네이션 테스트 (limit=2)...")
        async with session.get(f"{BASE_URL}/api/cards/?limit=2", headers=headers) as resp:
            page1 = await resp.json()
            print(f"   📊 첫 페이지: {len(page1['cards'])}개")
            print(f"   🔗 다음 커서: {page1['next_cursor']}")
            print(f"   📄 더 있음: {page1['has_more']}")
        
        # 6. 카드 상세 조회
        print("\n🔍 카드 상세 조회...")
        card_id = created_cards[0]
        async with session.get(f"{BASE_URL}/api/cards/{card_id}", headers=headers) as resp:
            if resp.status == 200:
                detail = await resp.json()
                print(f"   ✅ 상세 조회 성공: {detail['memo']}")
                print(f"   📝 태그: {detail['tags']}")
                print(f"   ⭐ 즐겨찾기: {detail['is_favorite']}")
            else:
                print(f"   ❌ 상세 조회 실패: {resp.status}")
        
        # 7. 데이터 정리 (모든 카드 삭제)
        print("\n🗑️  데이터 정리 중...")
        
        # PostgreSQL에서 직접 삭제 (API에 삭제 엔드포인트가 없으므로)
        import asyncpg
        
        try:
            conn = await asyncpg.connect("postgresql://postgres:password@localhost:5433/unit3_cards")
            
            # 생성한 카드들 삭제
            for card_id in created_cards:
                await conn.execute("DELETE FROM cards WHERE id = $1", card_id)
                print(f"   ✅ 카드 삭제: {card_id}")
            
            await conn.close()
            print("   🎉 모든 테스트 데이터 정리 완료!")
            
        except Exception as e:
            print(f"   ⚠️  데이터 정리 실패: {e}")
            print("   💡 수동으로 데이터를 정리해주세요.")

async def main():
    """메인 테스트 실행"""
    # 0. 기존 테스트 데이터 정리
    await cleanup_existing_test_data()
    
    # 1. 다중 카드 테스트
    await test_multiple_cards()

if __name__ == "__main__":
    asyncio.run(main())
