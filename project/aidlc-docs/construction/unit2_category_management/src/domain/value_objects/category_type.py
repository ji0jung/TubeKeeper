from enum import Enum
from dataclasses import dataclass

class CategoryTypeEnum(Enum):
    REGULAR = "regular"
    SHARED_CARDS = "shared_cards"
    TEMPORARY = "temporary"

@dataclass(frozen=True)
class CategoryType:
    value: CategoryTypeEnum
    
    @classmethod
    def regular(cls):
        return cls(CategoryTypeEnum.REGULAR)
    
    @classmethod
    def shared_cards(cls):
        return cls(CategoryTypeEnum.SHARED_CARDS)
    
    @classmethod
    def temporary(cls):
        return cls(CategoryTypeEnum.TEMPORARY)
    
    def is_system_category(self) -> bool:
        return self.value in [CategoryTypeEnum.SHARED_CARDS, CategoryTypeEnum.TEMPORARY]
    
    def is_deletable(self) -> bool:
        return self.value == CategoryTypeEnum.REGULAR
