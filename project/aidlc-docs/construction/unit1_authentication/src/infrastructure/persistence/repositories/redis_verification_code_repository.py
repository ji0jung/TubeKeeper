import json
import redis.asyncio as redis
from typing import Optional
from datetime import datetime

from domain.entities.verification_code import VerificationCode
from domain.repositories.verification_code_repository import VerificationCodeRepository
from domain.value_objects.email import Email
from domain.value_objects.code_purpose import CodePurpose
from infrastructure.config.settings import settings


class RedisVerificationCodeRepository(VerificationCodeRepository):
    """Redis 기반 인증 코드 리포지토리"""
    
    def __init__(self):
        self._redis = redis.from_url(settings.redis_url)
    
    def _get_key(self, email: str, purpose: str) -> str:
        """Redis 키 생성"""
        return f"verification_code:{email}:{purpose}"
    
    async def save(self, verification_code: VerificationCode) -> None:
        """인증 코드 저장"""
        key = self._get_key(verification_code.email.value, verification_code.purpose.value)
        
        # 인증 코드 데이터 직렬화
        data = {
            "code_id": str(verification_code.code_id),
            "email": verification_code.email.value,
            "code": verification_code.code.value,
            "purpose": verification_code.purpose.value,
            "created_at": verification_code.created_at.isoformat(),
            "expires_at": verification_code.expires_at.isoformat(),
            "is_used": verification_code.is_used
        }
        
        # TTL 계산 (만료 시간까지의 초)
        from common.utils import utc_now
        ttl_seconds = int((verification_code.expires_at - utc_now()).total_seconds())
        
        # Redis에 저장 (TTL 설정)
        await self._redis.setex(key, ttl_seconds, json.dumps(data))
    
    async def find_latest_by_email_and_purpose(
        self, email: Email, purpose: CodePurpose
    ) -> Optional[VerificationCode]:
        """이메일과 목적으로 최신 인증 코드 조회"""
        key = self._get_key(email.value, purpose.value)
        
        # Redis에서 데이터 조회
        data = await self._redis.get(key)
        if not data:
            return None
        
        # 데이터 역직렬화
        try:
            code_data = json.loads(data)
            
            # VerificationCode 객체 재구성
            from uuid import UUID
            from domain.value_objects.verification_code_value import VerificationCodeValue
            
            verification_code = VerificationCode(
                code_id=UUID(code_data["code_id"]),
                email=Email(code_data["email"]),
                code=VerificationCodeValue(code_data["code"]),
                purpose=CodePurpose(code_data["purpose"]),
                created_at=datetime.fromisoformat(code_data["created_at"]),
                expires_at=datetime.fromisoformat(code_data["expires_at"]),
                is_used=code_data["is_used"]
            )
            
            return verification_code
            
        except (json.JSONDecodeError, KeyError, ValueError):
            # 데이터 손상 시 키 삭제
            await self._redis.delete(key)
            return None
    
    async def close(self):
        """Redis 연결 종료"""
        await self._redis.close()
