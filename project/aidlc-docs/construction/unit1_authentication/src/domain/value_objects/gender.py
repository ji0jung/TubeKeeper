from enum import Enum


class Gender(Enum):
    """성별 값 객체"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    
    def __str__(self) -> str:
        return self.value
