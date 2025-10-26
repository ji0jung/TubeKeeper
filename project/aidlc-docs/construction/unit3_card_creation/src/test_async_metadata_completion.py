#!/usr/bin/env python3
"""
비동기 메타데이터 완성 테스트

YouTube API를 통한 비동기 메타데이터 처리 과정을 검증합니다.
- 비동기 메타데이터 추출 및 완성
- 백그라운드 작업 처리
- 메타데이터 업데이트 상태 추적
- 실패 시 재시도 로직
"""

카드 생성 후 백그라운드에서 YouTube 메타데이터를 수집하고 
S3 썸네일 업로드까지 완료되는 과정을 테스트합니다.
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from jose import jwt
from uuid import uuid4

# 설정
BASE_URL = "http://localhost:8001"
JWT_SECRET = "your-jwt-secret-key-for-unit3-cards"
JWT_ALGORITHM = "HS256"

def generate_test_token():
    """테스트용 JWT 토큰 생성"""
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

async def test_async_metadata_completion():
    """비동기 메타데이터 수집 완료 테스트"""
    token, user_id = generate_test_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print(f"🚀 비동기 메타데이터 수집 테스트 시작 (User ID: {user_id})")
    
    # 테스트할 YouTube URL들
    test_videos = [
        {
            "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "name": "Rick Roll"
        },
        {
            "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw", 
            "name": "Me at the zoo"
        },
        {
            "url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
            "name": "강남스타일"
        }
    ]
    
    async with aiohttp.ClientSession() as session:
        created_cards = []
        
        # 1. 카드들을 빠르게 생성
        print("\n📝 카드 생성 중...")
        for video in test_videos:
            card_data = {
                "content_url": video["url"],
                "category_id": "550e8400-e29b-41d4-a716-446655440000",
                "memo": f"{video['name']} 비동기 테스트",
                "tags": ["비동기", "메타데이터", "테스트"],
                "is_public": False
            }
            
            start_time = datetime.now()
            async with session.post(f"{BASE_URL}/api/cards/", headers=headers, json=card_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    card_id = result["card_id"]
                    end_time = datetime.now()
                    response_time = (end_time - start_time).total_seconds() * 1000
                    
                    created_cards.append({
                        "id": card_id,
                        "name": video["name"],
                        "url": video["url"]
                    })
                    
                    print(f"   ✅ {video['name']} 카드 생성: {card_id} ({response_time:.0f}ms)")
                else:
                    print(f"   ❌ {video['name']} 카드 생성 실패: {resp.status}")
        
        # 2. 초기 상태 확인 (CREATING 상태여야 함)
        print("\n🔍 초기 상태 확인...")
        for card in created_cards:
            async with session.get(f"{BASE_URL}/api/cards/{card['id']}", headers=headers) as resp:
                if resp.status == 200:
                    detail = await resp.json()
                    print(f"   📊 {card['name']}: {detail['status']} | 제목: '{detail.get('video_title', 'N/A')}' | 썸네일: {'있음' if detail.get('thumbnail_url') else '없음'}")
        
        # 3. 메타데이터 수집 완료까지 대기 및 모니터링
        print("\n⏳ 메타데이터 수집 완료 대기...")
        max_wait_time = 30  # 최대 30초 대기
        check_interval = 2   # 2초마다 확인
        
        for elapsed in range(0, max_wait_time, check_interval):
            await asyncio.sleep(check_interval)
            print(f"\n   🕐 {elapsed + check_interval}초 경과...")
            
            all_completed = True
            for card in created_cards:
                async with session.get(f"{BASE_URL}/api/cards/{card['id']}", headers=headers) as resp:
                    if resp.status == 200:
                        detail = await resp.json()
                        status = detail['status']
                        title = detail.get('video_title', '')
                        thumbnail = detail.get('thumbnail_url', '')
                        
                        if status == 'CREATING':
                            all_completed = False
                            print(f"      ⏳ {card['name']}: 수집 중...")
                        elif status == 'COMPLETED':
                            print(f"      ✅ {card['name']}: 완료 | 제목: '{title[:30]}...' | 썸네일: {'있음' if thumbnail else '없음'}")
                        else:
                            print(f"      ⚠️  {card['name']}: {status}")
            
            if all_completed:
                print(f"\n🎉 모든 메타데이터 수집 완료! ({elapsed + check_interval}초)")
                break
        else:
            print(f"\n⏰ {max_wait_time}초 타임아웃 - 일부 카드가 아직 처리 중일 수 있습니다")
        
        # 4. 최종 상태 확인
        print("\n📊 최종 상태 확인...")
        for card in created_cards:
            async with session.get(f"{BASE_URL}/api/cards/{card['id']}", headers=headers) as resp:
                if resp.status == 200:
                    detail = await resp.json()
                    print(f"\n   🎯 {card['name']} ({card['id']}):")
                    print(f"      상태: {detail['status']}")
                    print(f"      제목: {detail.get('video_title', 'N/A')}")
                    print(f"      썸네일: {detail.get('thumbnail_url', 'N/A')}")
                    print(f"      메모: {detail.get('memo', 'N/A')}")
                    print(f"      태그: {detail.get('tags', [])}")
        
        # 5. 데이터 정리
        print("\n🗑️  테스트 데이터 정리...")
        try:
            import asyncpg
            conn = await asyncpg.connect("postgresql://postgres:password@localhost:5433/unit3_cards")
            
            for card in created_cards:
                await conn.execute("DELETE FROM cards WHERE id = $1", card['id'])
                print(f"   ✅ 카드 삭제: {card['name']}")
            
            await conn.close()
            print("   🎉 모든 테스트 데이터 정리 완료!")
            
        except Exception as e:
            print(f"   ⚠️  데이터 정리 실패: {e}")

async def main():
    """메인 테스트 실행"""
    # 0. 기존 테스트 데이터 정리
    await cleanup_existing_test_data()
    
    # 1. 비동기 메타데이터 수집 테스트
    await test_async_metadata_completion()

if __name__ == "__main__":
    asyncio.run(main())
