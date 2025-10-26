import asyncio
import logging
from typing import Dict, Set
from uuid import UUID
from .metadata_worker import MetadataWorker

logger = logging.getLogger(__name__)

class TaskScheduler:
    """간단한 인메모리 백그라운드 작업 스케줄러"""
    
    def __init__(self):
        self._running_tasks: Dict[UUID, asyncio.Task] = {}
        self._completed_tasks: Set[UUID] = set()
    
    def schedule_metadata_processing(self, card_id: UUID) -> None:
        """메타데이터 처리 작업 스케줄링"""
        if card_id in self._running_tasks:
            logger.info(f"Metadata processing already scheduled for card: {card_id}")
            return
        
        # 백그라운드 작업 시작
        task = asyncio.create_task(self._process_metadata_task(card_id))
        self._running_tasks[card_id] = task
        
        logger.info(f"Scheduled metadata processing for card: {card_id}")
    
    async def _process_metadata_task(self, card_id: UUID) -> None:
        """메타데이터 처리 작업 실행"""
        try:
            # 새로운 워커 인스턴스 생성 (독립적인 DB 연결)
            metadata_worker = MetadataWorker()
            success = await metadata_worker.process_card_metadata(card_id)
            
            if success:
                self._completed_tasks.add(card_id)
                logger.info(f"Metadata processing completed for card: {card_id}")
            else:
                logger.error(f"Metadata processing failed for card: {card_id}")
                
        except Exception as e:
            logger.error(f"Unexpected error in metadata processing for card {card_id}: {e}")
        
        finally:
            # 완료된 작업 정리
            if card_id in self._running_tasks:
                del self._running_tasks[card_id]
    
    def get_task_status(self, card_id: UUID) -> str:
        """작업 상태 조회"""
        if card_id in self._running_tasks:
            return "PROCESSING"
        elif card_id in self._completed_tasks:
            return "COMPLETED"
        else:
            return "NOT_SCHEDULED"
    
    def get_running_tasks_count(self) -> int:
        """실행 중인 작업 수"""
        return len(self._running_tasks)
    
    async def shutdown(self) -> None:
        """스케줄러 종료 및 모든 작업 대기"""
        logger.info("Shutting down task scheduler...")
        
        if self._running_tasks:
            logger.info(f"Waiting for {len(self._running_tasks)} running tasks to complete...")
            await asyncio.gather(*self._running_tasks.values(), return_exceptions=True)
        
        logger.info("Task scheduler shutdown complete")
