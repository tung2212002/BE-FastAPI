from fastapi import WebSocket
from sqlalchemy.orm import Session
from redis.asyncio import Redis
from typing import List, Union

from app.core.websocket.websocket_manager import WebsocketManager
from app.model import (
    Message,
    MessageAttachment,
    ConversationMember,
    Account,
    Conversation,
)
from app.schema.websocket import (
    NewMessageSchema,
    NewConversationSchema,
    UpdateConversationSchema,
    UserTypingSchema,
    AddMemberSchema,
    ResponseMessageSchema,
)
from app.schema.account import AccountBasicResponse
from app.schema.message import MessageCreate, MessageUpdate
from app.schema.message_attachment import MessageAttachmentCreate
from app.schema.conversation_member import ConversationMemberCreate
from app.schema.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
)
from app.schema.user import UserBasicResponse
from app.schema.business import BusinessBasicInfoResponse
from app.schema.file import FileInfo
from app.crud import (
    message as messageCRUD,
    message_attachment as message_attachmentCRUD,
    conversation_member as conversation_memberCRUD,
    conversation as conversationCRUD,
    account as accountCRUD,
)
from app.core.conversation.conversation_helper import conversation_helper
from app.core.message.message_helper import message_helper
from app.hepler.enum import WebsocketActionType, TypeAccount, CreateMessageType
from app.common.exception import CustomException
from app.core.websocket.websocket_helper import websocket_helper
from app.storage.cache.message_cache_service import message_cache_service


class WebsocketHandler:
    def __init__(self, websocket_manager: WebsocketManager):
        self.websocket_manager: WebsocketManager = websocket_manager
        self.websocket_manager.handler_register(
            WebsocketActionType.NEW_MESSAGE, self.new_message_handler
        )
        self.websocket_manager.handler_register(
            WebsocketActionType.USER_TYPING, self.user_typing_handler
        )

    async def new_message_handler(
        self,
        websocket: WebSocket,
        db: Session,
        redis: Redis,
        incoming_message: dict,
        current_user: Account,
    ):
        try:
            new_message_data: NewMessageSchema = NewMessageSchema(**incoming_message)
        except ValueError as e:
            print(e)
            await self.websocket_manager.send_error(
                websocket, "Invalid message format."
            )
            return

        conversation_id: int = new_message_data.conversation_id
        message_type: CreateMessageType = new_message_data.type
        is_new_conversation: bool = not conversation_id
        valid_attachment_list: List[FileInfo] = []

        if message_type == CreateMessageType.ATTACHMENT:
            valid_attachment_list = await conversation_helper.validate_attachments(
                redis,
                new_message_data.attachments,
                current_user.id,
                conversation_id,
            )
            if len(valid_attachment_list) == 0:
                await self.websocket_manager.send_error(
                    websocket, "Attachments is invalid."
                )
                return

        if is_new_conversation:
            if not new_message_data.members:
                await self.websocket_manager.send_error(
                    websocket, "Conversation id or members is required."
                )
                return

            member_ids: List[int] = conversation_helper.filter_member(
                new_message_data.members, current_user
            )

            outcoming_message, members = await websocket_helper.new_conversation(
                db, redis, websocket, current_user, member_ids, websocket_manager
            )
            user_id_to_websocket: dict = websocket_manager.user_id_to_websocket
            for member in members:
                websockets = user_id_to_websocket.get(member.id)
                if websockets:
                    for ws in websockets:
                        await websocket_manager.add_conversation(
                            outcoming_message.id, ws
                        )

            await websocket_helper.broadcast(
                websocket_manager, outcoming_message.id, outcoming_message
            )
            conversation_id = outcoming_message.id

        else:
            is_valid_conversation: bool = (
                await conversation_helper.is_join_conversation(
                    db, redis, conversation_id, current_user.id
                )
            )
            if not is_valid_conversation:
                await self.websocket_manager.send_error(
                    websocket,
                    f"Conversation {conversation_id} not found in your conversations.",
                )
                return

            if new_message_data.parent_id:
                is_valid_parent_message: bool = (
                    await message_helper.check_parent_message(
                        db, redis, new_message_data.parent_id, conversation_id
                    )
                )
                if not is_valid_parent_message:
                    await self.websocket_manager.send_error(
                        websocket,
                        f"Parent message {new_message_data.parent_id} not found in conversation {conversation_id}.",
                    )
                    return

        type = message_type
        outcoming_message: Union[ResponseMessageSchema, None] = None
        if type == CreateMessageType.TEXT:
            outcoming_message: ResponseMessageSchema = (
                await websocket_helper.create_text_message(
                    db, redis, current_user, conversation_id, new_message_data
                )
            )

            await websocket_helper.broadcast(
                websocket_manager, conversation_id, outcoming_message
            )

        elif type == CreateMessageType.ATTACHMENT:
            if new_message_data.content:
                outcoming_message: ResponseMessageSchema = (
                    await websocket_helper.create_text_message(
                        db, redis, current_user, conversation_id, new_message_data
                    )
                )
                await websocket_helper.broadcast(
                    websocket_manager, conversation_id, outcoming_message
                )

            outcoming_messages: List[ResponseMessageSchema] = (
                await websocket_helper.create_attachment_message(
                    db,
                    redis,
                    current_user,
                    conversation_id,
                    new_message_data,
                    valid_attachment_list,
                    is_new_conversation,
                )
            )

            for outcoming_message in outcoming_messages:
                await websocket_helper.broadcast(
                    websocket_manager, conversation_id, outcoming_message
                )

    async def user_typing_handler(
        self,
        websocket: WebSocket,
        db: Session,
        redis: Redis,
        incoming_message: dict,
        current_user: Account,
    ):
        user_typing_data: UserTypingSchema = UserTypingSchema(**incoming_message)
        conversation_id: int = user_typing_data.conversation_id

        is_join_conversation = await conversation_helper.is_join_conversation(
            db, redis, conversation_id, current_user.id
        )

        if not is_join_conversation:
            await self.websocket_manager.send_error(
                websocket,
                f"Conversation {conversation_id} not found in your conversations.",
            )
            return

        await websocket_helper.broadcast(
            websocket_manager, conversation_id, user_typing_data
        )

    async def add_user_to_conversation_handler(
        self,
        websocket: WebSocket,
        db: Session,
        redis: Redis,
        incoming_message: dict,
        current_user: Account,
    ):
        pass

    async def remove_user_from_conversation_handler(
        self,
        websocket: WebSocket,
        db: Session,
        redis: Redis,
        incoming_message: dict,
        current_user: Account,
    ):
        pass

    async def update_conversation_handler(
        self,
        websocket: WebSocket,
        db: Session,
        redis: Redis,
        incoming_message: dict,
        current_user: Account,
    ):
        pass

    async def reaction_message_handler(
        self,
        websocket: WebSocket,
        db: Session,
        redis: Redis,
        incoming_message: dict,
        current_user: Account,
    ):
        pass


websocket_manager = WebsocketManager()
websocket_handler = WebsocketHandler(websocket_manager)
