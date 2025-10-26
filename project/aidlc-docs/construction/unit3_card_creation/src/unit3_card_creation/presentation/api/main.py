from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .controllers.card_controller import router as card_router
from .controllers.tag_controller import router as tag_router
from .controllers.health_controller import router as health_router
from .middleware.error_middleware import ErrorHandlingMiddleware

app = FastAPI(
    title="Unit3 Card Creation & Management",
    description="YouTube 링크 기반 카드 생성 및 관리 서비스",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 에러 핸들링 미들웨어
app.add_middleware(ErrorHandlingMiddleware)

# 라우터 등록
app.include_router(health_router)
app.include_router(card_router)
app.include_router(tag_router)
