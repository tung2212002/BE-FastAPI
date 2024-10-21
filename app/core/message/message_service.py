from redis.asyncio import Redis
from sqlalchemy.orm import Session
from typing import List
from fastapi import status

from app.model import (
    Account,
    Conversation,
    Message,
    MessageImage,
    MessageReaction,
    PinnedMessage,
)
from app.crud import (
    conversation as conversationCRUD,
    contact as contactCRUD,
    message as messageCRUD,
    message_reaction as message_reactionCRUD,
    message_image as message_imageCRUD,
    pinned_message as pinned_messageCRUD,
    account as accountCRUD,
)
from app.hepler.enum import TypeAccount
from app.schema.business import BusinessBasicInfoResponse
from app.schema.account import AccountBasicResponse
from app.schema.conversation import ConversationResponse
from app.schema.message import MessageResponse, GetMessagesRequest, Attachment
from app.schema.message_reaction import MessageReactionResponse
from app.schema.message_image import MessageImageResponse, AttachmentResponse
from app.core.business.business_helper import business_helper
from app.core.user.user_helper import user_helper
from app.core.conversation.conversation_helper import conversation_helper
from app.common.exception import CustomException
from app.common.response import CustomResponse
from app.hepler.enum import ConversationType, MessageType


class MessageService:
    async def get(self, db: Session, redis: Redis, data: dict, current_user: Account):
        page = GetMessagesRequest(**data)

        if not conversationCRUD.get_by_account_id_and_conversation_id(
            db, account_id=current_user.id, conversation_id=page.conversation_id
        ):
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN, msg="Not allowed to access"
            )

        messages: List[Message] = messageCRUD.get_by_conversation_id(
            db, **page.model_dump()
        )

        response = []
        for message in messages:
            parent_message: Message = None
            images: List[MessageImage] = []
            reaction: MessageReaction = (
                message_reactionCRUD.get_by_account_id_and_message_id(
                    db, account_id=current_user.id, message_id=message.id
                )
            )
            user: AccountBasicResponse = conversation_helper.get_user_response(
                db, message.account
            )

            if message.parent_id:
                parent_message = messageCRUD.get(db, message.parent_id)

            if message.type == MessageType.IMAGE:
                images = message_imageCRUD.get_by_message_id(db, message_id=message.id)

            response.append(
                MessageResponse(
                    **message.__dict__,
                    user=user,
                    parent=parent_message.__dict__ if parent_message else None,
                    attachments=[
                        MessageImageResponse(**image.__dict__) for image in images
                    ],
                    reaction=(
                        MessageReactionResponse(**reaction.__dict__)
                        if reaction
                        else None
                    ),
                )
            )

        return CustomResponse(data=response)


message_service = MessageService()
