from typing import Optional, List
from uuid import UUID

from domain.entities.verification_code import VerificationCode
from domain.repositories.verification_code_repository import VerificationCodeRepository
from domain.value_objects.email import Email
from domain.value_objects.code_purpose import CodePurpose


class MemoryVerificationCodeRepository(VerificationCodeRepository):
    """메모리 기반 인증 코드 리포지토리 (테스트용)"""
    
    def __init__(self):
        self._codes: List[VerificationCode] = []
    
    async def save(self, verification_code: VerificationCode) -> None:
        """인증 코드 저장"""
        # 기존 코드 업데이트 또는 새로 추가
        for i, code in enumerate(self._codes):
            if code.code_id == verification_code.code_id:
                self._codes[i] = verification_code
                return
        self._codes.append(verification_code)
    
    async def find_latest_by_email_and_purpose(
        self, email: Email, purpose: CodePurpose
    ) -> Optional[VerificationCode]:
        """이메일과 목적으로 최신 인증 코드 조회"""
        matching_codes = [
            code for code in self._codes
            if code.email.value == email.value and code.purpose == purpose
        ]
        
        if not matching_codes:
            return None
        
        # 생성 시간 기준으로 최신 코드 반환
        return max(matching_codes, key=lambda c: c.created_at)
