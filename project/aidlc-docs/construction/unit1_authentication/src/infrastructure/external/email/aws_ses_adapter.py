import boto3
from botocore.exceptions import ClientError
from typing import Optional

from application.interfaces.email_service_interface import EmailServiceInterface
from infrastructure.config.settings import settings


class AWSSESAdapter(EmailServiceInterface):
    """AWS SES 이메일 어댑터"""
    
    def __init__(self):
        self._ses_client = boto3.client(
            'ses',
            region_name=settings.aws_region,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key
        )
        self._sender_email = settings.ses_sender_email
    
    async def send_verification_code(self, to_email: str, code: str, purpose: str) -> bool:
        """인증 코드 이메일 발송"""
        try:
            subject = self._get_subject(purpose)
            body = self._get_body(code, purpose)
            
            response = self._ses_client.send_email(
                Source=self._sender_email,
                Destination={'ToAddresses': [to_email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Html': {'Data': body, 'Charset': 'UTF-8'}
                    }
                }
            )
            
            return True
            
        except ClientError as e:
            print(f"Failed to send email: {e}")
            return False
    
    def _get_subject(self, purpose: str) -> str:
        """이메일 제목 생성"""
        if purpose == 'registration':
            return '[AIDLC] 회원가입 인증 코드'
        elif purpose == 'login':
            return '[AIDLC] 로그인 인증 코드'
        else:
            return '[AIDLC] 인증 코드'
    
    def _get_body(self, code: str, purpose: str) -> str:
        """이메일 본문 생성"""
        if purpose == 'registration':
            action = '회원가입'
        elif purpose == 'login':
            action = '로그인'
        else:
            action = '인증'
            
        return f"""
        <html>
        <body>
            <h2>AIDLC {action} 인증 코드</h2>
            <p>안녕하세요!</p>
            <p>{action}을 완료하기 위해 아래 인증 코드를 입력해주세요.</p>
            <h3 style="color: #007bff; font-size: 24px; letter-spacing: 3px;">{code}</h3>
            <p>이 코드는 15분 후에 만료됩니다.</p>
            <p>본인이 요청하지 않은 경우 이 이메일을 무시해주세요.</p>
            <br>
            <p>감사합니다.<br>AIDLC 팀</p>
        </body>
        </html>
        """
