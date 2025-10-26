from dataclasses import dataclass
from typing import Optional

@dataclass
class ErrorResponse:
    error_code: str
    message: str
    details: Optional[str] = None

class ApplicationException(Exception):
    def __init__(self, error_code: str, message: str, details: str = None):
        self.error_code = error_code
        self.message = message
        self.details = details
        super().__init__(message)
    
    def to_response(self) -> ErrorResponse:
        return ErrorResponse(
            error_code=self.error_code,
            message=self.message,
            details=self.details
        )

class ValidationException(ApplicationException):
    def __init__(self, message: str, details: str = None):
        super().__init__("VALIDATION_ERROR", message, details)

class CategoryNotFoundException(ApplicationException):
    def __init__(self, category_id: str):
        super().__init__("CATEGORY_NOT_FOUND", f"카테고리를 찾을 수 없습니다: {category_id}")

class UnauthorizedException(ApplicationException):
    def __init__(self):
        super().__init__("UNAUTHORIZED", "인증이 필요합니다")
