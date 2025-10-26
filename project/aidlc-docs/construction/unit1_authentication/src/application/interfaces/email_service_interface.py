from abc import ABC, abstractmethod


class EmailServiceInterface(ABC):
    """이메일 서비스 인터페이스"""
    
    @abstractmethod
    async def send_verification_code(self, to_email: str, code: str, purpose: str) -> bool:
        """인증 코드 이메일 발송"""
        pass
