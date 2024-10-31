from redis.asyncio import Redis
from sqlalchemy.orm import Session
from typing import List
from fastapi import status
from datetime import datetime

from app.crud import (
    conversation as conversationCRUD,
    account as accountCRUD,
    conversation_member as conversation_memberCRUD,
)
from app.schema.page import Pagination
from app.schema.conversation import (
    ConversationCreateRequest,
    ConversationResponse,
    ConversationUpdate,
    ConversationUpdateRequest,
    ConversationUpdateAvatarRequest,
    ConversationGetExistWithListMemberRequest,
)
from app.schema.websocket import (
    NewConversationSchema,
    UpdateAvatarConversationSchema,
)
from app.schema.message_image import AttachmentCreateRequest, AttachmentResponse
from app.common.exception import CustomException
from app.common.response import CustomResponse
from app.model import Account, Conversation, ConversationMember
from app.core.conversation.conversation_helper import conversation_helper
from app.hepler.enum import ConversationType, TypeAccount
from app.storage.s3 import s3_service
from app.core.websocket.websocket_handler import websocket_manager
from app.storage.cache.file_url_cache_service import file_url_cache_service


class ConversationService:
    async def get(self, db: Session, redis: Redis, data: dict, current_user: Account):
        page: Pagination = Pagination(**data)
        # conversations: List[Conversation] = conversationCRUD.get_by_account_id(
        #     db, account_id=current_user.id, **page.model_dump()
        # )

        # response = []
        # for conversation in conversations:
        #     if conversation.type == ConversationType.PRIVATE:
        #         response.append(
        #             conversation_helper.get_private_conversation_response(
        #                 db, conversation, current_user
        #             )
        #         )
        #     else:
        #         response.append(
        #             conversation_helper.get_group_conversation_response(
        #                 db, conversation
        #             )
        #         )

        # return CustomResponse(data=response)
        conversations: List[Conversation] = conversationCRUD.get_by_lastest_message(
            db, account_id=current_user.id, **page.model_dump()
        )

        response = []
        for conversation in conversations:
            if conversation.type == ConversationType.PRIVATE:
                response.append(
                    conversation_helper.get_private_conversation_response(
                        db, conversation, current_user
                    )
                )
            else:
                response.append(
                    conversation_helper.get_group_conversation_response(
                        db, conversation
                    )
                )

        return CustomResponse(data=response)

    async def get_existing_conversation(
        self, db: Session, redis: Redis, data: dict, current_user: Account
    ):
        conversation_data = ConversationGetExistWithListMemberRequest(**data)

        member_ids: List[int] = conversation_helper.filter_member(
            conversation_data.members, current_user
        )
        conversation_id: int = conversation_memberCRUD.get_by_account_ids(
            db, [current_user.id] + member_ids
        )

        if not conversation_id:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Conversation not found"
            )

        conversation: Conversation = conversationCRUD.get(db, conversation_id)

        if conversation.type == ConversationType.PRIVATE:
            response = conversation_helper.get_private_conversation_response(
                db, conversation, current_user
            )
        else:
            response = conversation_helper.get_group_conversation_response(
                db, conversation
            )

        return CustomResponse(data=response)

    async def create(
        self, db: Session, redis: Redis, data: dict, current_user: Account
    ):
        conversation_data = ConversationCreateRequest(**data)

        member_ids: List[int] = conversation_helper.filter_member(
            conversation_data.members, current_user
        )
        members: List[Account] = []
        response: ConversationResponse = None

        if len(member_ids) == 1:
            member: Account = accountCRUD.get(db, member_ids[0])
            if not member:
                raise CustomException(
                    status_code=status.HTTP_404_NOT_FOUND, msg="Member not found"
                )
            conversation_helper.check_valid_contact(db, member, current_user)
            response = conversation_helper.create_private_conversation(
                db, current_user, member
            )
            members.append(member)
        else:
            if current_user.type_account != TypeAccount.BUSINESS:
                raise CustomException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    msg="Only business account can create group conversation",
                )
            for member_id in member_ids:
                member = accountCRUD.get(db, member_id)
                if not member:
                    raise CustomException(
                        status_code=status.HTTP_404_NOT_FOUND, msg="Member not found"
                    )
                members.append(member)

            conversation_helper.check_business_valid_contact(db, members, current_user)
            response = conversation_helper.create_group_conversation(
                db, members, current_user
            )

        user_id_to_websocket: dict = websocket_manager.user_id_to_websocket
        for member_id in members + [current_user]:
            websockets = user_id_to_websocket.get(member_id.id)
            if websockets:
                for websocket in websockets:
                    await websocket_manager.add_conversation(response.id, websocket)

        incoming_message: NewConversationSchema = NewConversationSchema(
            id=response.id,
            name=response.name,
            avatar=response.avatar,
            members=response.members,
            created_at=response.created_at,
            conversation_type=response.type,
        )

        await websocket_manager.broadcast(
            response.id, incoming_message.model_dump_json()
        )
        return CustomResponse(status_code=status.HTTP_201_CREATED, data=response)

    async def update(
        self, db: Session, redis: Redis, data: dict, current_user: Account
    ):
        conversation_data: ConversationUpdateRequest = ConversationUpdateRequest(**data)
        conversation: Conversation = (
            conversation_helper.get_conversation_by_account_and_id(
                db, current_user, conversation_data.id
            )
        )

        obj_in = ConversationUpdate(**conversation_data.model_dump())
        conversation = conversationCRUD.update(db, db_obj=conversation, obj_in=obj_in)

        incoming_message = UpdateAvatarConversationSchema(
            id=conversation.id,
            name=conversation.name,
            updated_at=conversation.updated_at,
        )

        await websocket_manager.broadcast(
            conversation.id, incoming_message.model_dump_json()
        )

        return CustomResponse(data=ConversationResponse(**conversation.__dict__))

    async def update_avatar(
        self, db: Session, redis: Redis, data: dict, current_user: Account
    ):
        conversation_data: ConversationUpdateAvatarRequest = (
            ConversationUpdateAvatarRequest(**data)
        )
        conversation: Conversation = (
            conversationCRUD.get_by_account_id_and_conversation_id(
                db, account_id=current_user.id, conversation_id=conversation_data.id
            )
        )
        if not conversation:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Conversation not found"
            )

        avatar = conversation_data.avatar
        key = avatar.filename
        s3_service.upload_file(avatar, key)
        conversation_data.avatar = key

        obj_in = ConversationUpdate(**conversation_data.model_dump())
        conversation = conversationCRUD.update(db, db_obj=conversation, obj_in=obj_in)

        incoming_message = UpdateAvatarConversationSchema(
            id=conversation.id,
            avatar=conversation.avatar,
            updated_at=conversation.updated_at,
        )

        await websocket_manager.broadcast(
            conversation.id,
            incoming_message.model_dump_json(),
        )

        return CustomResponse(data=ConversationResponse(**conversation.__dict__))

    async def upload_attachment(
        self, db: Session, redis: Redis, data: dict, current_user: Account
    ):
        attach_file_data = AttachmentCreateRequest(**data)

        conversation: Conversation = (
            conversationCRUD.get_by_account_id_and_conversation_id(
                db,
                account_id=current_user.id,
                conversation_id=attach_file_data.conversation_id,
            )
        )

        if not conversation:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Conversation not found"
            )

        files = attach_file_data.files
        file = files[0]
        key = file.filename
        s3_service.upload_file(file, key)
        try:
            await file_url_cache_service.cache_file_url_message(
                redis,
                user_id=current_user.id,
                conversation_id=conversation.id,
                upload_filename=key,
            )
        except Exception as e:
            print(e)

        return CustomResponse(data=AttachmentResponse(upload_filename=key, url=key))


conversation_service = ConversationService()
