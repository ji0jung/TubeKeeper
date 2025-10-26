from application.interfaces.email_service_interface import EmailServiceInterface


class ConsoleEmailAdapter(EmailServiceInterface):
    """콘솔 출력 이메일 어댑터 (테스트용)"""
    
    async def send_verification_code(self, to_email: str, code: str, purpose: str) -> bool:
        """인증 코드 콘솔 출력"""
        print(f"\n📧 이메일 발송 시뮬레이션")
        print(f"받는 사람: {to_email}")
        print(f"목적: {purpose}")
        print(f"인증 코드: {code}")
        print(f"만료 시간: 15분")
        print("-" * 40)
        return True
