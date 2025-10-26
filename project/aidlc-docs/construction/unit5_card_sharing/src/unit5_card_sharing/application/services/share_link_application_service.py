from ..use_cases.create_share_link_use_case import CreateShareLinkUseCase
from ..use_cases.get_shared_card_use_case import GetSharedCardUseCase
from ..use_cases.save_shared_card_use_case import SaveSharedCardUseCase
from ..dtos.commands import CreateShareLinkCommand, AccessShareLinkQuery, SaveSharedCardCommand
from ..dtos.response_dtos import CreateShareLinkDto, SharedCardDto, SaveSharedCardDto

class ShareLinkApplicationService:
    def __init__(
        self,
        create_use_case: CreateShareLinkUseCase,
        get_use_case: GetSharedCardUseCase,
        save_use_case: SaveSharedCardUseCase
    ):
        self._create_use_case = create_use_case
        self._get_use_case = get_use_case
        self._save_use_case = save_use_case
    
    async def create_share_link(self, command: CreateShareLinkCommand) -> CreateShareLinkDto:
        return await self._create_use_case.execute(command)
    
    async def get_shared_card(self, query: AccessShareLinkQuery) -> SharedCardDto:
        return await self._get_use_case.execute(query)
    
    async def save_shared_card(self, command: SaveSharedCardCommand) -> SaveSharedCardDto:
        return await self._save_use_case.execute(command)
