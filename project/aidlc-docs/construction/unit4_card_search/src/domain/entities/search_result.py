"""SearchResult Entity (Aggregate Root)"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List
from uuid import UUID, uuid4

from .card_summary import CardSummary
from ..value_objects.result_metadata import ResultMetadata


@dataclass
class SearchResult:
    """검색 결과 애그리게이트 루트"""
    
    id: UUID = field(default_factory=uuid4)
    search_query_id: UUID = field(default=None)
    card_summaries: List[CardSummary] = field(default_factory=list)
    metadata: ResultMetadata = field(default=None)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = field(default=None)
    
    def __post_init__(self):
        """초기화 후 만료 시간 설정"""
        if self.expires_at is None:
            # 기본 5분 후 만료
            self.expires_at = self.generated_at + timedelta(minutes=5)
    
    @classmethod
    def create(cls, search_query_id: UUID, card_summaries: List[CardSummary],
               metadata: ResultMetadata, ttl_minutes: int = 5) -> 'SearchResult':
        """새 검색 결과 생성"""
        now = datetime.utcnow()
        expires_at = now + timedelta(minutes=ttl_minutes)
        
        return cls(
            search_query_id=search_query_id,
            card_summaries=card_summaries,
            metadata=metadata,
            generated_at=now,
            expires_at=expires_at
        )
    
    def add_card(self, card_summary: CardSummary) -> None:
        """카드 요약 추가"""
        self.card_summaries.append(card_summary)
    
    def update_metadata(self, metadata: ResultMetadata) -> None:
        """메타데이터 갱신"""
        self.metadata = metadata
    
    def is_expired(self) -> bool:
        """만료 여부 확인"""
        return datetime.utcnow() > self.expires_at
    
    def get_page(self, start: int = 0, limit: int = 20) -> List[CardSummary]:
        """특정 페이지 결과 반환"""
        end = start + limit
        return self.card_summaries[start:end]
    
    def get_card_count(self) -> int:
        """카드 개수 반환"""
        return len(self.card_summaries)
    
    def extend_expiry(self, additional_minutes: int = 5) -> None:
        """만료 시간 연장"""
        self.expires_at = datetime.utcnow() + timedelta(minutes=additional_minutes)
