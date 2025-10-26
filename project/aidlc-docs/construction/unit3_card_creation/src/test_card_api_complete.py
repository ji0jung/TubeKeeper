#!/usr/bin/env python3
"""
카드 API 전체 기능 테스트 (AI 요약 제거 후)
"""
import asyncio
import json
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unit3_card_creation.presentation.api.main import app


def test_card_api_endpoints():
    """카드 API 엔드포인트 테스트"""
    print("🚀 카드 API 전체 기능 테스트 시작\n")
    
    client = TestClient(app)
    
    # 1. 헬스체크
    print("1️⃣ 헬스체크 테스트")
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("   ✅ 헬스체크 통과\n")
    
    # 2. 카드 생성 (인증 없이 - 403 예상)
    print("2️⃣ 카드 생성 테스트 (인증 없음)")
    create_data = {
        "content_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "category_id": "550e8400-e29b-41d4-a716-446655440000",
        "memo": "테스트 메모입니다",
        "tags": ["개발", "유튜브", "테스트"]
    }
    response = client.post("/api/cards/", json=create_data)
    assert response.status_code == 403  # 인증 필요
    print("   ✅ 인증 없이 카드 생성 시 403 반환\n")
    
    # 3. 카드 목록 조회 (인증 없이 - 403 예상)
    print("3️⃣ 카드 목록 조회 테스트 (인증 없음)")
    response = client.get("/api/cards/")
    assert response.status_code == 403
    print("   ✅ 인증 없이 목록 조회 시 403 반환\n")
    
    # 4. 카드 상세 조회 (인증 없이 - 403 예상)
    print("4️⃣ 카드 상세 조회 테스트 (인증 없음)")
    test_card_id = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f"/api/cards/{test_card_id}")
    assert response.status_code == 403
    print("   ✅ 인증 없이 상세 조회 시 403 반환\n")
    
    # 5. 즐겨찾기 토글 (인증 없이 - 403 예상)
    print("5️⃣ 즐겨찾기 토글 테스트 (인증 없음)")
    response = client.post(f"/api/cards/{test_card_id}/favorite")
    assert response.status_code == 403
    print("   ✅ 인증 없이 즐겨찾기 토글 시 403 반환\n")
    
    # 6. 요청 데이터 유효성 검사
    print("6️⃣ 요청 데이터 유효성 검사")
    
    # 필수 필드 누락 (인증이 먼저 체크되므로 403 예상)
    invalid_data = {"memo": "메모만 있음"}
    response = client.post("/api/cards/", json=invalid_data)
    assert response.status_code == 403  # 인증이 먼저 체크됨
    print("   ✅ 필수 필드 누락 시 403 반환 (인증 우선)")
    
    # 잘못된 UUID 형식 (인증이 먼저 체크되므로 403 예상)
    invalid_uuid_data = {
        "content_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "category_id": "invalid-uuid"
    }
    response = client.post("/api/cards/", json=invalid_uuid_data)
    assert response.status_code == 403  # 인증이 먼저 체크됨
    print("   ✅ 잘못된 UUID 형식 시 403 반환 (인증 우선)\n")


def test_request_dto_structure():
    """요청 DTO 구조 테스트"""
    print("7️⃣ 요청 DTO 구조 테스트")
    
    # CreateCardRequest 구조 확인
    from unit3_card_creation.presentation.api.dtos.request_dtos import CreateCardRequest
    
    # 최소 필수 데이터
    minimal_request = CreateCardRequest(
        content_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        category_id="550e8400-e29b-41d4-a716-446655440000"
    )
    assert minimal_request.memo == ""
    assert minimal_request.tags == []
    print("   ✅ 최소 필수 데이터로 요청 객체 생성 성공")
    
    # 전체 데이터
    full_request = CreateCardRequest(
        content_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        category_id="550e8400-e29b-41d4-a716-446655440000",
        memo="테스트 메모",
        tags=["개발", "유튜브"]
    )
    assert full_request.memo == "테스트 메모"
    assert full_request.tags == ["개발", "유튜브"]
    print("   ✅ 전체 데이터로 요청 객체 생성 성공\n")


def test_response_dto_structure():
    """응답 DTO 구조 테스트"""
    print("8️⃣ 응답 DTO 구조 테스트")
    
    from unit3_card_creation.presentation.api.dtos.response_dtos import (
        CreateCardResponse, CardDetailResponse, CardSummaryResponse
    )
    from uuid import uuid4
    from datetime import datetime
    
    # CreateCardResponse
    create_response = CreateCardResponse(
        card_id=uuid4(),
        status="CREATING",
        message="카드가 생성되었습니다"
    )
    print("   ✅ CreateCardResponse 구조 확인")
    
    # CardDetailResponse (is_public 포함 확인)
    detail_response = CardDetailResponse(
        card_id=uuid4(),
        content_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        video_title="Never Gonna Give You Up",
        thumbnail_url="https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        memo="테스트 메모",
        tags=["개발", "유튜브"],
        is_favorite=True,
        is_public=False,  # 새로 추가된 필드
        status="COMPLETED",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    assert hasattr(detail_response, 'is_public')
    print("   ✅ CardDetailResponse에 is_public 필드 포함 확인")
    
    # CardSummaryResponse
    summary_response = CardSummaryResponse(
        card_id=uuid4(),
        content_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        video_title="Never Gonna Give You Up",
        thumbnail_url="https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
        is_favorite=False,
        created_at=datetime.utcnow()
    )
    print("   ✅ CardSummaryResponse 구조 확인\n")


def main():
    """메인 테스트 실행"""
    test_card_api_endpoints()
    test_request_dto_structure()
    test_response_dto_structure()
    print("🎉 모든 API 테스트 완료!")


if __name__ == "__main__":
    main()
