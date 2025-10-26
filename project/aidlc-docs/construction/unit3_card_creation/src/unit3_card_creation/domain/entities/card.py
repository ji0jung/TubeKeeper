from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from ..value_objects.content_url import ContentUrl
from ..value_objects.card_status import CardStatus, CardStatusType
from ..value_objects.basic_types import Tags, Memo
from .video_metadata import VideoMetadata


@dataclass
class Card:
    card_id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    category_id: UUID = field(default_factory=uuid4)
    content_url: Optional[ContentUrl] = None
    video_metadata: VideoMetadata = field(default_factory=VideoMetadata)
    memo: Memo = field(default_factory=lambda: Memo(""))
    tags: Tags = field(default_factory=lambda: Tags([]))
    status: CardStatus = field(default_factory=lambda: CardStatus(CardStatusType.CREATING))
    is_favorite: bool = False
    favorited_at: Optional[datetime] = None
    is_public: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.utcnow().replace(tzinfo=None))
    updated_at: datetime = field(default_factory=lambda: datetime.utcnow().replace(tzinfo=None))
    
    @classmethod
    def create(cls, user_id: UUID, category_id: UUID, content_url: ContentUrl, 
               memo: str = "", tags: list[str] = None) -> 'Card':
        return cls(
            user_id=user_id,
            category_id=category_id,
            content_url=content_url,
            memo=Memo(memo),
            tags=Tags(tags or []),
            status=CardStatus(CardStatusType.CREATING)
        )
    
    def update_metadata(self, metadata: VideoMetadata):
        """메타데이터 업데이트 후 완료 상태로 변경"""
        self.video_metadata = metadata
        self.status = CardStatus(CardStatusType.COMPLETED)
        self.updated_at = datetime.utcnow().replace(tzinfo=None)
    
    def toggle_favorite(self):
        """즐겨찾기 토글"""
        self.is_favorite = not self.is_favorite
        self.favorited_at = datetime.utcnow().replace(tzinfo=None) if self.is_favorite else None
        self.updated_at = datetime.utcnow().replace(tzinfo=None)
    
    def toggle_public(self):
        """공개 설정 토글"""
        self.is_public = not self.is_public
        self.updated_at = datetime.utcnow().replace(tzinfo=None)
    
    def update_memo(self, memo_content: str):
        """메모 업데이트"""
        self.memo = Memo(memo_content)
        self.updated_at = datetime.utcnow().replace(tzinfo=None)
    
    def update_tags(self, tag_list: list[str]):
        """태그 업데이트"""
        self.tags = Tags(tag_list)
        self.updated_at = datetime.utcnow().replace(tzinfo=None)
    
    def mark_as_completed(self):
        """카드를 완료 상태로 변경"""
        self.status = CardStatus(CardStatusType.COMPLETED)
        self.updated_at = datetime.utcnow().replace(tzinfo=None)
    
    def mark_as_failed(self):
        """카드를 실패 상태로 변경"""
        self.status = CardStatus(CardStatusType.FAILED)
        self.updated_at = datetime.utcnow().replace(tzinfo=None)
