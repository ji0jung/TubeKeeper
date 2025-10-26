"""PaginationInfo Value Object"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from .search_scope import PaginationType


@dataclass(frozen=True)
class PaginationInfo:
    """페이징 정보를 나타내는 값 객체"""
    
    type: PaginationType
    cursor: Optional[datetime] = None
    page: Optional[int] = None
    limit: int = 20
    
    def __post_init__(self):
        """페이징 정보 유효성 검증"""
        if self.limit <= 0 or self.limit > 100:
            raise ValueError("limit은 1-100 사이여야 합니다")
        
        if self.type == PaginationType.CURSOR and self.cursor is None:
            # 첫 페이지는 cursor가 None일 수 있음
            pass
        elif self.type == PaginationType.OFFSET:
            if self.page is None:
                raise ValueError("오프셋 페이징에서는 page가 필요합니다")
            if self.page < 1:
                raise ValueError("page는 1 이상이어야 합니다")
    
    def is_cursor_based(self) -> bool:
        """커서 기반 페이징 여부"""
        return self.type == PaginationType.CURSOR
    
    def is_offset_based(self) -> bool:
        """오프셋 기반 페이징 여부"""
        return self.type == PaginationType.OFFSET
    
    def get_offset(self) -> int:
        """오프셋 값 계산"""
        if not self.is_offset_based() or self.page is None:
            return 0
        return (self.page - 1) * self.limit
    
    @classmethod
    def cursor_based(cls, cursor: Optional[datetime] = None, limit: int = 20) -> 'PaginationInfo':
        """커서 기반 페이징 정보 생성"""
        return cls(PaginationType.CURSOR, cursor=cursor, limit=limit)
    
    @classmethod
    def offset_based(cls, page: int = 1, limit: int = 20) -> 'PaginationInfo':
        """오프셋 기반 페이징 정보 생성"""
        return cls(PaginationType.OFFSET, page=page, limit=limit)
