from typing import Any, Optional, Dict
from pydantic import BaseModel

class StandardResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: str
    error: Optional[Dict[str, Any]] = None

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None

def success_response(data: Any = None, message: str = "Success") -> StandardResponse:
    return StandardResponse(
        success=True,
        data=data,
        message=message
    )

def error_response(code: str, message: str, details: Dict[str, Any] = None) -> StandardResponse:
    return StandardResponse(
        success=False,
        error=ErrorDetail(
            code=code,
            message=message,
            details=details
        ).dict(),
        message=message
    )
