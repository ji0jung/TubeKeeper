import pytest
from uuid import uuid4

from ...domain.value_objects.category_name import CategoryName
from ...domain.value_objects.category_type import CategoryType
from ...domain.value_objects.hierarchy_level import HierarchyLevel
from ...domain.entities.category import Category
from ...domain.entities.category_aggregate import CategoryAggregate

class TestCategoryName:
    def test_valid_name(self):
        name = CategoryName("테스트카테고리")
        assert name.value == "테스트카테고리"
    
    def test_invalid_empty_name(self):
        with pytest.raises(ValueError, match="카테고리 이름은 비어있을 수 없습니다"):
            CategoryName("")
    
    def test_invalid_long_name(self):
        with pytest.raises(ValueError, match="카테고리 이름은 10글자를 초과할 수 없습니다"):
            CategoryName("이것은매우긴카테고리이름입니다")
    
    def test_invalid_special_characters(self):
        with pytest.raises(ValueError, match="카테고리 이름은 영어, 숫자, 한글, 밑줄"):
            CategoryName("테스트@카테고리")

class TestCategoryType:
    def test_regular_category(self):
        cat_type = CategoryType.regular()
        assert not cat_type.is_system_category()
        assert cat_type.is_deletable()
    
    def test_system_category(self):
        cat_type = CategoryType.shared_cards()
        assert cat_type.is_system_category()
        assert not cat_type.is_deletable()

class TestHierarchyLevel:
    def test_valid_levels(self):
        level1 = HierarchyLevel(1)
        level2 = HierarchyLevel(2)
        level3 = HierarchyLevel(3)
        
        assert level1.is_root_level()
        assert not level2.is_root_level()
        assert level3.is_max_level()
    
    def test_invalid_level(self):
        with pytest.raises(ValueError, match="카테고리 계층은 1~3 레벨만 허용됩니다"):
            HierarchyLevel(4)
    
    def test_next_level(self):
        level1 = HierarchyLevel(1)
        level2 = level1.next_level()
        assert level2.value == 2

class TestCategoryAggregate:
    def test_create_category(self):
        user_id = uuid4()
        aggregate = CategoryAggregate(user_id)
        
        category = aggregate.create_category(CategoryName("테스트"))
        
        assert category.name.value == "테스트"
        assert category.user_id == user_id
        assert len(category.get_domain_events()) == 1
    
    def test_category_limit(self):
        user_id = uuid4()
        aggregate = CategoryAggregate(user_id)
        
        # 100개 카테고리 생성
        for i in range(100):
            aggregate.create_category(CategoryName(f"카테고리{i}"))
        
        # 101번째 카테고리 생성 시 예외 발생
        with pytest.raises(ValueError, match="사용자당 최대 100개의 카테고리만 생성할 수 있습니다"):
            aggregate.create_category(CategoryName("초과카테고리"))
