from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from domain.exceptions.domain_exceptions import DomainException
import logging

logger = logging.getLogger(__name__)


async def domain_exception_handler(request: Request, exc: DomainException):
    """도메인 예외 핸들러"""
    logger.warning(f"Domain exception: {exc.message}")
    
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": {
                "code": exc.error_code or "DOMAIN_ERROR",
                "message": exc.message,
                "details": {}
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """입력 검증 예외 핸들러"""
    errors = exc.errors()
    first_error = errors[0] if errors else {}
    
    # 이메일 형식 오류 처리 - 위치만 확인
    if first_error.get('loc') == ['body', 'email']:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "code": "AUTH_005",
                    "message": "Invalid email format",
                    "details": {"errors": errors}
                }
            }
        )
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid input data",
                "details": {"errors": errors}
            }
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 예외 핸들러"""
    # 404 Not Found 처리
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "Endpoint not found",
                    "details": {}
                }
            }
        )
    
    # 기존 HTTPException에서 오류 코드 추출
    detail = str(exc.detail)
    if ":" in detail:
        error_code, message = detail.split(":", 1)
        error_code = error_code.strip()
        message = message.strip()
    else:
        error_code = "HTTP_ERROR"
        message = detail
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "details": {}
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 핸들러"""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error",
                "details": {}
            }
        }
    )
