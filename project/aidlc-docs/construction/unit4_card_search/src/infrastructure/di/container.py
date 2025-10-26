"""Dependency Injection Container"""

import asyncpg
import aioredis
from functools import lru_cache

from ...config.settings import settings
from ...domain.services.search_query_validation_service import SearchQueryValidationService
from ...domain.services.search_execution_service import SearchExecutionService
from ...domain.services.search_suggestion_service import SearchSuggestionService
from ...domain.services.public_card_saving_service import PublicCardSavingService
from ...application.services.search_application_service import SearchApplicationService
from ...application.use_cases.search_my_cards_use_case import SearchMyCardsUseCase
from ...application.use_cases.search_public_cards_use_case import SearchPublicCardsUseCase
from ...application.use_cases.save_public_card_use_case import SavePublicCardUseCase
from ...application.use_cases.get_search_suggestions_use_case import GetSearchSuggestionsUseCase
from ...infrastructure.repositories.card_search_repository import CardSearchRepository
from ...infrastructure.repositories.search_suggestion_repository import SearchSuggestionRepository
from ...infrastructure.cache.search_cache_service import SearchCacheService
from ...infrastructure.events.event_publisher import RedisEventPublisher


class DIContainer:
    """의존성 주입 컨테이너"""
    
    def __init__(self):
        self._db_pool = None
        self._redis_client = None
        self._services = {}
    
    async def initialize(self):
        """컨테이너 초기화"""
        # 데이터베이스 연결
        self._db_pool = await asyncpg.create_pool(
            settings.database_url,
            min_size=5,
            max_size=settings.database_pool_size
        )
        
        # Redis 연결
        self._redis_client = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )
        
        # 서비스 등록
        self._register_services()
    
    def _register_services(self):
        """서비스 등록"""
        # 리포지토리
        card_search_repo = CardSearchRepository(self._db_pool)
        suggestion_repo = SearchSuggestionRepository(self._db_pool)
        
        # 캐시 서비스
        cache_service = SearchCacheService(self._redis_client)
        
        # 이벤트 발행자
        event_publisher = RedisEventPublisher(self._redis_client)
        
        # 도메인 서비스
        validation_service = SearchQueryValidationService()
        execution_service = SearchExecutionService(card_search_repo)
        suggestion_service = SearchSuggestionService(suggestion_repo)
        saving_service = PublicCardSavingService(card_search_repo, None, None)  # 실제 구현에서 주입
        
        # 유스케이스
        search_my_cards_uc = SearchMyCardsUseCase(validation_service, execution_service)
        search_public_cards_uc = SearchPublicCardsUseCase(validation_service, execution_service)
        save_public_card_uc = SavePublicCardUseCase(saving_service, event_publisher)
        get_suggestions_uc = GetSearchSuggestionsUseCase(suggestion_service, event_publisher)
        
        # 애플리케이션 서비스
        search_app_service = SearchApplicationService(
            search_my_cards_uc,
            search_public_cards_uc,
            save_public_card_uc,
            get_suggestions_uc,
            suggestion_service
        )
        
        self._services['search_application_service'] = search_app_service
    
    def get_search_service(self) -> SearchApplicationService:
        """검색 애플리케이션 서비스 조회"""
        return self._services['search_application_service']
    
    async def cleanup(self):
        """리소스 정리"""
        if self._db_pool:
            await self._db_pool.close()
        if self._redis_client:
            await self._redis_client.close()


# 전역 컨테이너 인스턴스
container = DIContainer()


@lru_cache()
def get_container() -> DIContainer:
    """컨테이너 인스턴스 조회"""
    return container
