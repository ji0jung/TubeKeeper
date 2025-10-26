"""SearchQuery Entity (Aggregate Root)"""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import List

from ..value_objects.search_criteria import SearchCriteria
from ..value_objects.search_scope import SearchScope
from ..value_objects.pagination_info import PaginationInfo
from ..events.domain_events import SearchQueryCreated


@dataclass
class SearchQuery:
    """검색 쿼리 애그리게이트 루트"""
    
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default=None)
    criteria: SearchCriteria = field(default=None)
    scope: SearchScope = field(default=None)
    pagination_info: PaginationInfo = field(default=None)
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used_at: datetime = field(default_factory=datetime.utcnow)
    
    # Domain Events
    _domain_events: List = field(default_factory=list, init=False)
    
    @classmethod
    def create(cls, user_id: UUID, criteria: SearchCriteria, 
               scope: SearchScope, pagination_info: PaginationInfo) -> 'SearchQuery':
        """새 검색 쿼리 생성"""
        # 검색 조건 유효성 검증
        cls._validate_criteria(criteria, scope)
        
        search_query = cls(
            user_id=user_id,
            criteria=criteria,
            scope=scope,
            pagination_info=pagination_info
        )
        
        # 도메인 이벤트 발행
        search_query._add_domain_event(SearchQueryCreated(
            search_query_id=search_query.id,
            user_id=user_id,
            criteria=criteria,
            scope=scope,
            occurred_at=search_query.created_at
        ))
        
        return search_query
    
    def update_criteria(self, criteria: SearchCriteria) -> None:
        """검색 조건 수정"""
        self._validate_criteria(criteria, self.scope)
        self.criteria = criteria
        self.last_used_at = datetime.utcnow()
    
    def change_scope(self, scope: SearchScope) -> None:
        """검색 범위 변경"""
        self._validate_criteria(self.criteria, scope)
        self.scope = scope
        self.last_used_at = datetime.utcnow()
    
    def update_pagination(self, pagination_info: PaginationInfo) -> None:
        """페이징 정보 업데이트"""
        self.pagination_info = pagination_info
        self.last_used_at = datetime.utcnow()
    
    def mark_as_used(self) -> None:
        """최근 사용 시간 갱신"""
        self.last_used_at = datetime.utcnow()
    
    @staticmethod
    def _validate_criteria(criteria: SearchCriteria, scope: SearchScope) -> None:
        """검색 조건 유효성 검증"""
        # 공개 카드 검색에서 카테고리 필터 사용 불가
        if scope.is_public_cards() and criteria.has_category_filter():
            raise ValueError("공개 카드 검색에서는 카테고리 필터를 사용할 수 없습니다")
        
        # 공개 카드 검색에서 키워드와 태그 동시 사용 불가
        if scope.is_public_cards() and criteria.has_keyword() and criteria.has_tag():
            raise ValueError("공개 카드 검색에서는 키워드와 태그를 동시에 사용할 수 없습니다")
        
        # 공개 카드 검색에서는 키워드 또는 태그 중 하나는 필수
        if scope.is_public_cards() and not (criteria.has_keyword() or criteria.has_tag()):
            raise ValueError("공개 카드 검색에서는 키워드 또는 태그가 필요합니다")
    
    def _add_domain_event(self, event) -> None:
        """도메인 이벤트 추가"""
        self._domain_events.append(event)
    
    def get_domain_events(self) -> List:
        """도메인 이벤트 목록 반환"""
        return self._domain_events.copy()
    
    def clear_domain_events(self) -> None:
        """도메인 이벤트 목록 초기화"""
        self._domain_events.clear()
