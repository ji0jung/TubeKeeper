#!/usr/bin/env python3
"""테스트용 JWT 토큰 생성 스크립트"""

import sys
import os
from datetime import datetime, timedelta
from jose import jwt
from uuid import uuid4

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from unit3_card_creation.infrastructure.config.settings import settings

def generate_test_token(user_id: str = None, email: str = "test@example.com"):
    """테스트용 JWT 토큰 생성"""
    
    if not user_id:
        user_id = str(uuid4())
    
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=24)  # 24시간
    }
    
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    
    print(f"Generated JWT Token:")
    print(f"User ID: {user_id}")
    print(f"Email: {email}")
    print(f"Token: {token}")
    print(f"\nCurl example:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:8001/api/cards')
    
    return token

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_test_token(sys.argv[1])
    else:
        generate_test_token()
