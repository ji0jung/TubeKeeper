from typing import List, Optional
from uuid import UUID

from ..entities.category import Category

class CategoryHierarchyService:
    
    def get_subcategories(self, categories: List[Category], parent_id: UUID) -> List[Category]:
        return [c for c in categories if c.parent_id == parent_id]
    
    def get_category_tree(self, categories: List[Category]) -> List[dict]:
        root_categories = [c for c in categories if c.parent_id is None]
        return [self._build_tree_node(c, categories) for c in root_categories]
    
    def _build_tree_node(self, category: Category, all_categories: List[Category]) -> dict:
        children = self.get_subcategories(all_categories, category.id)
        return {
            "id": category.id,
            "name": category.name.value,
            "type": category.category_type.value.value,
            "level": category.hierarchy_level.value,
            "children": [self._build_tree_node(child, all_categories) for child in children]
        }
