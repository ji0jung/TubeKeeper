import aiohttp
import os
from datetime import datetime
from ...domain.services.domain_services import ContentMetadataExtractor
from ...domain.entities.video_metadata import VideoMetadata
from ...domain.value_objects.content_url import ContentUrl
from ...domain.value_objects.basic_types import VideoTitle, Thumbnail


class YouTubeApiAdapter(ContentMetadataExtractor):
    def __init__(self):
        self._api_key = os.getenv("YOUTUBE_API_KEY")
        if not self._api_key:
            raise ValueError("YOUTUBE_API_KEY environment variable is required")
        self._base_url = "https://www.googleapis.com/youtube/v3"
    
    async def extract_metadata(self, content_url: ContentUrl) -> VideoMetadata:
        video_id = content_url.get_video_id()
        
        async with aiohttp.ClientSession() as session:
            video_info = await self._get_video_info(session, video_id)
            
            metadata = VideoMetadata()
            metadata.update_from_youtube(
                title=video_info["title"],
                thumbnail_url=video_info["thumbnail"],
                duration=video_info["duration"],
                published_at=video_info["published_at"]
            )
            
            return metadata
    
    async def _get_video_info(self, session: aiohttp.ClientSession, video_id: str) -> dict:
        url = f"{self._base_url}/videos"
        params = {
            "part": "snippet,contentDetails",
            "id": video_id,
            "key": self._api_key
        }
        
        async with session.get(url, params=params) as response:
            if response.status != 200:
                raise Exception(f"YouTube API error: {response.status}")
            
            data = await response.json()
            if not data.get("items"):
                raise Exception("Video not found")
            
            item = data["items"][0]
            snippet = item["snippet"]
            
            return {
                "title": snippet["title"],
                "thumbnail": snippet["thumbnails"]["high"]["url"],
                "duration": self._parse_duration(item["contentDetails"]["duration"]),
                "published_at": datetime.fromisoformat(snippet["publishedAt"].replace("Z", "+00:00")).replace(tzinfo=None)
            }
    
    def _parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration to seconds"""
        import re
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
