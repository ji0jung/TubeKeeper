from ...domain.entities.card import Card
from ...domain.entities.video_metadata import VideoMetadata
from ...domain.value_objects.content_url import ContentUrl
from ...domain.value_objects.card_status import CardStatus, CardStatusType
from ...domain.value_objects.basic_types import VideoTitle, Thumbnail, Script, Tags, Memo
from ..persistence.models import CardModel


class CardMapper:
    def to_model(self, card: Card) -> CardModel:
        return CardModel(
            id=card.card_id,
            user_id=card.user_id,
            category_id=card.category_id,
            content_url=card.content_url.value if card.content_url else "",
            
            # Video metadata
            video_title=card.video_metadata.video_title.value if card.video_metadata.video_title else None,
            thumbnail_s3_url=card.video_metadata.thumbnail.s3_url if card.video_metadata.thumbnail else "",
            thumbnail_youtube_url=card.video_metadata.thumbnail.youtube_url if card.video_metadata.thumbnail else "",
            
            # Card info
            memo=card.memo.content,
            tags=card.tags.items,
            status=card.status.value.value,
            duration=card.video_metadata.duration,
            published_at=card.video_metadata.published_at,
            
            # Favorite
            is_favorite=card.is_favorite,
            favorited_at=card.favorited_at,
            
            # Public
            is_public=card.is_public,
            
            # Timestamps
            created_at=card.created_at.replace(tzinfo=None) if card.created_at and card.created_at.tzinfo else card.created_at,
            updated_at=card.updated_at.replace(tzinfo=None) if card.updated_at and card.updated_at.tzinfo else card.updated_at
        )
    
    def to_entity(self, model: CardModel) -> Card:
        # Video metadata
        video_metadata = VideoMetadata()
        if model.video_title:
            video_metadata.video_title = VideoTitle(model.video_title)
        if model.thumbnail_s3_url or model.thumbnail_youtube_url:
            video_metadata.thumbnail = Thumbnail(model.thumbnail_s3_url, model.thumbnail_youtube_url)
        
        video_metadata.duration = model.duration
        video_metadata.published_at = model.published_at
        
        # Card
        card = Card(
            card_id=model.id,
            user_id=model.user_id,
            category_id=model.category_id,
            content_url=ContentUrl(model.content_url) if model.content_url else None,
            video_metadata=video_metadata,
            memo=Memo(model.memo or ""),
            tags=Tags(model.tags or []),
            status=CardStatus(CardStatusType(model.status)),
            is_favorite=model.is_favorite,
            favorited_at=model.favorited_at,
            is_public=model.is_public,
            created_at=model.created_at.replace(tzinfo=None) if model.created_at and model.created_at.tzinfo else model.created_at,
            updated_at=model.updated_at.replace(tzinfo=None) if model.updated_at and model.updated_at.tzinfo else model.updated_at
        )
        
        return card
