"""Unit Tests for SearchQueryValidationService"""

import pytest
from uuid import uuid4

from ...domain.services.search_query_validation_service import SearchQueryValidationService
from ...domain.value_objects.search_criteria import SearchCriteria
from ...domain.value_objects.search_scope import SearchScope


class TestSearchQueryValidationService:
    """SearchQueryValidationService 단위 테스트"""
    
    def setup_method(self):
        self.service = SearchQueryValidationService()
    
    def test_validate_my_cards_search_with_keyword(self):
        """내 카드 키워드 검색 유효성 검증"""
        criteria = SearchCriteria(keyword="test")
        scope = SearchScope.my_cards()
        
        result = self.service.validate_search_criteria(criteria, scope)
        
        assert result.is_valid
    
    def test_validate_my_cards_search_with_category(self):
        """내 카드 카테고리 필터 유효성 검증"""
        criteria = SearchCriteria(category_id=uuid4())
        scope = SearchScope.my_cards()
        
        result = self.service.validate_search_criteria(criteria, scope)
        
        assert result.is_valid
    
    def test_validate_public_cards_search_with_keyword(self):
        """공개 카드 키워드 검색 유효성 검증"""
        criteria = SearchCriteria(keyword="test")
        scope = SearchScope.public_cards()
        
        result = self.service.validate_search_criteria(criteria, scope)
        
        assert result.is_valid
    
    def test_validate_public_cards_search_with_category_should_fail(self):
        """공개 카드 검색에서 카테고리 필터 사용 시 실패"""
        criteria = SearchCriteria(category_id=uuid4())
        scope = SearchScope.public_cards()
        
        result = self.service.validate_search_criteria(criteria, scope)
        
        assert not result.is_valid
        assert "카테고리 필터를 사용할 수 없습니다" in result.error_message
    
    def test_validate_public_cards_search_with_keyword_and_tag_should_fail(self):
        """공개 카드 검색에서 키워드와 태그 동시 사용 시 실패"""
        criteria = SearchCriteria(keyword="test", tag="tag")
        scope = SearchScope.public_cards()
        
        result = self.service.validate_search_criteria(criteria, scope)
        
        assert not result.is_valid
        assert "동시에 사용할 수 없습니다" in result.error_message
    
    def test_validate_keyword_search_too_short(self):
        """검색어 길이 부족 시 실패"""
        result = self.service.validate_keyword_search("a")
        
        assert not result.is_valid
        assert "최소 2글자" in result.error_message
    
    def test_validate_keyword_search_too_long(self):
        """검색어 길이 초과 시 실패"""
        long_keyword = "a" * 101
        result = self.service.validate_keyword_search(long_keyword)
        
        assert not result.is_valid
        assert "100글자를 초과" in result.error_message
