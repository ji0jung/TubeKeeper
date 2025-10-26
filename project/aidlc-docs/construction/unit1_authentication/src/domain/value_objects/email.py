import re
from dataclasses import dataclass
from domain.exceptions.domain_exceptions import InvalidEmailFormatException


@dataclass(frozen=True)
class Email:
    """이메일 값 객체"""
    value: str
    
    def __post_init__(self):
        if not self._is_valid_format(self.value):
            raise InvalidEmailFormatException(f"Invalid email format: {self.value}")
    
    @staticmethod
    def _is_valid_format(email: str) -> bool:
        """이메일 형식 검증"""
        if not email or len(email) > 254:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def __str__(self) -> str:
        return self.value
