from fastapi import WebSocket
from sqlalchemy.orm import Session
from redis.asyncio import Redis
from typing import Any, Dict, List, Tuple
from fastapi import status
from pydantic import BaseModel

from app.model import Account, MessageAttachment, Message
from app.crud import (
    account as accountCRUD,
    message as messageCRUD,
    conversation as conversationCRUD,
    conversation_member as conversation_memberCRUD,
    message_attachment as message_attachmentCRUD,
)
from app.core.websocket.websocket_manager import WebsocketManager
from app.core.conversation.conversation_helper import conversation_helper
from app.core.file.file_helper import file_helper
from app.core.message.message_helper import message_helper
from app.schema.conversation import ConversationResponse
from app.schema.message import MessageCreate
from app.schema.message_attachment import MessageAttachmentCreate
from app.schema.websocket import (
    NewMessageSchema,
    ResponseMessageSchema,
    AttachmentResponse,
)
from app.schema.websocket import NewConversationSchema
from app.schema.file import FileInfo
from app.schema.account import AccountBasicResponse
from app.storage.cache.message_cache_service import message_cache_service
from app.storage.cache.file_url_cache_service import file_url_cache_service
from app.common.exception import CustomException
from app.hepler.enum import TypeAccount, MessageType, WebsocketActionType, FolderBucket


class WebsocketHelper:
    async def new_conversation(
        self,
        db: Session,
        redis: Redis,
        websocket: WebSocket,
        current_user: Account,
        member_ids: List[int],
        websocket_manager: WebsocketManager,
    ) -> Tuple[NewConversationSchema, List[Account]]:
        response_conversation: NewConversationSchema = None
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

        return (
            NewConversationSchema(
                **{
                    k: v
                    for k, v in response_conversation.__dict__.items()
                    if k not in ["type", "members"]
                },
                conversation_type=response_conversation.type,
                members=[
                    conversation_helper.get_user_basic_response(db, member)
                    for member in members
                ],
            ),
            members,
        )

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
            member: Account = accountCRUD.get(db, member_ids[0])
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
        user: AccountBasicResponse = conversation_helper.get_user_basic_response(
            db, current_user
        )

        outcoming_message: ResponseMessageSchema = self.create_message(
            db,
            current_user.id,
            conversation_id,
            message_data,
            [],
            user,
            MessageType.TEXT,
        )

        return outcoming_message

    async def create_attachment_message(
        self,
        db: Session,
        redis: Redis,
        current_user: Account,
        conversation_id: int,
        message_data: NewMessageSchema,
        attachments: List[FileInfo],
        is_new_conversation: bool,
    ) -> List[ResponseMessageSchema]:
        response: List[ResponseMessageSchema] = []
        user: AccountBasicResponse = conversation_helper.get_user_basic_response(
            db, current_user
        )

        attachment_images: List[FileInfo] = file_helper.filter_images(attachments)
        attachment_files: List[FileInfo] = [
            attachment
            for attachment in attachments
            if attachment not in attachment_images
        ]

        if attachment_images:
            outcoming_message = self.create_message(
                db,
                current_user.id,
                conversation_id,
                message_data,
                attachment_images,
                user,
                MessageType.IMAGE,
            )

            response.append(outcoming_message)

        if attachment_files:
            for attachment in attachment_files:
                outcoming_message: ResponseMessageSchema = self.create_message(
                    db,
                    current_user.id,
                    conversation_id,
                    message_data,
                    [attachment],
                    user,
                    MessageType.FILE,
                )

                response.append(outcoming_message)

        await file_url_cache_service.delete_cache_file_url_message(
            redis,
            names=[attachment.name for attachment in attachments],
            user_id=current_user.id,
            conversation_id=0 if is_new_conversation else conversation_id,
        )

        return response

    def create_message(
        self,
        db: Session,
        account_id: int,
        conversation_id: int,
        new_message_data: NewMessageSchema,
        attachments: List[FileInfo],
        user: AccountBasicResponse,
        type: MessageType,
    ) -> ResponseMessageSchema:
        attachment_response: List[AttachmentResponse] = []

        message = MessageCreate(
            conversation_id=conversation_id,
            account_id=account_id,
            type=type,
            content=new_message_data.content,
            parent_id=new_message_data.parent_id,
        )

        message: Message = messageCRUD.create(db, obj_in=message)

        for index, attachment in enumerate(attachments):
            message_attachment = MessageAttachmentCreate(
                **attachment.model_dump(),
                position=index,
                message_id=message.id,
            )

            message_attachment: MessageAttachment = message_attachmentCRUD.create(
                db, obj_in=message_attachment
            )

            attachment_response.append(
                AttachmentResponse(**message_attachment.__dict__)
            )

        return ResponseMessageSchema(
            **{k: v for k, v in message.__dict__.items() if k != "type"},
            user=user,
            attachments=attachment_response,
            type=WebsocketActionType.NEW_MESSAGE,
            message_type=type,
        )

    async def broadcast(
        self,
        websocket_manager: WebsocketManager,
        conversation_id: int,
        outcoming_message: BaseModel,
    ) -> None:
        await websocket_manager.broadcast(
            conversation_id, outcoming_message.model_dump_json()
        )


websocket_helper = WebsocketHelper()
