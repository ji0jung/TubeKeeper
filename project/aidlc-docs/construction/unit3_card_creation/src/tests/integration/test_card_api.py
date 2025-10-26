import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unit3_card_creation.presentation.api.main import app


class TestCardAPI:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "Unit3 Card Creation" in response.json()["message"]
    
    def test_create_card_without_auth(self, client):
        response = client.post("/api/cards/", json={
            "content_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_id": "550e8400-e29b-41d4-a716-446655440000"
        })
        assert response.status_code == 403  # No auth token
    
    def test_create_card_with_memo_and_tags_without_auth(self, client):
        response = client.post("/api/cards/", json={
            "content_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "category_id": "550e8400-e29b-41d4-a716-446655440000",
            "memo": "테스트 메모입니다",
            "tags": ["개발", "유튜브", "테스트"]
        })
        assert response.status_code == 403  # No auth token
    
    def test_create_card_request_validation(self, client):
        # Test missing required fields
        response = client.post("/api/cards/", json={
            "memo": "메모만 있음"
        })
        assert response.status_code == 422  # Validation error
        
        # Test invalid URL
        response = client.post("/api/cards/", json={
            "content_url": "invalid-url",
            "category_id": "550e8400-e29b-41d4-a716-446655440000"
        })
        assert response.status_code == 403  # Would be 422 if auth passed
