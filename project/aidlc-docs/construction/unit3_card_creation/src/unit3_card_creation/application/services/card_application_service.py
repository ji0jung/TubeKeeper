from typing import Optional, List, Dict
from uuid import UUID
from ..use_cases.create_card_use_case import CreateCardUseCase
from ..use_cases.get_card_use_case import GetCardUseCase
from ..use_cases.get_cards_by_user_use_case import GetCardsByUserUseCase
from ..use_cases.toggle_favorite_use_case import ToggleFavoriteUseCase
from ..commands.commands import CreateCardCommand, ToggleFavoriteCommand
from ..queries.queries import GetCardQuery, GetCardsByUserQuery
from ..queries.get_user_tags_query import GetUserTagsQuery
from ..dtos.card_dtos import CreateCardResult, CardDetailDto, CardListResult
from ...infrastructure.background.task_scheduler import TaskScheduler


class CardApplicationService:
    def __init__(
        self,
        create_card_use_case: CreateCardUseCase,
        get_card_use_case: GetCardUseCase,
        get_cards_by_user_use_case: GetCardsByUserUseCase,
        toggle_favorite_use_case: ToggleFavoriteUseCase,
        task_scheduler: TaskScheduler
    ):
        self._create_card_use_case = create_card_use_case
        self._get_card_use_case = get_card_use_case
        self._get_cards_by_user_use_case = get_cards_by_user_use_case
        self._toggle_favorite_use_case = toggle_favorite_use_case
        self._task_scheduler = task_scheduler
    
    async def create_card(self, command: CreateCardCommand) -> CreateCardResult:
        result = await self._create_card_use_case.execute(command)
        
        # 백그라운드에서 메타데이터 수집 시작
        self._task_scheduler.schedule_metadata_processing(result.card_id)
        
        return result
    
    async def get_card(self, query: GetCardQuery) -> Optional[CardDetailDto]:
        return await self._get_card_use_case.execute(query)
    
    async def get_cards_by_user(self, query: GetCardsByUserQuery) -> CardListResult:
        return await self._get_cards_by_user_use_case.execute(query)
    
    async def toggle_favorite(self, command: ToggleFavoriteCommand) -> bool:
        return await self._toggle_favorite_use_case.execute(command)
    
    async def update_card_metadata(self, card_id: UUID, user_id: UUID, memo: str, tags: list[str]) -> bool:
        """카드 메타데이터 업데이트 (메모, 태그)"""
        try:
            # 카드 조회 및 권한 확인
            card_aggregate = await self._get_card_use_case._card_repository.find_by_id(card_id)
            if not card_aggregate or card_aggregate.card.user_id != user_id:
                return False
            
            # 메모와 태그 업데이트
            if memo is not None:
                card_aggregate.card.update_memo(memo)
            if tags is not None:
                card_aggregate.card.update_tags(tags)
            
            # 저장
            await self._get_card_use_case._card_repository.save(card_aggregate)
            return True
            
        except Exception:
            return False
    
    async def delete_card(self, card_id: UUID, user_id: UUID) -> bool:
        """카드 삭제"""
        try:
            # 카드 조회 및 권한 확인
            card_aggregate = await self._get_card_use_case._card_repository.find_by_id(card_id)
            if not card_aggregate or card_aggregate.card.user_id != user_id:
                return False
            
            # 삭제 실행
            await self._get_card_use_case._card_repository.delete(card_id)
            return True
            
        except Exception:
            return False
    
    async def get_user_tags(self, query: GetUserTagsQuery) -> List[Dict[str, any]]:
        """사용자 태그 목록 조회 (사용 빈도순)"""
        # 사용자의 모든 카드 조회
        cards_query = GetCardsByUserQuery(
            user_id=query.user_id,
            limit=1000,  # 충분히 큰 수로 모든 카드 조회
            favorites_only=False
        )
        cards_result = await self._get_cards_by_user_use_case.execute(cards_query)
        
        print(f"DEBUG: 조회된 카드 수: {len(cards_result.cards)}")
        
        # 태그 빈도 계산
        tag_counter = {}
        for i, card in enumerate(cards_result.cards):
            print(f"DEBUG: 카드 {i+1} 태그: {card.tags}")
            for tag in card.tags:
                if tag in tag_counter:
                    tag_counter[tag] += 1
                else:
                    tag_counter[tag] = 1
        
        print(f"DEBUG: 태그 카운터: {tag_counter}")
        
        # 빈도순으로 정렬하여 반환
        sorted_tags = sorted(tag_counter.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                "name": tag_name,
                "count": count
            }
            for tag_name, count in sorted_tags
        ]
