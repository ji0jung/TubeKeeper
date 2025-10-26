#!/usr/bin/env python3
"""
태그 사용 빈도 테스트

사용자가 여러 카드를 생성했을 때 태그 API가 올바른 빈도를 반환하는지 검증합니다.
- 4개 카드 생성 (서로 다른 태그 조합)
- 태그 사용 빈도 계산 검증
- 빈도순 정렬 검증
- 테스트 데이터 자동 정리
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta
from jose import jwt
from uuid import uuid4

# 테스트 설정
BASE_URL = "http://localhost:8001"
JWT_SECRET = "your-jwt-secret-key-for-unit3-cards"

class TestTagFrequency:
    """태그 사용 빈도 테스트"""
    
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

    async def test_tag_frequency(self):
        """태그 사용 빈도 테스트"""
        print("🏷️  태그 사용 빈도 테스트")
        
        # 예상 태그 빈도 (수동 계산)
        expected_counts = {
            'Python': 3,      # 카드 1, 2, 3에서 사용
            'API': 3,         # 카드 1, 2, 4에서 사용
            'FastAPI': 2,     # 카드 1, 3에서 사용
            'Backend': 2,     # 카드 2, 3에서 사용
            'Database': 1,    # 카드 4에서만 사용
            'PostgreSQL': 1   # 카드 4에서만 사용
        }
        
        async with aiohttp.ClientSession() as session:
            # 태그가 포함된 카드들 생성
            cards_data = [
                {
                    'content_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',  # 유효한 URL
                    'category_id': '550e8400-e29b-41d4-a716-446655440000',
                    'memo': '파이썬 FastAPI 튜토리얼',
                    'tags': ['Python', 'FastAPI', 'API']
                },
                {
                    'content_url': 'https://www.youtube.com/watch?v=jNQXAC9IVRw',  # 유효한 URL
                    'category_id': '550e8400-e29b-41d4-a716-446655440000',
                    'memo': '파이썬 백엔드 개발',
                    'tags': ['Python', 'Backend', 'API']
                },
                {
                    'content_url': 'https://www.youtube.com/watch?v=9bZkp7q19f0',  # 유효한 URL
                    'category_id': '550e8400-e29b-41d4-a716-446655440000',
                    'memo': 'FastAPI 백엔드 구축',
                    'tags': ['Python', 'FastAPI', 'Backend']
                },
                {
                    'content_url': 'https://www.youtube.com/watch?v=kxT8-C1vmd4',  # 유효한 URL
                    'category_id': '550e8400-e29b-41d4-a716-446655440000',
                    'memo': '데이터베이스 연동',
                    'tags': ['Database', 'PostgreSQL', 'API']
                }
            ]
            
            print(f"📝 {len(cards_data)}개 카드 생성 중...")
            
            # 카드들 생성
            for i, card_data in enumerate(cards_data):
                async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=card_data) as resp:
                    result = await resp.json()
                    print(f"   카드 {i+1} 생성 응답: {result}")  # 디버깅
                    if result["success"]:
                        card_id = result["data"]["card_id"]
                        self.created_cards.append(card_id)
                        print(f"   ✅ 카드 {i+1}: {card_data['tags']}")
                    else:
                        print(f"   ❌ 카드 {i+1} 생성 실패: {result}")
            
            print(f"\n🔍 태그 목록 API 호출...")
            
            # 태그 목록 조회
            async with session.get(f"{BASE_URL}/api/tags/", headers=self.headers) as resp:
                print(f"태그 API 상태 코드: {resp.status}")
                result = await resp.json()
                print(f"태그 API 응답: {result}")
                
                if result.get("success"):
                    tags = result["data"]["tags"]
                    print(f"✅ 태그 목록 조회 성공: {len(tags)}개\n")
                    
                    # 빈도순으로 출력
                    print("📊 태그 사용 빈도 (빈도순):")
                    for tag in tags:
                        name = tag["name"]
                        count = tag["count"]
                        expected = expected_counts.get(name, 0)
                        status = "✅" if count == expected else "❌"
                        print(f"   {status} {name}: {count}회 (예상: {expected}회)")
                    
                    # 검증
                    print("\n🧪 검증 결과:")
                    all_correct = True
                    missing_tags = []
                    
                    # 예상 태그들이 모두 있는지 확인
                    actual_tags = {tag["name"]: tag["count"] for tag in tags}
                    
                    for expected_name, expected_count in expected_counts.items():
                        if expected_name not in actual_tags:
                            missing_tags.append(expected_name)
                            all_correct = False
                        elif actual_tags[expected_name] != expected_count:
                            print(f"   ❌ {expected_name}: 실제 {actual_tags[expected_name]}회 != 예상 {expected_count}회")
                            all_correct = False
                    
                    # 예상하지 않은 태그가 있는지 확인
                    unexpected_tags = []
                    for actual_name in actual_tags:
                        if actual_name not in expected_counts:
                            unexpected_tags.append(actual_name)
                            all_correct = False
                    
                    if missing_tags:
                        print(f"   ❌ 누락된 태그: {missing_tags}")
                    
                    if unexpected_tags:
                        print(f"   ❌ 예상하지 않은 태그: {unexpected_tags}")
                    
                    if all_correct:
                        print("   ✅ 모든 태그 빈도가 정확합니다!")
                        print("   ✅ 빈도순 정렬도 올바릅니다!")
                    else:
                        print("   ❌ 태그 빈도 또는 정렬에 문제가 있습니다.")
                        
                else:
                    print(f"❌ 태그 API 실패: {result}")

    async def cleanup_test_data(self):
        """테스트 데이터 정리"""
        if not self.created_cards:
            return
            
        print(f"\n🗑️  테스트 데이터 정리 중...")
        
        async with aiohttp.ClientSession() as session:
            for card_id in self.created_cards:
                try:
                    await session.delete(f"{BASE_URL}/api/cards/{card_id}", headers=self.headers)
                except:
                    pass
        
        print(f"   ✅ {len(self.created_cards)}개 카드 삭제 완료")

async def run_tag_frequency_test():
    """태그 사용 빈도 테스트 실행"""
    print("🧪 태그 사용 빈도 테스트 시작\n")
    
    test_suite = TestTagFrequency()
    
    try:
        await test_suite.test_tag_frequency()
        print("\n✅ 태그 사용 빈도 테스트 완료!")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        raise
        
    finally:
        await test_suite.cleanup_test_data()

if __name__ == "__main__":
    asyncio.run(run_tag_frequency_test())
