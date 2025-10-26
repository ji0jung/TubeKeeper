#!/usr/bin/env python3
"""
Unit5 테스트 설정 및 공통 유틸리티

이 모듈은 Unit5 카드 공유 시스템의 모든 테스트에서 사용되는 공통 설정과 유틸리티를 제공합니다.

주요 기능:
- JWT 토큰 생성 (Unit3 방식과 동일)
- 테스트 환경 설정 (포트 8005 사용)
- 데이터베이스 정리 함수
- 인증 헤더 생성

사용 예시:
    token, user_id = TestConfig.generate_test_token()
    headers = TestConfig.get_auth_headers(token)
    await TestConfig.cleanup_test_data()
"""

from datetime import datetime, timedelta
from jose import jwt
from uuid import uuid4

# 테스트 설정
BASE_URL = "http://localhost:8005"
JWT_SECRET = "unit5-secret-key"
JWT_ALGORITHM = "HS256"

class TestConfig:
    """테스트 설정 클래스"""
    
    @staticmethod
    def generate_test_token():
        """테스트용 JWT 토큰 생성"""
        user_id = str(uuid4())
        payload = {
            "sub": user_id,  # Unit5는 'sub' 필드 사용
            "email": "test@example.com",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token, user_id
    
    @staticmethod
    def get_auth_headers(token: str):
        """인증 헤더 생성"""
        return {"Authorization": f"Bearer {token}"}
    
    @staticmethod
    async def cleanup_test_data():
        """테스트 시작 전 기존 데이터 정리"""
        try:
            import asyncpg
            conn = await asyncpg.connect("postgresql://postgres:password@localhost:5435/unit5_sharing")
            await conn.execute("DELETE FROM share_links")
            await conn.execute("DELETE FROM share_link_access_logs")
            await conn.close()
            print("✅ 테스트 데이터 정리 완료")
        except Exception as e:
            print(f"⚠️ 데이터 정리 실패: {e}")
