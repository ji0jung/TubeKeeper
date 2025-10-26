from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from ...domain.repositories.card_repository import CardRepository
from ...domain.aggregates.card_aggregate import CardAggregate
from ...domain.value_objects.content_url import ContentUrl
from ..persistence.models import CardModel
from .mappers import CardMapper


class PostgreSQLCardRepository(CardRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._mapper = CardMapper()
    
    async def save(self, card_aggregate: CardAggregate) -> None:
        model = self._mapper.to_model(card_aggregate.card)
        
        # Upsert
        existing = await self._session.get(CardModel, card_aggregate.card.card_id)
        if existing:
            for key, value in model.__dict__.items():
                if not key.startswith('_'):
                    setattr(existing, key, value)
        else:
            self._session.add(model)
        
        await self._session.commit()
    
    async def find_by_id(self, card_id: UUID) -> Optional[CardAggregate]:
        result = await self._session.execute(
            select(CardModel).where(CardModel.id == card_id)
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        card = self._mapper.to_entity(model)
        return CardAggregate(card)
    
    async def find_by_content_url(self, user_id: UUID, content_url: ContentUrl) -> Optional[CardAggregate]:
        result = await self._session.execute(
            select(CardModel).where(
                and_(
                    CardModel.user_id == user_id,
                    CardModel.content_url == content_url.value
                )
            )
        )
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        card = self._mapper.to_entity(model)
        return CardAggregate(card)
    
    async def find_by_user_id(self, user_id: UUID, limit: int = 20, cursor: Optional[str] = None) -> List[CardAggregate]:
        query = select(CardModel).where(CardModel.user_id == user_id)
        
        if cursor:
            from datetime import datetime
            cursor_time = datetime.fromisoformat(cursor)
            query = query.where(CardModel.created_at < cursor_time)
        
        query = query.order_by(CardModel.created_at.desc()).limit(limit)
        
        result = await self._session.execute(query)
        models = result.scalars().all()
        
        return [CardAggregate(self._mapper.to_entity(model)) for model in models]
    
    async def delete(self, card_id: UUID) -> None:
        model = await self._session.get(CardModel, card_id)
        if model:
            await self._session.delete(model)
            await self._session.commit()
    
    async def exists_by_content_url(self, user_id: UUID, content_url: ContentUrl) -> bool:
        result = await self._session.execute(
            select(CardModel.id).where(
                and_(
                    CardModel.user_id == user_id,
                    CardModel.content_url == content_url.value
                )
            )
        )
        return result.scalar_one_or_none() is not None
