from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ...infrastructure.persistence.database import get_db_session
from ...infrastructure.repositories.postgresql_card_repository import PostgreSQLCardRepository
from ...infrastructure.external_services.youtube_api_adapter import YouTubeApiAdapter
from ...infrastructure.services.card_duplication_service import CardDuplicationService
from ...infrastructure.background.task_scheduler import TaskScheduler
from ...application.use_cases.create_card_use_case import CreateCardUseCase
from ...application.use_cases.get_card_use_case import GetCardUseCase
from ...application.use_cases.get_cards_by_user_use_case import GetCardsByUserUseCase
from ...application.use_cases.toggle_favorite_use_case import ToggleFavoriteUseCase
from ...application.services.card_application_service import CardApplicationService

# 전역 스케줄러 인스턴스 (싱글톤)
_task_scheduler: TaskScheduler = None


async def get_card_repository(session: AsyncSession = Depends(get_db_session)) -> PostgreSQLCardRepository:
    return PostgreSQLCardRepository(session)


async def get_youtube_adapter() -> YouTubeApiAdapter:
    return YouTubeApiAdapter()


async def get_duplication_service(
    repository: PostgreSQLCardRepository = Depends(get_card_repository)
) -> CardDuplicationService:
    return CardDuplicationService(repository)


async def get_task_scheduler() -> TaskScheduler:
    global _task_scheduler
    if _task_scheduler is None:
        _task_scheduler = TaskScheduler()
    return _task_scheduler


async def get_create_card_use_case(
    repository: PostgreSQLCardRepository = Depends(get_card_repository),
    duplication_service: CardDuplicationService = Depends(get_duplication_service)
) -> CreateCardUseCase:
    return CreateCardUseCase(repository, duplication_service)


async def get_card_application_service(
    create_use_case: CreateCardUseCase = Depends(get_create_card_use_case),
    repository: PostgreSQLCardRepository = Depends(get_card_repository),
    task_scheduler: TaskScheduler = Depends(get_task_scheduler)
) -> CardApplicationService:
    get_use_case = GetCardUseCase(repository)
    get_cards_use_case = GetCardsByUserUseCase(repository)
    toggle_favorite_use_case = ToggleFavoriteUseCase(repository)
    
    return CardApplicationService(
        create_use_case,
        get_use_case,
        get_cards_use_case,
        toggle_favorite_use_case,
        task_scheduler
    )
