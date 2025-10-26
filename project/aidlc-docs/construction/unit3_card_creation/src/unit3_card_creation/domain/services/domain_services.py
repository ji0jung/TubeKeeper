from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from ..entities.card import Card
from ..entities.video_metadata import VideoMetadata
from ..value_objects.content_url import ContentUrl


class ContentMetadataExtractor(ABC):
    """콘텐츠 메타데이터 추출 서비스"""
    
    @abstractmethod
    async def extract_metadata(self, content_url: ContentUrl) -> VideoMetadata:
        """콘텐츠 URL에서 메타데이터 추출"""
        pass


class CardDuplicationChecker(ABC):
    """카드 중복 검사 서비스"""
    
    @abstractmethod
    async def check_duplicate(self, user_id: UUID, content_url: ContentUrl) -> Optional[Card]:
        """사용자의 동일한 URL 카드 존재 여부 확인"""
        pass
