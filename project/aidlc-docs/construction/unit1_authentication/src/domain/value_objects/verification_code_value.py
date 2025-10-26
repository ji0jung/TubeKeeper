import secrets
from dataclasses import dataclass
from domain.exceptions.domain_exceptions import InvalidVerificationCodeException


@dataclass(frozen=True)
class VerificationCodeValue:
    """인증 코드 값 객체"""
    value: str
    
    @classmethod
    def generate(cls) -> 'VerificationCodeValue':
        """6자리 랜덤 코드 생성"""
        code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
        return cls(code)
    
    def __post_init__(self):
        if not (len(self.value) == 6 and self.value.isdigit()):
            raise InvalidVerificationCodeException("Code must be 6 digits")
    
    def __str__(self) -> str:
        return self.value
