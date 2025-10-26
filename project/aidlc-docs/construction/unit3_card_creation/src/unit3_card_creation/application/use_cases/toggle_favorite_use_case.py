from ..commands.commands import ToggleFavoriteCommand
from ...domain.repositories.card_repository import CardRepository


class ToggleFavoriteUseCase:
    def __init__(self, card_repository: CardRepository):
        self._card_repository = card_repository
    
    async def execute(self, command: ToggleFavoriteCommand) -> bool:
        card_aggregate = await self._card_repository.find_by_id(command.card_id)
        
        if not card_aggregate or card_aggregate.card.user_id != command.user_id:
            raise ValueError("Card not found or access denied")
        
        card_aggregate.toggle_favorite()
        await self._card_repository.save(card_aggregate)
        
        return card_aggregate.card.is_favorite
