from enum import Enum


class Language(Enum):
    """언어 값 객체"""
    KOREAN = "ko"
    ENGLISH = "en"
    
    def __str__(self) -> str:
        return self.value
