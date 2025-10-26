from fastapi import Depends
from ...infrastructure.database import get_db_session
from ...infrastructure.repositories.postgresql_share_link_repository import PostgreSQLShareLinkRepository
from ...application.use_cases.create_share_link_use_case import CreateShareLinkUseCase
from ...application.use_cases.get_shared_card_use_case import GetSharedCardUseCase
from ...application.use_cases.save_shared_card_use_case import SaveSharedCardUseCase
from ...application.services.share_link_application_service import ShareLinkApplicationService

def get_share_link_service(db_session = Depends(get_db_session)) -> ShareLinkApplicationService:
    repository = PostgreSQLShareLinkRepository(db_session)
    create_use_case = CreateShareLinkUseCase(repository)
    get_use_case = GetSharedCardUseCase(repository)
    save_use_case = SaveSharedCardUseCase(repository)
    return ShareLinkApplicationService(create_use_case, get_use_case, save_use_case)
