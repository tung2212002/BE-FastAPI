from fastapi import WebSocket, WebSocketDisconnect
from redis.asyncio import Redis
from sqlalchemy.orm import Session
from typing import List
from json.decoder import JSONDecodeError

from app.core.websocket.websocket_handler import websocket_handler, websocket_manager
from app.model import Account
from app.crud import conversation as conversationCRUD
from app.storage.cache.message_cache_service import message_cache_service


class WebsocketService:
    async def connect(
        self, websocket: WebSocket, db: Session, redis: Redis, current_user: Account
    ) -> None:
        await websocket_manager.connect(websocket)

        await websocket_manager.add_user(current_user.id, websocket)

        conversation_ids: List[int] = None
        try:
            conversation_ids = (
                await message_cache_service.get_cache_list_conversation_id(
                    redis, user_id=current_user.id
                )
            )
        except Exception as e:
            print(e)
        if not conversation_ids:
            conversation_ids = conversationCRUD.get_ids_by_account_id(
                db, account_id=current_user.id
            )
            try:
                await message_cache_service.cache_list_conversation_id(
                    redis, user_id=current_user.id, conversation_ids=conversation_ids
                )
            except Exception as e:
                print(e)

        for conversation_id in conversation_ids:
            await websocket_manager.add_conversation(conversation_id, websocket)

        try:
            while True:
                try:
                    incoming_message = await websocket.receive_json()
                    message_type = incoming_message.get("type")
                    message_data = incoming_message.get("data")

                    if not message_type or not message_data:
                        await websocket_manager.send_error(
                            websocket, "Message type or data is missing."
                        )
                        continue

                    handler = websocket_manager.handler.get(message_type)
                    if not handler:
                        await websocket_manager.send_error(
                            websocket, "Message type is invalid."
                        )
                        continue

                    await handler(
                        websocket,
                        db,
                        redis,
                        message_data,
                        current_user,
                    )

                except (JSONDecodeError, AttributeError) as e:
                    await websocket_manager.send_error(
                        websocket, "Invalid message format."
                    )
                    continue
                except ValueError as e:
                    print(e)
                    await websocket_manager.send_error(
                        websocket, "Could not validate message."
                    )
                    continue
        except WebSocketDisconnect:
            print("Disconnect---------")
            await websocket_manager.remove_user(current_user.id, websocket)
            for conversation_id in conversation_ids:
                await websocket_manager.remove_conversations(conversation_id, websocket)
            await websocket_manager.pubsub.close()


websocket_service = WebsocketService()
