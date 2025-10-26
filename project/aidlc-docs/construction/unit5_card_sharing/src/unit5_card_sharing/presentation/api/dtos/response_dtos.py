from typing import Any, Optional, Dict
from pydantic import BaseModel

class StandardResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    message: str
    error: Optional[Dict[str, Any]] = None

def success_response(data: Any = None, message: str = "Success") -> StandardResponse:
    return StandardResponse(success=True, data=data, message=message)

def error_response(code: str, message: str) -> StandardResponse:
    return StandardResponse(
        success=False,
        error={"code": code, "message": message},
        message=message
    )
