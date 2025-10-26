from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class VideoTitle:
    value: str
    
    def __post_init__(self):
        if not self.value.strip():
            raise ValueError("Video title cannot be empty")
        if len(self.value) > 200:
            raise ValueError("Video title too long")


@dataclass(frozen=True)
class Thumbnail:
    s3_url: str = ""
    youtube_url: str = ""
    
    def get_display_url(self) -> str:
        return self.s3_url if self.s3_url else self.youtube_url


@dataclass(frozen=True)
class Script:
    content: str
    language: str = "en"
    
    def __post_init__(self):
        if len(self.content) > 100000:
            raise ValueError("Script too long")
    
    def is_empty(self) -> bool:
        return not self.content.strip()
    
    def is_too_long_for_summary(self) -> bool:
        return len(self.content) > 50000


@dataclass(frozen=True)
class Tags:
    items: List[str]
    
    def __post_init__(self):
        if len(self.items) > 20:
            raise ValueError("Too many tags")
        for tag in self.items:
            if len(tag) > 50:
                raise ValueError("Tag too long")


@dataclass(frozen=True)
class Memo:
    content: str
    
    def __post_init__(self):
        if len(self.content) > 2000:
            raise ValueError("Memo too long")
    
    def is_empty(self) -> bool:
        return not self.content.strip()
