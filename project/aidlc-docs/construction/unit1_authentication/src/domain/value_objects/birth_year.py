from dataclasses import dataclass
from datetime import datetime
from domain.exceptions.domain_exceptions import InvalidBirthYearException


@dataclass(frozen=True)
class BirthYear:
    """출생년도 값 객체"""
    value: int
    
    def __post_init__(self):
        current_year = datetime.now().year
        if not (1900 <= self.value <= current_year):
            raise InvalidBirthYearException(
                f"Birth year must be between 1900 and {current_year}, got: {self.value}"
            )
    
    def __str__(self) -> str:
        return str(self.value)
