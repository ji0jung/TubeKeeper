"""JWT Authentication for Unit4"""

from typing import Optional
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel

from ...config.settings import settings


security = HTTPBearer()


class User(BaseModel):
    """사용자 모델"""
    id: str
    email: str


class JWTAuth:
    """JWT 인증 서비스"""
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """JWT 토큰 디코딩"""
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError:
            return None


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """현재 사용자 조회"""
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = JWTAuth.decode_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        
        if user_id is None or email is None:
            raise credentials_exception
            
        return User(id=user_id, email=email)
        
    except JWTError:
        raise credentials_exception
