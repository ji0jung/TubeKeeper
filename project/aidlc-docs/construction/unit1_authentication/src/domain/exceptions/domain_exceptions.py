class DomainException(Exception):
    """기본 도메인 예외"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class InvalidEmailFormatException(DomainException):
    """잘못된 이메일 형식 예외"""
    def __init__(self, message: str):
        super().__init__(message, "AUTH_005")


class EmailAlreadyExistsException(DomainException):
    """이메일 중복 예외"""
    def __init__(self, message: str):
        super().__init__(message, "AUTH_004")


class InvalidBirthYearException(DomainException):
    """잘못된 출생년도 예외"""
    def __init__(self, message: str):
        super().__init__(message, "AUTH_008")


class InvalidGenderException(DomainException):
    """잘못된 성별 값 예외"""
    def __init__(self, message: str):
        super().__init__(message, "AUTH_009")


class InvalidLanguageException(DomainException):
    """잘못된 언어 설정 예외"""
    def __init__(self, message: str):
        super().__init__(message, "AUTH_010")


class InvalidVerificationCodeException(DomainException):
    """잘못된 인증 코드 예외"""
    def __init__(self, message: str):
        super().__init__(message, "AUTH_006")


class VerificationCodeExpiredException(DomainException):
    """인증 코드 만료 예외"""
    def __init__(self, message: str):
        super().__init__(message, "AUTH_007")


class UserNotFoundException(DomainException):
    """사용자 미발견 예외"""
    def __init__(self, message: str):
        super().__init__(message, "AUTH_003")


class UserAlreadyDeactivatedException(DomainException):
    """이미 비활성화된 사용자 예외"""
    def __init__(self, message: str):
        super().__init__(message, "AUTH_011")


class ProfileNotFoundException(DomainException):
    """프로필 미발견 예외"""
    def __init__(self, message: str):
        super().__init__(message, "AUTH_012")


class SessionNotFoundException(DomainException):
    """세션 미발견 예외"""
    def __init__(self, message: str):
        super().__init__(message, "AUTH_014")


class MaxSessionLimitExceededException(DomainException):
    """최대 세션 수 초과 예외"""
    def __init__(self, message: str):
        super().__init__(message, "AUTH_015")


class InvalidCredentialsException(DomainException):
    """잘못된 인증 정보 예외"""
    def __init__(self, message: str):
        super().__init__(message, "AUTH_001")


class TokenExpiredException(DomainException):
    """토큰 만료 예외"""
    def __init__(self, message: str):
        super().__init__(message, "AUTH_002")
