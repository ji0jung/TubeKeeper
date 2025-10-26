"""SearchSuggestionRepository Implementation"""

from typing import List
from uuid import UUID
import asyncpg

from ...domain.repositories.search_repositories import ISearchSuggestionRepository
from ...domain.services.search_suggestion_service import TagSuggestion
from ...domain.value_objects.search_scope import SearchScope


class SearchSuggestionRepository(ISearchSuggestionRepository):
    """검색 제안 리포지토리 구현"""
    
    def __init__(self, db_pool):
        self._db_pool = db_pool
    
    async def get_recent_searches(self, user_id: UUID, limit: int) -> List[str]:
        """최근 검색어 조회"""
        query = """
        SELECT DISTINCT search_query
        FROM search_statistics
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT $2
        """
        
        async with self._db_pool.acquire() as conn:
            rows = await conn.fetch(query, user_id, limit)
        
        return [row['search_query'] for row in rows]
    
    async def save_recent_search(self, user_id: UUID, query: str) -> None:
        """최근 검색어 저장"""
        insert_query = """
        INSERT INTO search_statistics (user_id, search_query, search_scope, result_count, response_time_ms)
        VALUES ($1, $2, 'MY_CARDS', 0, 0)
        """
        
        async with self._db_pool.acquire() as conn:
            await conn.execute(insert_query, user_id, query)
    
    async def get_my_card_tags(self, user_id: UUID) -> List[TagSuggestion]:
        """내 카드 태그 조회"""
        query = """
        SELECT tag, COUNT(*) as count
        FROM (
            SELECT unnest(tags) as tag
            FROM cards 
            WHERE user_id = $1 AND deleted_at IS NULL
        ) tag_usage
        GROUP BY tag
        ORDER BY count DESC, tag ASC
        LIMIT 20
        """
        
        async with self._db_pool.acquire() as conn:
            rows = await conn.fetch(query, user_id)
        
        return [TagSuggestion(name=row['tag'], count=row['count']) for row in rows]
    
    async def get_popular_tags(self, scope: SearchScope, limit: int) -> List[TagSuggestion]:
        """인기 태그 조회"""
        if scope.is_public_cards():
            # 공개 카드의 인기 태그
            query = """
            SELECT tag, usage_count as count
            FROM popular_tags_view
            ORDER BY usage_count DESC
            LIMIT $1
            """
        else:
            # 전체 태그 (내 카드용)
            query = """
            SELECT tag, COUNT(*) as count
            FROM (
                SELECT unnest(tags) as tag
                FROM cards 
                WHERE deleted_at IS NULL
                  AND created_at > NOW() - INTERVAL '30 days'
            ) tag_usage
            GROUP BY tag
            HAVING COUNT(*) >= 2
            ORDER BY count DESC
            LIMIT $1
            """
        
        async with self._db_pool.acquire() as conn:
            rows = await conn.fetch(query, limit)
        
        return [TagSuggestion(name=row['tag'], count=row['count']) for row in rows]
