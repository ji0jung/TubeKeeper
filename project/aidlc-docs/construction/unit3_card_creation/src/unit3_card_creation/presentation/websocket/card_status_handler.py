from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
from uuid import UUID
import json
import logging

logger = logging.getLogger(__name__)


class CardStatusHandler:
    def __init__(self):
        # user_id -> set of websockets
        self.connections: Dict[UUID, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: UUID):
        await websocket.accept()
        
        if user_id not in self.connections:
            self.connections[user_id] = set()
        
        self.connections[user_id].add(websocket)
        logger.info(f"WebSocket connected for user {user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: UUID):
        if user_id in self.connections:
            self.connections[user_id].discard(websocket)
            if not self.connections[user_id]:
                del self.connections[user_id]
        
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_card_status_update(self, user_id: UUID, card_id: UUID, status: str):
        if user_id not in self.connections:
            return
        
        message = {
            "type": "card_status_update",
            "card_id": str(card_id),
            "status": status,
            "timestamp": "2024-01-01T00:00:00Z"  # 실제로는 현재 시간
        }
        
        disconnected = set()
        for websocket in self.connections[user_id]:
            try:
                await websocket.send_text(json.dumps(message))
            except:
                disconnected.add(websocket)
        
        # 연결이 끊어진 WebSocket 제거
        for websocket in disconnected:
            self.connections[user_id].discard(websocket)

card_status_handler = CardStatusHandler()
