import asyncio
import logging
from typing import Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from ...domain.repositories.card_repository import CardRepository
from ...infrastructure.external_services.youtube_api_adapter import YouTubeApiAdapter
from ...infrastructure.external_services.s3_thumbnail_adapter import S3ThumbnailAdapter
from ...infrastructure.repositories.postgresql_card_repository import PostgreSQLCardRepository
from ...infrastructure.persistence.database import get_db_session

logger = logging.getLogger(__name__)

class MetadataWorker:
    def __init__(self):
        self._youtube_adapter = YouTubeApiAdapter()
        self._s3_adapter = S3ThumbnailAdapter()
    
    async def process_card_metadata(self, card_id: UUID) -> bool:
        """카드 메타데이터 수집 및 업데이트"""
        try:
            # 새로운 데이터베이스 세션 생성
            async for session in get_db_session():
                try:
                    card_repository = PostgreSQLCardRepository(session)
                    
                    # 카드 조회
                    card_aggregate = await card_repository.find_by_id(card_id)
                    if not card_aggregate:
                        logger.error(f"Card not found: {card_id}")
                        return False
                    
                    card = card_aggregate.card
                    
                    # YouTube 메타데이터 수집
                    metadata = await self._youtube_adapter.extract_metadata(card.content_url)
                    
                    # 썸네일 처리 및 S3 업로드
                    if metadata.thumbnail and metadata.thumbnail.youtube_url:
                        try:
                            # S3에 썸네일 업로드
                            s3_thumbnail = await self._s3_adapter.process_thumbnail(metadata.thumbnail.youtube_url)
                            metadata.update_thumbnail(s3_thumbnail)
                            logger.info(f"S3 thumbnail uploaded for card: {card_id}")
                        except Exception as s3_error:
                            logger.warning(f"S3 upload failed for card {card_id}, using YouTube URL: {s3_error}")
                            # S3 업로드 실패 시 YouTube URL 유지
                    
                    # 카드 업데이트
                    card_aggregate.update_metadata(metadata)
                    card.mark_as_completed()
                    
                    # 저장
                    await card_repository.save(card_aggregate)
                    
                    logger.info(f"Metadata processing completed for card: {card_id}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Failed to process metadata for card {card_id}: {e}")
                    
                    # 실패 상태로 업데이트
                    try:
                        card_aggregate = await card_repository.find_by_id(card_id)
                        if card_aggregate:
                            card_aggregate.card.mark_as_failed()
                            await card_repository.save(card_aggregate)
                    except Exception as save_error:
                        logger.error(f"Failed to mark card as failed: {save_error}")
                    
                    return False
                
                finally:
                    # 세션은 자동으로 정리됨 (async generator)
                    pass
            
        except Exception as e:
            logger.error(f"Database session error for card {card_id}: {e}")
            return False
