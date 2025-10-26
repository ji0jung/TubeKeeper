"""SearchCriteria Value Object"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class SearchCriteria:
    """검색 조건을 나타내는 값 객체"""
    
    keyword: Optional[str] = None
    tag: Optional[str] = None
    category_id: Optional[UUID] = None
    
    def __post_init__(self):
        """검색 조건 유효성 검증"""
        if self.keyword:
            if len(self.keyword.strip()) < 2:
                raise ValueError("검색어는 최소 2글자 이상이어야 합니다")
            if len(self.keyword) > 100:
                raise ValueError("검색어는 100글자를 초과할 수 없습니다")
        
        if self.tag and len(self.tag.strip()) == 0:
            raise ValueError("태그는 빈 문자열일 수 없습니다")
    
    def has_keyword(self) -> bool:
        """키워드 검색 여부"""
        return self.keyword is not None and len(self.keyword.strip()) > 0
    
    def has_tag(self) -> bool:
        """태그 검색 여부"""
        return self.tag is not None and len(self.tag.strip()) > 0
    
    def has_category_filter(self) -> bool:
        """카테고리 필터 여부"""
        return self.category_id is not None
    
    def is_empty(self) -> bool:
        """검색 조건이 비어있는지 확인"""
        return not (self.has_keyword() or self.has_tag() or self.has_category_filter())
