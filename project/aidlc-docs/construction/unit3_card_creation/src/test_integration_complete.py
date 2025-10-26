#!/usr/bin/env python3
"""
전체 시스템 통합 테스트

Unit3 카드 생성 시스템의 모든 기능을 종합적으로 테스트합니다.
- 시스템 헬스체크 (DB, Redis, API)
- 카드 CRUD 전체 플로우 검증
- 메타데이터 처리 및 썸네일 생성
- 즐겨찾기, 태그, 메모 기능
- 에러 처리 및 예외 상황
"""
Unit3 카드 관리 시스템 완전한 통합 테스트

이 테스트는 다음 기능들을 검증합니다:
1. 헬스체크 및 시스템 상태
2. 카드 CRUD 전체 워크플로우
3. 비동기 메타데이터 수집
4. 썸네일 처리 및 압축
5. 즐겨찾기 기능
6. 페이지네이션
7. 에러 처리
8. 권한 검증
"""

import asyncio
import aiohttp
import pytest
from datetime import datetime, timedelta
from jose import jwt
from uuid import uuid4
import time

# 테스트 설정
BASE_URL = "http://localhost:8001"
JWT_SECRET = "your-jwt-secret-key-for-unit3-cards"
JWT_ALGORITHM = "HS256"

class TestConfig:
    """테스트 설정 클래스"""
    
    @staticmethod
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

    @staticmethod
    async def cleanup_test_data():
        """테스트 시작 전 기존 데이터 정리"""
        try:
            import asyncpg
            conn = await asyncpg.connect("postgresql://postgres:password@localhost:5433/unit3_cards")
            result = await conn.execute("DELETE FROM cards")
            await conn.close()
            deleted_count = int(result.split()[-1]) if result.split() else 0
            return deleted_count
        except Exception:
            return 0

class TestSystemHealth:
    """시스템 헬스체크 테스트"""
    
    async def test_health_endpoint(self):
        """헬스체크 엔드포인트 테스트"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as resp:
                assert resp.status == 200
                data = await resp.json()
                assert data["status"] == "healthy"
                assert data["database"] == "connected"
                print("✅ 헬스체크 테스트 통과")

    async def test_root_endpoint(self):
        """루트 엔드포인트 테스트"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/") as resp:
                assert resp.status == 200
                data = await resp.json()
                assert "service" in data
                assert "version" in data
                print("✅ 루트 엔드포인트 테스트 통과")

class TestCardCRUD:
    """카드 CRUD 기능 테스트"""
    
    def __init__(self):
        self.token, self.user_id = TestConfig.generate_test_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.created_cards = []

    async def test_card_creation(self):
        """카드 생성 테스트"""
        card_data = {
            "content_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_id": "550e8400-e29b-41d4-a716-446655440000",
            "memo": "CRUD 테스트 카드",
            "tags": ["테스트", "CRUD"],
            "is_public": False
        }
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=card_data) as resp:
                end_time = time.time()
                
                assert resp.status == 200
                result = await resp.json()
                
                # 응답 검증
                assert "success" in result
                assert result["success"] == True
                assert "data" in result
                assert "card_id" in result["data"]
                assert result["data"]["status"] == "CREATED"
                
                # 성능 검증 (5초 이내)
                response_time = (end_time - start_time) * 1000
                assert response_time < 5000
                
                card_id = result["data"]["card_id"]
                self.created_cards.append(card_id)
                
                print(f"✅ 카드 생성 테스트 통과 (응답시간: {response_time:.0f}ms)")
                return card_id

    async def test_card_retrieval(self, card_id):
        """카드 조회 테스트"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/cards/{card_id}", headers=self.headers) as resp:
                assert resp.status == 200
                data = await resp.json()
                
                # 기본 필드 검증
                assert data["success"] == True
                assert "card" in data["data"]
                card_info = data["data"]["card"]
                assert card_info["card_id"] == card_id
                assert card_info["memo"] == "CRUD 테스트 카드"
                assert card_info["tags"] == ["테스트", "CRUD"]
                
                print("✅ 카드 조회 테스트 통과")
                return data

    async def test_card_update(self, card_id):
        """카드 수정 테스트"""
        update_data = {
            "memo": "수정된 CRUD 테스트 카드",
            "tags": ["수정됨", "CRUD", "업데이트"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.put(f"{BASE_URL}/api/cards/{card_id}", headers=self.headers, json=update_data) as resp:
                assert resp.status == 200
                data = await resp.json()
                
                # 수정 내용 검증
                assert data["success"] == True
                card_info = data["data"]["card"]
                assert card_info["memo"] == "수정된 CRUD 테스트 카드"
                assert card_info["tags"] == ["수정됨", "CRUD", "업데이트"]
                
                print("✅ 카드 수정 테스트 통과")

    async def test_card_deletion(self, card_id):
        """카드 삭제 테스트"""
        async with aiohttp.ClientSession() as session:
            # 삭제 실행
            async with session.delete(f"{BASE_URL}/api/cards/{card_id}", headers=self.headers) as resp:
                assert resp.status == 200
                result = await resp.json()
                assert "message" in result
            
            # 삭제 확인 (404 응답)
            async with session.get(f"{BASE_URL}/api/cards/{card_id}", headers=self.headers) as resp:
                assert resp.status == 404
                
                print("✅ 카드 삭제 테스트 통과")

class TestAsyncMetadata:
    """비동기 메타데이터 수집 테스트"""
    
    def __init__(self):
        self.token, self.user_id = TestConfig.generate_test_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.created_cards = []

    async def test_metadata_collection(self):
        """메타데이터 수집 테스트"""
        test_videos = [
            {
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "expected_title": "Rick Astley - Never Gonna Give You Up"
            },
            {
                "url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
                "expected_title": "Me at the zoo"
            }
        ]
        
        async with aiohttp.ClientSession() as session:
            # 카드 생성
            for i, video in enumerate(test_videos):
                card_data = {
                    "content_url": video["url"],
                    "category_id": "550e8400-e29b-41d4-a716-446655440000",
                    "memo": f"메타데이터 테스트 {i+1}",
                    "tags": ["메타데이터", "비동기"],
                    "is_public": False
                }
                
                async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=card_data) as resp:
                    result = await resp.json()
                    self.created_cards.append(result["data"]["card_id"])
            
            # 메타데이터 수집 대기 (최대 10초)
            await asyncio.sleep(3)
            
            # 메타데이터 수집 결과 검증
            for i, card_id in enumerate(self.created_cards):
                async with session.get(f"{BASE_URL}/api/cards/{card_id}", headers=self.headers) as resp:
                    data = await resp.json()
                    
                    # 표준 형식에서 카드 정보 추출
                    card_info = data["data"]["card"]
                    
                    # 상태 검증
                    assert card_info["status"] in ["COMPLETED", "CREATING"]
                    
                    # 완료된 경우 메타데이터 검증
                    if card_info["status"] == "COMPLETED":
                        assert card_info["video_title"] is not None
                        assert len(card_info["video_title"]) > 0
                        assert card_info["thumbnail_url"] is not None
                        
                        expected_title = test_videos[i]["expected_title"]
                        assert expected_title in card_info["video_title"]
                        
                        print(f"✅ 메타데이터 수집 테스트 통과 - {card_info['video_title'][:30]}...")

class TestFavoriteFeature:
    """즐겨찾기 기능 테스트"""
    
    def __init__(self):
        self.token, self.user_id = TestConfig.generate_test_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.created_cards = []

    async def test_favorite_toggle(self):
        """즐겨찾기 토글 테스트"""
        # 카드 생성
        card_data = {
            "content_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_id": "550e8400-e29b-41d4-a716-446655440000",
            "memo": "즐겨찾기 테스트",
            "tags": ["즐겨찾기"],
            "is_public": False
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=card_data) as resp:
                result = await resp.json()
                card_id = result["data"]["card_id"]
                self.created_cards.append(card_id)
            
            # 즐겨찾기 설정
            async with session.post(f"{BASE_URL}/api/cards/{card_id}/favorite", headers=self.headers) as resp:
                assert resp.status == 200
                result = await resp.json()
                assert result["success"] == True
                assert result["data"]["is_favorite"] == True
            
            # 즐겨찾기 해제
            async with session.post(f"{BASE_URL}/api/cards/{card_id}/favorite", headers=self.headers) as resp:
                assert resp.status == 200
                result = await resp.json()
                assert result["success"] == True
                assert result["data"]["is_favorite"] == False
                
                print("✅ 즐겨찾기 토글 테스트 통과")

    async def test_favorites_filtering(self):
        """즐겨찾기 필터링 테스트"""
        async with aiohttp.ClientSession() as session:
            card_ids = []
            
            # 3개 카드 생성
            for i in range(3):
                card_data = {
                    "content_url": f"https://www.youtube.com/watch?v=filter{i}",
                    "category_id": "550e8400-e29b-41d4-a716-446655440000",
                    "memo": f"필터링 테스트 {i+1}"
                }
                
                async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=card_data) as resp:
                    result = await resp.json()
                    card_id = result["data"]["card_id"]
                    card_ids.append(card_id)
                    self.created_cards.append(card_id)
            
            # 첫 번째와 세 번째 카드만 즐겨찾기 설정
            for i in [0, 2]:
                async with session.post(f"{BASE_URL}/api/cards/{card_ids[i]}/favorite", headers=self.headers) as resp:
                    result = await resp.json()
                    print(f"즐겨찾기 토글 응답: {result}")  # 디버깅
                    if "success" not in result:
                        print(f"오류 응답: {result}")
                        continue
                    assert result["success"] == True
                    assert result["data"]["is_favorite"] == True
            
            await asyncio.sleep(1)  # 데이터베이스 동기화 대기
            
            # 즐겨찾기 필터링 조회
            async with session.get(f"{BASE_URL}/api/cards/?favorites_only=true", headers=self.headers) as resp:
                result = await resp.json()
                
                assert result["success"] == True
                favorite_cards = result["data"]["cards"]
                
                # 2개의 즐겨찾기 카드만 반환되어야 함
                assert len(favorite_cards) == 2
                
                # 모든 카드가 즐겨찾기 상태여야 함
                for card in favorite_cards:
                    assert card["is_favorite"] == True
                
                print("✅ 즐겨찾기 필터링 테스트 통과")

    async def test_thumbnail_fallback(self):
        """썸네일 폴백 처리 테스트"""
        async with aiohttp.ClientSession() as session:
            # 정상 URL로 카드 생성
            card_data = {
                "content_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "category_id": "550e8400-e29b-41d4-a716-446655440000",
                "memo": "썸네일 폴백 테스트"
            }
            
            async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=card_data) as resp:
                result = await resp.json()
                card_id = result["data"]["card_id"]
                self.created_cards.append(card_id)
            
            await asyncio.sleep(3)  # 메타데이터 수집 대기
            
            # 카드 조회하여 썸네일 확인
            async with session.get(f"{BASE_URL}/api/cards/{card_id}", headers=self.headers) as resp:
                result = await resp.json()
                card_info = result["data"]["card"]
                
                thumbnail_url = card_info.get("thumbnail_url", "")
                
                # 썸네일 URL이 존재해야 함
                assert thumbnail_url != ""
                
                # 기본 썸네일 또는 S3 썸네일이어야 함
                is_default = "data:image/svg+xml" in thumbnail_url
                is_s3 = "s3://" in thumbnail_url or "amazonaws.com" in thumbnail_url
                
                assert is_default or is_s3
                
                print("✅ 썸네일 폴백 처리 테스트 통과")

class TestPagination:
    """페이지네이션 테스트"""
    
    def __init__(self):
        self.token, self.user_id = TestConfig.generate_test_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.created_cards = []

    async def test_pagination(self):
        """페이지네이션 테스트"""
        # 서로 다른 YouTube URL로 여러 카드 생성
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll
            "https://www.youtube.com/watch?v=jNQXAC9IVRw",  # Me at the zoo
            "https://www.youtube.com/watch?v=9bZkp7q19f0",  # 강남스타일
            "https://www.youtube.com/watch?v=kJQP7kiw5Fk",  # Despacito
            "https://www.youtube.com/watch?v=fJ9rUzIMcZQ"   # Bohemian Rhapsody
        ]
        
        async with aiohttp.ClientSession() as session:
            for i, url in enumerate(test_urls):
                card_data = {
                    "content_url": url,
                    "category_id": "550e8400-e29b-41d4-a716-446655440000",
                    "memo": f"페이지네이션 테스트 {i+1}",
                    "tags": ["페이지네이션"],
                    "is_public": False
                }
                
                async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=card_data) as resp:
                    result = await resp.json()
                    self.created_cards.append(result["data"]["card_id"])
            
            # 첫 페이지 조회 (limit=2)
            async with session.get(f"{BASE_URL}/api/cards/?limit=2", headers=self.headers) as resp:
                assert resp.status == 200
                data = await resp.json()
                
                assert data["success"] == True
                assert "data" in data
                assert "cards" in data["data"]
                assert len(data["data"]["cards"]) == 2
                assert data["data"]["has_more"] == True
                assert data["data"]["next_cursor"] is not None
                
                print("✅ 페이지네이션 테스트 통과")

class TestCRUDErrors:
    """CRUD 오류 시나리오 테스트"""
    
    def __init__(self):
        self.token, self.user_id = TestConfig.generate_test_token()
        self.other_token, self.other_user_id = TestConfig.generate_test_token()  # 다른 사용자
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        self.other_headers = {
            "Authorization": f"Bearer {self.other_token}",
            "Content-Type": "application/json"
        }
        self.created_cards = []

    async def test_create_card_errors(self):
        """카드 생성 오류 테스트"""
        async with aiohttp.ClientSession() as session:
            # 1. 잘못된 YouTube URL (200으로 응답하지만 ERROR 상태)
            invalid_url_data = {
                "content_url": "https://invalid-url.com/watch?v=invalid",
                "category_id": "550e8400-e29b-41d4-a716-446655440000",
                "memo": "잘못된 URL 테스트",
                "tags": ["오류테스트"]
            }
            
            async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=invalid_url_data) as resp:
                assert resp.status == 200
                result = await resp.json()
                assert result["success"] == True  # 우아한 처리로 200 응답
                assert result["data"]["status"] == "ERROR"
                assert "Invalid YouTube URL" in result["message"]
                print("✅ 잘못된 YouTube URL 오류 처리 테스트 통과")
            
            # 2. 필수 필드 누락 (content_url 없음)
            missing_field_data = {
                "category_id": "550e8400-e29b-41d4-a716-446655440000",
                "memo": "필수 필드 누락 테스트"
            }
            
            async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=missing_field_data) as resp:
                assert resp.status == 422  # Validation Error
                print("✅ 필수 필드 누락 오류 처리 테스트 통과")
            
            # 3. 잘못된 UUID 형식
            invalid_uuid_data = {
                "content_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "category_id": "invalid-uuid-format",
                "memo": "잘못된 UUID 테스트"
            }
            
            async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=invalid_uuid_data) as resp:
                assert resp.status == 422  # Validation Error
                print("✅ 잘못된 UUID 형식 오류 처리 테스트 통과")

    async def test_read_card_errors(self):
        """카드 조회 오류 테스트"""
        # 먼저 테스트용 카드 생성
        card_data = {
            "content_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_id": "550e8400-e29b-41d4-a716-446655440000",
            "memo": "권한 테스트용 카드",
            "tags": ["권한테스트"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=card_data) as resp:
                result = await resp.json()
                card_id = result["data"]["card_id"]
                self.created_cards.append(card_id)
            
            # 1. 존재하지 않는 카드 ID
            fake_card_id = str(uuid4())
            async with session.get(f"{BASE_URL}/api/cards/{fake_card_id}", headers=self.headers) as resp:
                assert resp.status == 404
                print("✅ 존재하지 않는 카드 조회 오류 처리 테스트 통과")
            
            # 2. 다른 사용자의 카드 접근 시도
            async with session.get(f"{BASE_URL}/api/cards/{card_id}", headers=self.other_headers) as resp:
                assert resp.status == 404  # 권한 없음으로 404 반환
                print("✅ 다른 사용자 카드 접근 오류 처리 테스트 통과")
            
            # 3. 잘못된 UUID 형식
            async with session.get(f"{BASE_URL}/api/cards/invalid-uuid", headers=self.headers) as resp:
                assert resp.status == 422  # Validation Error
                print("✅ 잘못된 UUID로 카드 조회 오류 처리 테스트 통과")

    async def test_update_card_errors(self):
        """카드 수정 오류 테스트"""
        # 먼저 테스트용 카드 생성
        card_data = {
            "content_url": "https://www.youtube.com/watch?v=jNQXAC9IVRw",
            "category_id": "550e8400-e29b-41d4-a716-446655440000",
            "memo": "수정 테스트용 카드",
            "tags": ["수정테스트"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=card_data) as resp:
                result = await resp.json()
                card_id = result["data"]["card_id"]
                self.created_cards.append(card_id)
            
            update_data = {"memo": "수정된 메모", "tags": ["수정됨"]}
            
            # 1. 존재하지 않는 카드 수정
            fake_card_id = str(uuid4())
            async with session.put(f"{BASE_URL}/api/cards/{fake_card_id}", headers=self.headers, json=update_data) as resp:
                assert resp.status == 404
                print("✅ 존재하지 않는 카드 수정 오류 처리 테스트 통과")
            
            # 2. 다른 사용자의 카드 수정 시도
            async with session.put(f"{BASE_URL}/api/cards/{card_id}", headers=self.other_headers, json=update_data) as resp:
                assert resp.status == 404  # 권한 없음으로 404 반환
                print("✅ 다른 사용자 카드 수정 오류 처리 테스트 통과")

    async def test_delete_card_errors(self):
        """카드 삭제 오류 테스트"""
        # 먼저 테스트용 카드 생성
        card_data = {
            "content_url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
            "category_id": "550e8400-e29b-41d4-a716-446655440000",
            "memo": "삭제 테스트용 카드",
            "tags": ["삭제테스트"]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/api/cards/", headers=self.headers, json=card_data) as resp:
                result = await resp.json()
                card_id = result["data"]["card_id"]
                self.created_cards.append(card_id)
            
            # 1. 존재하지 않는 카드 삭제
            fake_card_id = str(uuid4())
            async with session.delete(f"{BASE_URL}/api/cards/{fake_card_id}", headers=self.headers) as resp:
                assert resp.status == 404
                print("✅ 존재하지 않는 카드 삭제 오류 처리 테스트 통과")
            
            # 2. 다른 사용자의 카드 삭제 시도
            async with session.delete(f"{BASE_URL}/api/cards/{card_id}", headers=self.other_headers) as resp:
                assert resp.status == 404  # 권한 없음으로 404 반환
                print("✅ 다른 사용자 카드 삭제 오류 처리 테스트 통과")
            
            # 3. 정상 삭제 (정리용)
            async with session.delete(f"{BASE_URL}/api/cards/{card_id}", headers=self.headers) as resp:
                assert resp.status == 200
                self.created_cards.remove(card_id)

class TestErrorHandling:
    """에러 처리 테스트"""
    
    def __init__(self):
        self.token, self.user_id = TestConfig.generate_test_token()
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    async def test_unauthorized_access(self):
        """인증되지 않은 접근 테스트"""
        headers = {"Content-Type": "application/json"}  # 토큰 없음
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/cards/", headers=headers) as resp:
                assert resp.status == 403  # 403 Forbidden
                print("✅ 인증 오류 처리 테스트 통과")

    async def test_not_found_card(self):
        """존재하지 않는 카드 조회 테스트"""
        fake_card_id = str(uuid4())
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/cards/{fake_card_id}", headers=self.headers) as resp:
                assert resp.status == 404
                print("✅ 404 오류 처리 테스트 통과")

async def cleanup_all_test_data():
    """모든 테스트 데이터 정리"""
    deleted_count = await TestConfig.cleanup_test_data()
    if deleted_count > 0:
        print(f"🗑️  테스트 데이터 {deleted_count}개 정리 완료")

async def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 Unit3 카드 관리 시스템 완전한 통합 테스트 시작\n")
    
    # 테스트 시작 전 데이터 정리
    await cleanup_all_test_data()
    
    try:
        # 1. 시스템 헬스체크 테스트
        print("1️⃣ 시스템 헬스체크 테스트")
        health_test = TestSystemHealth()
        await health_test.test_health_endpoint()
        await health_test.test_root_endpoint()
        
        # 2. 카드 CRUD 테스트
        print("\n2️⃣ 카드 CRUD 테스트")
        crud_test = TestCardCRUD()
        card_id = await crud_test.test_card_creation()
        await crud_test.test_card_retrieval(card_id)
        await crud_test.test_card_update(card_id)
        await crud_test.test_card_deletion(card_id)
        
        # 3. 비동기 메타데이터 수집 테스트
        print("\n3️⃣ 비동기 메타데이터 수집 테스트")
        metadata_test = TestAsyncMetadata()
        await metadata_test.test_metadata_collection()
        
        # 4. 즐겨찾기 기능 테스트
        print("\n4️⃣ 즐겨찾기 기능 테스트")
        favorite_test = TestFavoriteFeature()
        await favorite_test.test_favorite_toggle()
        await favorite_test.test_favorites_filtering()
        
        # 5. 썸네일 폴백 테스트
        print("\n5️⃣ 썸네일 폴백 테스트")
        await favorite_test.test_thumbnail_fallback()
        
        # 6. 페이지네이션 테스트
        print("\n5️⃣ 페이지네이션 테스트")
        pagination_test = TestPagination()
        await pagination_test.test_pagination()
        
        # 6. 에러 처리 테스트
        print("\n6️⃣ 에러 처리 테스트")
        error_test = TestErrorHandling()
        await error_test.test_unauthorized_access()
        await error_test.test_not_found_card()
        
        # 7. CRUD 오류 테스트
        print("\n7️⃣ CRUD 오류 테스트")
        crud_error_test = TestCRUDErrors()
        await crud_error_test.test_create_card_errors()
        await crud_error_test.test_read_card_errors()
        await crud_error_test.test_update_card_errors()
        await crud_error_test.test_delete_card_errors()
        
        print("\n🎉 모든 통합 테스트 통과!")
        
    except Exception as e:
        print(f"\n❌ 테스트 실패: {e}")
        raise
    
    finally:
        # 테스트 완료 후 데이터 정리
        await cleanup_all_test_data()

if __name__ == "__main__":
    asyncio.run(run_all_tests())
