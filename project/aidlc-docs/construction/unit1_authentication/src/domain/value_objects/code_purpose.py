from enum import Enum


class CodePurpose(Enum):
    """인증 코드 목적 값 객체"""
    REGISTRATION = "registration"
    LOGIN = "login"
    
    def __str__(self) -> str:
        return self.value
