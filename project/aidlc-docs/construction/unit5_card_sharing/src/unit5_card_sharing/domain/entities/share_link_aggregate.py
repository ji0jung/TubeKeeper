import uuid
from typing import List
from .share_link import ShareLink
from ..events.domain_events import ShareLinkCreated, ShareLinkAccessed
from ..value_objects.share_token import ShareToken

class ShareLinkAggregate:
    def __init__(self, share_link: ShareLink):
        self._share_link = share_link
        self._domain_events: List = []
    
    @classmethod
    def create(cls, card_id: uuid.UUID, user_id: uuid.UUID) -> 'ShareLinkAggregate':
        share_link = ShareLink(card_id=card_id, user_id=user_id)
        aggregate = cls(share_link)
        aggregate._add_event(ShareLinkCreated(
            share_token=share_link.share_token.value,
            card_id=card_id,
            user_id=user_id,
            expires_at=share_link.expires_at.value
        ))
        return aggregate
    
    def access(self, user_agent: str = None, ip_address: str = None) -> None:
        if self._share_link.is_expired():
            raise ValueError("Share link has expired")
        
        self._share_link.increment_access_count()
        self._add_event(ShareLinkAccessed(
            share_token=self._share_link.share_token.value,
            user_agent=user_agent,
            ip_address=ip_address
        ))
    
    @property
    def share_link(self) -> ShareLink:
        return self._share_link
    
    @property
    def domain_events(self) -> List:
        return self._domain_events.copy()
    
    def clear_events(self) -> None:
        self._domain_events.clear()
    
    def _add_event(self, event) -> None:
        self._domain_events.append(event)
