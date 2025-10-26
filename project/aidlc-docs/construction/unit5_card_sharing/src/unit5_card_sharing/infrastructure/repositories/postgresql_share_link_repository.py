import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from datetime import datetime

from ...domain.repositories.share_link_repository import ShareLinkRepository
from ...domain.entities.share_link_aggregate import ShareLinkAggregate
from ...domain.entities.share_link import ShareLink
from ...domain.value_objects.share_token import ShareToken
from ...domain.value_objects.expiration_date import ExpirationDate
from .models import ShareLinkModel

class PostgreSQLShareLinkRepository(ShareLinkRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, aggregate: ShareLinkAggregate) -> None:
        share_link = aggregate.share_link
        
        # 기존 레코드 조회
        stmt = select(ShareLinkModel).where(ShareLinkModel.id == share_link.id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            # 업데이트
            model.access_count = share_link.access_count
            model.is_active = share_link.is_active
        else:
            # 새로 생성
            model = ShareLinkModel(
                id=share_link.id,
                share_token=share_link.share_token.value,
                card_id=share_link.card_id,
                user_id=share_link.user_id,
                created_at=share_link.created_at,
                expires_at=share_link.expires_at.value,
                access_count=share_link.access_count,
                is_active=share_link.is_active
            )
            self._session.add(model)
        
        await self._session.commit()
    
    async def find_by_token(self, token: ShareToken) -> Optional[ShareLinkAggregate]:
        stmt = select(ShareLinkModel).where(ShareLinkModel.share_token == token.value)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        
        share_link = ShareLink(
            id=model.id,
            share_token=ShareToken(model.share_token),
            card_id=model.card_id,
            user_id=model.user_id,
            created_at=model.created_at,
            expires_at=ExpirationDate(model.expires_at),
            access_count=model.access_count,
            is_active=model.is_active
        )
        
        return ShareLinkAggregate(share_link)
    
    async def find_by_card_id(self, card_id: uuid.UUID) -> list[ShareLinkAggregate]:
        stmt = select(ShareLinkModel).where(ShareLinkModel.card_id == card_id)
        result = await self._session.execute(stmt)
        models = result.scalars().all()
        
        aggregates = []
        for model in models:
            share_link = ShareLink(
                id=model.id,
                share_token=ShareToken(model.share_token),
                card_id=model.card_id,
                user_id=model.user_id,
                created_at=model.created_at,
                expires_at=ExpirationDate(model.expires_at),
                access_count=model.access_count,
                is_active=model.is_active
            )
            aggregates.append(ShareLinkAggregate(share_link))
        
        return aggregates
    
    async def delete_expired_links(self) -> int:
        stmt = delete(ShareLinkModel).where(ShareLinkModel.expires_at < datetime.utcnow())
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount
