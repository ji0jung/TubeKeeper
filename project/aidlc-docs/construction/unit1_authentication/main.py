from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
import sys
import os
import asyncio

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from interfaces.api.controllers.auth_controller import router as auth_router
from interfaces.api.controllers.profile_controller import router as profile_router
from interfaces.api.exception_handlers import (
    domain_exception_handler, http_exception_handler, general_exception_handler,
    validation_exception_handler
)
from domain.exceptions.domain_exceptions import DomainException

app = FastAPI(
    title="AIDLC Authentication Service",
    description="사용자 인증 및 프로필 관리 서비스",
    version="0.1.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(auth_router)
app.include_router(profile_router)

# 예외 핸들러 등록
app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    try:
        from infrastructure.persistence.db_init import initialize_database
        await initialize_database()
    except Exception as e:
        print(f"DB 초기화 실패: {e}")
        # 개발 환경에서는 계속 진행


@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "success": True,
        "data": {
            "message": "AIDLC Authentication Service",
            "version": "0.1.0",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "success": True,
        "data": {
            "status": "healthy"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
