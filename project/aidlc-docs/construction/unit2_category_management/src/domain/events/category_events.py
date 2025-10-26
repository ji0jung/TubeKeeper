from dataclasses import dataclass
from uuid import UUID
from .base import DomainEvent

@dataclass
class CategoryCreated(DomainEvent):
    category_id: UUID
    category_name: str
    parent_id: UUID = None
    
    def __init__(self, user_id: UUID, category_id: UUID, category_name: str, parent_id: UUID = None):
        super().__init__(user_id)
        self.category_id = category_id
        self.category_name = category_name
        self.parent_id = parent_id

@dataclass
class CategoryDeleted(DomainEvent):
    category_id: UUID
    category_name: str
    card_count: int
    
    def __init__(self, user_id: UUID, category_id: UUID, category_name: str, card_count: int):
        super().__init__(user_id)
        self.category_id = category_id
        self.category_name = category_name
        self.card_count = card_count

@dataclass
class CategoryRenamed(DomainEvent):
    category_id: UUID
    old_name: str
    new_name: str
    
    def __init__(self, user_id: UUID, category_id: UUID, old_name: str, new_name: str):
        super().__init__(user_id)
        self.category_id = category_id
        self.old_name = old_name
        self.new_name = new_name

@dataclass
class SharedCardsCategoryCreated(DomainEvent):
    category_id: UUID
    
    def __init__(self, user_id: UUID, category_id: UUID):
        super().__init__(user_id)
        self.category_id = category_id

@dataclass
class TemporaryCategoryCreated(DomainEvent):
    category_id: UUID
    
    def __init__(self, user_id: UUID, category_id: UUID):
        super().__init__(user_id)
        self.category_id = category_id

@dataclass
class CardsMovedToCategory(DomainEvent):
    from_category_id: UUID
    to_category_id: UUID
    card_count: int
    
    def __init__(self, user_id: UUID, from_category_id: UUID, to_category_id: UUID, card_count: int):
        super().__init__(user_id)
        self.from_category_id = from_category_id
        self.to_category_id = to_category_id
        self.card_count = card_count
