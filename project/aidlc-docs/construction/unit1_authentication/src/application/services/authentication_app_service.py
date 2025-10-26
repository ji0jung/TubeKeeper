from typing import Optional

from domain.aggregates.user_aggregate import UserAggregate
from domain.aggregates.verification_code_aggregate import VerificationCodeAggregate
from domain.repositories.user_repository import UserRepository
from domain.repositories.verification_code_repository import VerificationCodeRepository
from domain.value_objects.email import Email
from domain.value_objects.gender import Gender
from domain.value_objects.birth_year import BirthYear
from domain.value_objects.code_purpose import CodePurpose
from application.interfaces.email_service_interface import EmailServiceInterface
from application.dtos.authentication_dtos import (
    RegisterRequestDTO, VerifyRegistrationRequestDTO,
    LoginRequestDTO, VerifyLoginRequestDTO, AuthResponseDTO
)


class AuthenticationAppService:
    """인증 애플리케이션 서비스"""
    
    def __init__(
        self,
        user_repo: UserRepository,
        verification_code_repo: VerificationCodeRepository,
        email_service: EmailServiceInterface
    ):
        self._user_repo = user_repo
        self._verification_code_repo = verification_code_repo
        self._email_service = email_service
    
    async def register(self, request: RegisterRequestDTO) -> AuthResponseDTO:
        """회원가입 요청"""
        try:
            email = Email(request.email)
            
            # 중복 이메일 확인
            if await self._user_repo.exists_by_email(email):
                return AuthResponseDTO(
                    success=False,
                    message="이미 존재하는 이메일입니다."
                )
            
            # 인증 코드 생성
            code_aggregate = VerificationCodeAggregate.generate_new_code(
                email, CodePurpose.REGISTRATION
            )
            await self._verification_code_repo.save(code_aggregate.verification_code)
            
            # 이메일 발송
            await self._email_service.send_verification_code(
                request.email,
                code_aggregate.verification_code.code.value,
                "registration"
            )
            
            return AuthResponseDTO(
                success=True,
                message="인증 코드가 이메일로 발송되었습니다."
            )
            
        except Exception as e:
            return AuthResponseDTO(
                success=False,
                message=f"회원가입 요청 중 오류가 발생했습니다: {str(e)}"
            )
    
    async def verify_registration(self, request: VerifyRegistrationRequestDTO) -> AuthResponseDTO:
        """회원가입 인증 확인"""
        try:
            email = Email(request.email)
            
            # 인증 코드 조회
            verification_code = await self._verification_code_repo.find_latest_by_email_and_purpose(
                email, CodePurpose.REGISTRATION
            )
            
            if not verification_code:
                return AuthResponseDTO(
                    success=False,
                    message="인증 코드를 찾을 수 없습니다."
                )
            
            # 인증 코드 검증
            code_aggregate = VerificationCodeAggregate.from_existing(verification_code)
            if not code_aggregate.verify(request.verification_code):
                return AuthResponseDTO(
                    success=False,
                    message="잘못된 인증 코드입니다."
                )
            
            # 사용자 생성
            gender = Gender(request.gender) if hasattr(request, 'gender') and request.gender else None
            birth_year = BirthYear(request.birth_year) if hasattr(request, 'birth_year') and request.birth_year else None
            
            user_aggregate = UserAggregate.create_new_user(email, gender, birth_year)
            await self._user_repo.save(user_aggregate.user)
            
            # 인증 코드 사용 처리
            await self._verification_code_repo.save(verification_code)
            
            return AuthResponseDTO(
                success=True,
                message="회원가입이 완료되었습니다.",
                user={
                    "user_id": str(user_aggregate.user.user_id),
                    "email": user_aggregate.user.email.value
                }
            )
            
        except Exception as e:
            return AuthResponseDTO(
                success=False,
                message=f"회원가입 인증 중 오류가 발생했습니다: {str(e)}"
            )
    
    async def login(self, request: LoginRequestDTO) -> AuthResponseDTO:
        """로그인 요청"""
        try:
            email = Email(request.email)
            
            # 사용자 존재 확인
            user = await self._user_repo.find_by_email(email)
            if not user or not user.can_login():
                return AuthResponseDTO(
                    success=False,
                    message="존재하지 않거나 비활성화된 계정입니다."
                )
            
            # 인증 코드 생성
            code_aggregate = VerificationCodeAggregate.generate_new_code(
                email, CodePurpose.LOGIN
            )
            await self._verification_code_repo.save(code_aggregate.verification_code)
            
            # 이메일 발송
            await self._email_service.send_verification_code(
                request.email,
                code_aggregate.verification_code.code.value,
                "login"
            )
            
            return AuthResponseDTO(
                success=True,
                message="인증 코드가 이메일로 발송되었습니다."
            )
            
        except Exception as e:
            return AuthResponseDTO(
                success=False,
                message=f"로그인 요청 중 오류가 발생했습니다: {str(e)}"
            )
    
    async def verify_login(self, request: VerifyLoginRequestDTO) -> AuthResponseDTO:
        """로그인 인증 확인"""
        try:
            email = Email(request.email)
            
            # 인증 코드 조회 및 검증
            verification_code = await self._verification_code_repo.find_latest_by_email_and_purpose(
                email, CodePurpose.LOGIN
            )
            
            if not verification_code:
                return AuthResponseDTO(
                    success=False,
                    message="인증 코드를 찾을 수 없습니다."
                )
            
            code_aggregate = VerificationCodeAggregate.from_existing(verification_code)
            if not code_aggregate.verify(request.verification_code):
                return AuthResponseDTO(
                    success=False,
                    message="잘못된 인증 코드입니다."
                )
            
            # 사용자 조회
            user = await self._user_repo.find_by_email(email)
            if not user:
                return AuthResponseDTO(
                    success=False,
                    message="사용자를 찾을 수 없습니다."
                )
            
            # JWT 토큰 생성 (임시로 user_id 반환)
            token = f"jwt_token_for_{user.user_id}"
            
            return AuthResponseDTO(
                success=True,
                token=token,
                user={
                    "user_id": str(user.user_id),
                    "email": user.email.value
                },
                message="로그인이 완료되었습니다."
            )
            
        except Exception as e:
            return AuthResponseDTO(
                success=False,
                message=f"로그인 인증 중 오류가 발생했습니다: {str(e)}"
            )
