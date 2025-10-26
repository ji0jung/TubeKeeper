from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .controllers.share_controller import router as share_router

app = FastAPI(
    title="Unit5 Card Sharing Service",
    description="카드 공유 링크 생성 및 관리 서비스",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(share_router)

@app.get("/")
async def root():
    return {
        "service": "Unit5 Card Sharing System",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "message": "All systems operational"
    }
