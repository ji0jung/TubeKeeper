from typing import List, Any

from domain.entities.verification_code import VerificationCode
from domain.events.verification_events import VerificationCodeGenerated, VerificationCodeUsed
from domain.value_objects.email import Email
from domain.value_objects.code_purpose import CodePurpose


class VerificationCodeAggregate:
    """인증 코드 애그리게이트"""
    
    def __init__(self, verification_code: VerificationCode):
        self._verification_code = verification_code
        self._domain_events: List[Any] = []
    
    @classmethod
    def generate_new_code(cls, email: Email, purpose: CodePurpose, 
                         expire_minutes: int = 15) -> 'VerificationCodeAggregate':
        """새 인증 코드 생성"""
        verification_code = VerificationCode.create(email, purpose, expire_minutes)
        
        aggregate = cls(verification_code)
        aggregate._add_event(VerificationCodeGenerated(
            code_id=verification_code.code_id,
            email=email,
            purpose=purpose,
            expires_at=verification_code.expires_at
        ))
        
        return aggregate
    
    @classmethod
    def from_existing(cls, verification_code: VerificationCode) -> 'VerificationCodeAggregate':
        """기존 인증 코드로부터 애그리게이트 생성"""
        return cls(verification_code)
    
    def verify(self, input_code: str) -> bool:
        """인증 코드 검증"""
        is_valid = self._verification_code.verify(input_code)
        
        if is_valid:
            self._verification_code.mark_as_used()
            self._add_event(VerificationCodeUsed(
                code_id=self._verification_code.code_id,
                email=self._verification_code.email,
                purpose=self._verification_code.purpose,
                used_at=self._verification_code.used_at
            ))
        
        return is_valid
    
    def is_valid(self) -> bool:
        """유효성 확인"""
        return not self._verification_code.is_used and not self._verification_code.is_expired()
    
    @property
    def verification_code(self) -> VerificationCode:
        return self._verification_code
    
    @property
    def domain_events(self) -> List[Any]:
        return self._domain_events.copy()
    
    def clear_events(self) -> None:
        """이벤트 목록 초기화"""
        self._domain_events.clear()
    
    def _add_event(self, event: Any) -> None:
        """도메인 이벤트 추가"""
        self._domain_events.append(event)
