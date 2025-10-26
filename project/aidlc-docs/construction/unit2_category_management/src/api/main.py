from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import categories
from ..config.settings import settings

app = FastAPI(
    title="Unit2 Category Management API",
    description="카테고리 생성, 수정, 삭제 기능을 제공하는 API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories.router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
