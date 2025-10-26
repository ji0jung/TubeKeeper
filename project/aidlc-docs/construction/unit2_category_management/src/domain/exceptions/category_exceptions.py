class CategoryDomainException(Exception):
    pass

class CategoryNotFound(CategoryDomainException):
    def __init__(self, category_id: str):
        super().__init__(f"카테고리를 찾을 수 없습니다: {category_id}")

class CategoryLimitExceeded(CategoryDomainException):
    def __init__(self):
        super().__init__("사용자당 최대 100개의 카테고리만 생성할 수 있습니다")

class DuplicateCategoryName(CategoryDomainException):
    def __init__(self, name: str):
        super().__init__(f"같은 계층에서 중복된 카테고리 이름은 사용할 수 없습니다: {name}")

class SystemCategoryModificationNotAllowed(CategoryDomainException):
    def __init__(self):
        super().__init__("시스템 카테고리는 수정하거나 삭제할 수 없습니다")

class CategoryHasCards(CategoryDomainException):
    def __init__(self, card_count: int):
        super().__init__(f"카드가 있는 카테고리는 삭제할 수 없습니다 (카드 수: {card_count})")

class MaxHierarchyDepthExceeded(CategoryDomainException):
    def __init__(self):
        super().__init__("카테고리 계층은 최대 3단계까지만 허용됩니다")
