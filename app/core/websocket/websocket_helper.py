from fastapi import WebSocket
from sqlalchemy.orm import Session
from redis.asyncio import Redis
from typing import Any, Dict, List, Tuple
from fastapi import status

from app.core.websocket.websocket_manager import WebsocketManager
from app.model import Account
from app.core.conversation.conversation_helper import conversation_helper
from app.common.exception import CustomException
from app.crud import (
    account as accountCRUD,
    message as messageCRUD,
    conversation as conversationCRUD,
    conversation_member as conversation_memberCRUD,
)
from app.schema.conversation import ConversationResponse
from app.hepler.enum import TypeAccount
from app.schema.message import MessageCreate
from app.schema.websocket import NewMessageSchema, ResponseMessageSchema
from app.schema.account import AccountBasicResponse
from app.storage.cache.message_cache_service import message_cache_service


class WebsocketHelper:
    async def new_conversation(
        self,
        db: Session,
        redis: Redis,
        websocket: WebSocket,
        current_user: Account,
        member_ids: List[int],
        websocket_manager: WebsocketManager,
    ) -> Tuple[ConversationResponse, List[Account]]:
        response_conversation: ConversationResponse = None
        members: List[Account] = []

        if len(member_ids) == 1:
            response_conversation, members = await self.create_private_conversation(
                db, websocket, redis, current_user, member_ids, websocket_manager
            )
        else:
            response_conversation, members = await self.create_group_conversation(
                db, websocket, redis, current_user, member_ids, websocket_manager
            )
        try:
            for member in members:
                await message_cache_service.add_conversation_id_to_list(
                    redis, user_id=member.id, conversation_id=response_conversation.id
                )
                pass
        except Exception as e:
            print(e)

        return response_conversation, members

    async def create_private_conversation(
        self,
        db: Session,
        websocket: WebSocket,
        redis: Redis,
        current_user: Account,
        member_ids: List[int],
        websocket_manager: WebsocketManager,
    ) -> Tuple[ConversationResponse, List[Account]]:
        try:
            member = accountCRUD.get(db, member_ids[0])
            if not member:
                await websocket_manager.send_error(
                    websocket, f"Member {member_ids[0]} not found."
                )
            conversation_helper.check_valid_contact(db, member, current_user)
            if conversation_memberCRUD.get_by_account_ids(
                db, [current_user.id, member.id]
            ):
                raise CustomException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    msg="Already connected to member.",
                )
        except CustomException as e:
            await websocket_manager.send_error(websocket, "Cannot connect to members.")
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST,
                msg="Cannot connect to members.",
            )

        return conversation_helper.create_private_conversation(
            db, current_user, member
        ), [member, current_user]

    async def create_group_conversation(
        self,
        db: Session,
        websocket: WebSocket,
        redis: Redis,
        current_user: Account,
        member_ids: List[int],
        websocket_manager: WebsocketManager,
    ) -> Tuple[ConversationResponse, List[Account]]:
        if current_user.type_account != TypeAccount.BUSINESS:
            await websocket_manager.send_error(
                websocket,
                "Only business account can create group conversation",
            )
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST,
                msg="Only business account can create group conversation",
            )
        members: List[Account] = []
        for member_id in member_ids:
            member = accountCRUD.get(db, member_id)
            if not member:
                await websocket_manager.send_error(
                    websocket, f"Member {member_id} not found."
                )
                raise CustomException(
                    status_code=status.HTTP_404_NOT_FOUND, msg="Member not found"
                )

            members.append(member)

        conversation_helper.check_business_valid_contact(db, members, current_user)
        if conversation_memberCRUD.get_by_account_ids(
            db, [current_user.id] + member_ids
        ):
            await websocket_manager.send_error(
                websocket, "Already connected to members."
            )
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST,
                msg="Already connected to members.",
            )
        return conversation_helper.create_group_conversation(
            db, members, current_user
        ), members + [current_user]

    async def create_text_message(
        self,
        db: Session,
        redis: Redis,
        current_user: Account,
        conversation_id: int,
        message_data: NewMessageSchema,
    ) -> ResponseMessageSchema:
        if not message_data.parent_id:
            content: str = message_data.content
            message = MessageCreate(
                conversation_id=conversation_id,
                account_id=current_user.id,
                content=content,
            )
            if message_data.attachments:
                pass

            message = messageCRUD.create(db, obj_in=message)
            user: AccountBasicResponse = conversation_helper.get_user_basic_response(
                db, current_user
            )
            outcoming_message = ResponseMessageSchema(
                id=message.id,
                conversation_id=message.conversation_id,
                account_id=message.account_id,
                content=message.content,
                created_at=message.created_at,
                user=user,
            )

            return outcoming_message

    async def create_attachment_message(
        self,
        db: Session,
        redis: Redis,
        current_user: Account,
        conversation_id: int,
        message_data: NewMessageSchema,
    ) -> ResponseMessageSchema:
        if not message_data.parent_id:
            content: str = message_data.content
            message = MessageCreate(
                conversation_id=conversation_id,
                account_id=current_user.id,
                content=content,
            )
            if message_data.attachments:
                pass

            message = messageCRUD.create(db, obj_in=message)
            user: AccountBasicResponse = conversation_helper.get_user_basic_response(
                db, current_user
            )
            outcoming_message = ResponseMessageSchema(
                id=message.id,
                conversation_id=message.conversation_id,
                account_id=message.account_id,
                content=message.content,
                created_at=message.created_at,
                user=user,
            )

            return outcoming_message


websocket_helper = WebsocketHelper()
