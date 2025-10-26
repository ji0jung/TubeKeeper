from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from .database import Base


class CardModel(Base):
    __tablename__ = "cards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    category_id = Column(UUID(as_uuid=True), nullable=False)
    content_url = Column(String(500), nullable=False)
    
    # Video metadata
    video_title = Column(String(200))
    thumbnail_s3_url = Column(String(500))
    thumbnail_youtube_url = Column(String(500))
    
    # Card info
    memo = Column(Text)
    tags = Column(JSON)
    status = Column(String(20), nullable=False)
    duration = Column(Integer, default=0)
    published_at = Column(DateTime)
    
    # Favorite
    is_favorite = Column(Boolean, default=False)
    favorited_at = Column(DateTime)
    
    # Public
    is_public = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.utcnow().replace(tzinfo=None))
    updated_at = Column(DateTime, default=lambda: datetime.utcnow().replace(tzinfo=None), 
                       onupdate=lambda: datetime.utcnow().replace(tzinfo=None))
