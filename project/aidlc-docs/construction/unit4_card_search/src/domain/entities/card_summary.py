"""CardSummary Entity"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from uuid import UUID


@dataclass
class CardSummary:
    """검색 결과용 카드 요약 엔티티"""
    
    card_id: UUID
    title: str
    thumbnail: str
    summary: str
    tags: List[str]
    category_name: Optional[str] = None  # 내 카드만
    owner_name: Optional[str] = None  # 공개 카드만
    is_favorite: bool = False  # 내 카드만
    is_public: bool = False
    created_at: datetime = None
    
    def highlight_keyword(self, keyword: str) -> dict:
        """키워드 하이라이트 정보 생성 (클라이언트에서 사용)"""
        if not keyword:
            return {}
        
        keyword_lower = keyword.lower()
        highlights = {}
        
        # 제목에서 키워드 위치 찾기
        title_lower = self.title.lower()
        if keyword_lower in title_lower:
            start = title_lower.find(keyword_lower)
            highlights['title'] = {
                'start': start,
                'end': start + len(keyword),
                'text': keyword
            }
        
        # 요약에서 키워드 위치 찾기
        summary_lower = self.summary.lower()
        if keyword_lower in summary_lower:
            start = summary_lower.find(keyword_lower)
            highlights['summary'] = {
                'start': start,
                'end': start + len(keyword),
                'text': keyword
            }
        
        return highlights
    
    def is_my_card(self) -> bool:
        """내 카드 여부"""
        return self.category_name is not None
    
    def is_shared_card(self) -> bool:
        """공유받은 카드 여부"""
        return self.owner_name is not None
    
    @classmethod
    def from_card(cls, card, category_name: Optional[str] = None, 
                  owner_name: Optional[str] = None) -> 'CardSummary':
        """Card 엔티티에서 CardSummary 생성"""
        return cls(
            card_id=card.id,
            title=card.title,
            thumbnail=card.thumbnail,
            summary=card.summary or "",
            tags=card.tags or [],
            category_name=category_name,
            owner_name=owner_name,
            is_favorite=getattr(card, 'is_favorite', False),
            is_public=card.is_public,
            created_at=card.created_at
        )
