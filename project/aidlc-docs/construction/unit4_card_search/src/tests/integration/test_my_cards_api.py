"""Integration Tests for My Cards API"""

import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from ...main import app


class TestMyCardsAPI:
    """내 카드 API 통합 테스트"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def auth_headers(self):
        # 테스트용 JWT 토큰
        return {"Authorization": "Bearer test_token"}
    
    def test_search_my_cards_success(self, client, auth_headers):
        """내 카드 검색 성공"""
        response = client.get(
            "/api/my-cards",
            headers=auth_headers,
            params={"limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "cards" in data["data"]
    
    def test_search_my_cards_with_keyword(self, client, auth_headers):
        """키워드로 내 카드 검색"""
        response = client.get(
            "/api/my-cards",
            headers=auth_headers,
            params={"search": "test", "limit": 10}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_search_my_cards_invalid_cursor(self, client, auth_headers):
        """잘못된 커서 형식"""
        response = client.get(
            "/api/my-cards",
            headers=auth_headers,
            params={"cursor": "invalid_cursor"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "SEARCH_010"
    
    def test_search_my_cards_unauthorized(self, client):
        """인증 없이 접근"""
        response = client.get("/api/my-cards")
        
        assert response.status_code == 401
    
    def test_get_favorite_cards(self, client, auth_headers):
        """즐겨찾기 카드 조회"""
        response = client.get(
            "/api/my-cards/favorites",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
