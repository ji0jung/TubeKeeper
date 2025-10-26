from dataclasses import dataclass
from uuid import UUID

@dataclass
class GetUserTagsQuery:
    """사용자 태그 목록 조회 쿼리"""
    user_id: UUID
