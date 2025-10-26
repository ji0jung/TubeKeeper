"""ResultMetadata Value Object"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass(frozen=True)
class ResultMetadata:
    """검색 결과 메타데이터를 나타내는 값 객체"""
    
    total_count: Optional[int] = None  # 오프셋 기반에서만 사용
    has_more: bool = False
    next_cursor: Optional[datetime] = None  # 커서 기반에서만 사용
    next_page: Optional[int] = None  # 오프셋 기반에서만 사용
    processing_time_ms: int = 0
    
    def has_next_page(self) -> bool:
        """다음 페이지 존재 여부"""
        return self.has_more
    
    def is_cursor_metadata(self) -> bool:
        """커서 기반 메타데이터 여부"""
        return self.next_cursor is not None
    
    def is_offset_metadata(self) -> bool:
        """오프셋 기반 메타데이터 여부"""
        return self.total_count is not None
    
    @classmethod
    def cursor_based(cls, has_more: bool, next_cursor: Optional[datetime] = None, 
                    processing_time_ms: int = 0) -> 'ResultMetadata':
        """커서 기반 메타데이터 생성"""
        return cls(
            has_more=has_more,
            next_cursor=next_cursor,
            processing_time_ms=processing_time_ms
        )
    
    @classmethod
    def offset_based(cls, total_count: int, current_page: int, limit: int,
                    processing_time_ms: int = 0) -> 'ResultMetadata':
        """오프셋 기반 메타데이터 생성"""
        has_more = (current_page * limit) < total_count
        next_page = current_page + 1 if has_more else None
        
        return cls(
            total_count=total_count,
            has_more=has_more,
            next_page=next_page,
            processing_time_ms=processing_time_ms
        )
