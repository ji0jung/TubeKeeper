"""CardSearchRepository Implementation"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
import asyncpg

from ...domain.repositories.search_repositories import ICardSearchRepository, SearchResultData
from ...domain.entities.card_summary import CardSummary
from ...domain.value_objects.search_criteria import SearchCriteria
from ...domain.value_objects.pagination_info import PaginationInfo


class CardSearchRepository(ICardSearchRepository):
    """카드 검색 리포지토리 구현"""
    
    def __init__(self, db_pool):
        self._db_pool = db_pool
    
    async def search_my_cards(self, user_id: UUID, criteria: SearchCriteria, 
                            pagination: PaginationInfo) -> List[CardSummary]:
        """내 카드 검색 (커서 기반)"""
        query = """
        SELECT c.id, c.title, c.thumbnail, c.summary, c.tags, 
               cat.name as category_name, c.is_favorite, c.created_at
        FROM cards c
        LEFT JOIN categories cat ON c.category_id = cat.id
        WHERE c.user_id = $1 AND c.deleted_at IS NULL
        """
        params = [user_id]
        param_count = 1
        
        # 커서 조건
        if pagination.cursor:
            query += f" AND c.created_at < ${param_count + 1}"
            params.append(pagination.cursor)
            param_count += 1
        
        # 카테고리 필터
        if criteria.has_category_filter():
            query += f" AND c.category_id = ${param_count + 1}"
            params.append(criteria.category_id)
            param_count += 1
        
        # 키워드 검색
        if criteria.has_keyword():
            query += f" AND to_tsvector('korean', c.title || ' ' || coalesce(c.summary, '') || ' ' || coalesce(c.memo, '')) @@ plainto_tsquery('korean', ${param_count + 1})"
            params.append(criteria.keyword)
            param_count += 1
        
        # 태그 검색
        if criteria.has_tag():
            query += f" AND ${param_count + 1} = ANY(c.tags)"
            params.append(criteria.tag)
            param_count += 1
        
        query += f" ORDER BY c.created_at DESC LIMIT ${param_count + 1}"
        params.append(pagination.limit + 1)  # +1 for has_more check
        
        async with self._db_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            
        return [self._row_to_card_summary(row, is_my_card=True) for row in rows]
    
    async def search_public_cards(self, criteria: SearchCriteria, pagination: PaginationInfo,
                                exclude_user_id: UUID) -> SearchResultData:
        """공개 카드 검색 (오프셋 기반)"""
        base_query = """
        FROM cards c
        JOIN users u ON c.user_id = u.id
        WHERE c.is_public = true AND c.user_id != $1 AND c.deleted_at IS NULL
        """
        params = [exclude_user_id]
        param_count = 1
        
        # 검색 조건
        if criteria.has_keyword():
            base_query += f" AND to_tsvector('korean', c.title || ' ' || coalesce(c.summary, '')) @@ plainto_tsquery('korean', ${param_count + 1})"
            params.append(criteria.keyword)
            param_count += 1
        elif criteria.has_tag():
            base_query += f" AND ${param_count + 1} = ANY(c.tags)"
            params.append(criteria.tag)
            param_count += 1
        
        # 총 개수 조회
        count_query = "SELECT COUNT(*) " + base_query
        
        # 데이터 조회
        select_query = f"""
        SELECT c.id, c.title, c.thumbnail, c.summary, c.tags,
               u.name as owner_name, c.created_at,
               CASE 
                 WHEN $2 IS NOT NULL THEN
                   ts_rank(to_tsvector('korean', c.title || ' ' || coalesce(c.summary, '')), 
                           plainto_tsquery('korean', $2))
                 ELSE 1.0
               END as relevance_score
        {base_query}
        ORDER BY relevance_score DESC, c.created_at DESC
        OFFSET ${param_count + 1} LIMIT ${param_count + 2}
        """
        
        offset = pagination.get_offset()
        params.extend([offset, pagination.limit])
        
        async with self._db_pool.acquire() as conn:
            total_count = await conn.fetchval(count_query, *params[:-2])
            rows = await conn.fetch(select_query, *params)
        
        cards = [self._row_to_card_summary(row, is_my_card=False) for row in rows]
        return SearchResultData(cards, total_count)
    
    async def get_public_card(self, card_id: UUID) -> Optional[CardSummary]:
        """공개 카드 조회"""
        query = """
        SELECT c.id, c.title, c.thumbnail, c.summary, c.tags, c.content_url,
               u.name as owner_name, c.created_at, c.is_public, c.user_id
        FROM cards c
        JOIN users u ON c.user_id = u.id
        WHERE c.id = $1 AND c.is_public = true AND c.deleted_at IS NULL
        """
        
        async with self._db_pool.acquire() as conn:
            row = await conn.fetchrow(query, card_id)
        
        return self._row_to_card_summary(row, is_my_card=False) if row else None
    
    def _row_to_card_summary(self, row, is_my_card: bool) -> CardSummary:
        """DB 행을 CardSummary로 변환"""
        return CardSummary(
            card_id=row['id'],
            title=row['title'],
            thumbnail=row['thumbnail'],
            summary=row['summary'] or "",
            tags=row['tags'] or [],
            category_name=row.get('category_name') if is_my_card else None,
            owner_name=row.get('owner_name') if not is_my_card else None,
            is_favorite=row.get('is_favorite', False) if is_my_card else False,
            is_public=row.get('is_public', False),
            created_at=row['created_at']
        )
