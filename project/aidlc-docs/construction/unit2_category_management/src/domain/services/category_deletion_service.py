from typing import List, Optional
from uuid import UUID

from ..entities.category import Category
from ..entities.category_aggregate import CategoryAggregate

class CategoryDeletionService:
    
    def can_delete_category(self, category: Category, card_count: int, subcategories: List[Category]) -> bool:
        if not category.can_be_deleted():
            return False
        
        if card_count > 0:
            return False
            
        if len(subcategories) > 0:
            return False
            
        return True
    
    def get_deletion_impact(self, category: Category, card_count: int, subcategories: List[Category]) -> dict:
        return {
            "category_id": category.id,
            "category_name": category.name.value,
            "card_count": card_count,
            "subcategory_count": len(subcategories),
            "subcategories": [{"id": sub.id, "name": sub.name.value} for sub in subcategories],
            "can_delete": self.can_delete_category(category, card_count, subcategories),
            "requires_card_migration": card_count > 0,
            "requires_subcategory_migration": len(subcategories) > 0
        }
