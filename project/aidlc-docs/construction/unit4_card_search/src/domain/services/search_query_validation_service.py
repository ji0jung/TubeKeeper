"""SearchQueryValidationService"""

from uuid import UUID
from ..value_objects.search_criteria import SearchCriteria
from ..value_objects.search_scope import SearchScope


class ValidationResult:
    def __init__(self, is_valid: bool, error_message: str = ""):
        self.is_valid = is_valid
        self.error_message = error_message


class SearchQueryValidationService:
    """검색 쿼리 유효성 검증 서비스"""
    
    def validate_search_criteria(self, criteria: SearchCriteria, scope: SearchScope) -> ValidationResult:
        """검색 조건 유효성 검증"""
        # 공개 카드 검색 제약 검증
        if scope.is_public_cards():
            if criteria.has_category_filter():
                return ValidationResult(False, "공개 카드 검색에서는 카테고리 필터를 사용할 수 없습니다")
            
            if criteria.has_keyword() and criteria.has_tag():
                return ValidationResult(False, "공개 카드 검색에서는 키워드와 태그를 동시에 사용할 수 없습니다")
            
            if not (criteria.has_keyword() or criteria.has_tag()):
                return ValidationResult(False, "공개 카드 검색에서는 키워드 또는 태그가 필요합니다")
        
        return ValidationResult(True)
    
    def validate_tag_search(self, tag: str) -> ValidationResult:
        """태그 검색 유효성 검증"""
        if not tag or len(tag.strip()) == 0:
            return ValidationResult(False, "태그는 빈 문자열일 수 없습니다")
        
        if len(tag) > 50:
            return ValidationResult(False, "태그는 50글자를 초과할 수 없습니다")
        
        return ValidationResult(True)
    
    def validate_keyword_search(self, keyword: str) -> ValidationResult:
        """키워드 검색 유효성 검증"""
        if not keyword or len(keyword.strip()) < 2:
            return ValidationResult(False, "검색어는 최소 2글자 이상이어야 합니다")
        
        if len(keyword) > 100:
            return ValidationResult(False, "검색어는 100글자를 초과할 수 없습니다")
        
        return ValidationResult(True)
    
    def validate_category_filter(self, category_id: UUID, user_id: UUID) -> ValidationResult:
        """카테고리 필터 유효성 검증"""
        # 실제 구현에서는 카테고리 존재 여부 및 소유권 확인
        if not category_id:
            return ValidationResult(False, "유효하지 않은 카테고리 ID입니다")
        
        return ValidationResult(True)
