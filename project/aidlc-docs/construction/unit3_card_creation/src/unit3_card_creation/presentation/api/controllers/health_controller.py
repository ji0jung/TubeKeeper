from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from ....infrastructure.persistence.database import get_db_session

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(session: AsyncSession = Depends(get_db_session)):
    """시스템 헬스체크"""
    try:
        # 데이터베이스 연결 확인
        await session.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "message": "All systems operational"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )


@router.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": "Unit3 Card Management System",
        "version": "1.0.0",
        "status": "running"
    }
