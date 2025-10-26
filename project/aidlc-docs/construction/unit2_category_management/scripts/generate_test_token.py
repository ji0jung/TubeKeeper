#!/usr/bin/env python3
"""
JWT 테스트 토큰 생성 유틸리티

Unit2 독립 테스트를 위한 JWT 토큰 생성기
- Unit1 인증 서비스와 독립적으로 동작
- 로컬 테스트용 JWT 토큰 생성
- 사용자 ID와 이메일을 포함한 토큰 생성

역할:
    - 테스트 환경에서 인증 토큰 제공
    - Unit1 없이도 Unit2 독립 테스트 가능
    - 실제 JWT 형식과 동일한 토큰 생성

사용법:
    token = generate_test_token(user_id, email)
    headers = {"Authorization": f"Bearer {token}"}
"""

import sys
import os
from datetime import datetime, timedelta
from jose import jwt
from uuid import uuid4

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.config.settings import settings

def generate_test_token(user_id: str = None, email: str = "test@example.com"):
    """Unit2 단독 테스트용 JWT 토큰 생성"""
    
    if not user_id:
        user_id = str(uuid4())
    
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24)  # 24시간으로 연장
    }
    
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    
    print(f"Generated JWT Token:")
    print(f"User ID: {user_id}")
    print(f"Email: {email}")
    print(f"Token: {token}")
    print(f"\nCurl example:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:8002/api/categories')
    
    return token

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_test_token(sys.argv[1])
    else:
        generate_test_token()
