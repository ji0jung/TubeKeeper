from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from ..value_objects.basic_types import VideoTitle, Thumbnail


@dataclass
class VideoMetadata:
    video_title: Optional[VideoTitle] = None
    thumbnail: Optional[Thumbnail] = None
    duration: int = 0  # seconds
    published_at: Optional[datetime] = None
    
    def update_from_youtube(self, title: str, thumbnail_url: str, 
                          duration: int, published_at: datetime):
        """YouTube API 데이터로 메타데이터 업데이트"""
        self.video_title = VideoTitle(title)
        self.thumbnail = Thumbnail(youtube_url=thumbnail_url)
        self.duration = duration
        # timezone 정보 제거하여 naive datetime으로 저장
        self.published_at = published_at.replace(tzinfo=None) if published_at else None
    
    def update_thumbnail(self, thumbnail: Thumbnail):
        """썸네일 업데이트 (S3 URL 포함)"""
        self.thumbnail = thumbnail
