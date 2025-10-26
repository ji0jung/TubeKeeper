import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ContentUrl:
    value: str
    
    def __post_init__(self):
        if not self.is_valid():
            raise ValueError(f"Invalid YouTube URL: {self.value}")
    
    def is_valid(self) -> bool:
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
            r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})'
        ]
        return any(re.match(pattern, self.value) for pattern in youtube_patterns)
    
    def normalize(self) -> 'ContentUrl':
        video_id = self.get_video_id()
        if video_id:
            return ContentUrl(f"https://www.youtube.com/watch?v={video_id}")
        return self
    
    def get_video_id(self) -> Optional[str]:
        patterns = [
            r'(?:v=|/)([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, self.value)
            if match:
                return match.group(1)
        return None
