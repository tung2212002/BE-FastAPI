import asyncio
import json
from fastapi import WebSocket
from redis.asyncio import Redis
from typing import List, Dict, Set

from app.core.websocket.pubsub_manager import RedisPubSubManager
from app.core.loggers import logger


class WebsocketManager:
    def __init__(self) -> None:
        self.handler: Dict[str, callable] = {}
        self.conversations: Dict[int, Set[WebSocket]] = {}
        self.pubsub = RedisPubSubManager()
        self.user_id_to_websocket: Dict[int, Set[WebSocket]] = {}

    def handler_register(self, event: str, func: callable) -> None:
        self.handler[event] = func

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()

    async def add_user(self, user_id: int, websocket: WebSocket) -> None:
        if user_id not in self.user_id_to_websocket:
            self.user_id_to_websocket[user_id] = set()
        self.user_id_to_websocket[user_id].add(websocket)

    async def add_conversation(
        self, conversation_id: int, websocket: WebSocket
    ) -> None:
        if conversation_id in self.conversations:
            self.conversations[conversation_id].add(websocket)
        else:
            self.conversations[conversation_id] = set()
            self.conversations[conversation_id].add(websocket)
            await self.pubsub.connect()
            pubsub_subscribe = await self.pubsub.subscribe(conversation_id)
            asyncio.create_task(self.listen(pubsub_subscribe))

    async def remove_conversations(
        self, conversation_id: int, websocket: WebSocket
    ) -> None:
        self.conversations[conversation_id].remove(websocket)
        if len(self.conversations[conversation_id]) == 0:
            del self.conversations[conversation_id]
            await self.pubsub.unsubscribe(conversation_id)

    async def remove_user(self, user_id: int, websocket: WebSocket) -> None:
        self.user_id_to_websocket[user_id].remove(websocket)
        if len(self.user_id_to_websocket[user_id]) == 0:
            del self.user_id_to_websocket[user_id]

    async def broadcast(self, conversation_id: int, message: str | dict) -> None:
        if isinstance(message, dict):
            message = json.dumps(message)
        await self.pubsub.publish(conversation_id, message)

    async def listen(self, pubsub_subscribe: Redis) -> None:
        try:
            while True:
                message = await pubsub_subscribe.get_message(
                    ignore_subscribe_messages=True
                )
                if message is not None:
                    conversation_id = message["channel"].decode("utf-8")
                    message = message["data"].decode("utf-8")
                    conversation_id: int = int(conversation_id)
                    for ws in self.conversations[conversation_id]:
                        await ws.send_text(message)

        except Exception as e:
            logger.error(f"Error in listen: {e}")

    async def send_error(self, websocket: WebSocket, message: str) -> None:
        await websocket.send_json({"status": "error", "message": message})
