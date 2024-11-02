from sqlalchemy.orm import Session
from typing import List, Union
from fastapi import status
from redis.asyncio import Redis

from app.model import (
    Account,
    Conversation,
    ConversationMember,
    Message,
    Manager,
    Business,
    Company,
)
from app.crud import (
    conversation as conversationCRUD,
    conversation_member as conversation_memberCRUD,
    account as accountCRUD,
    contact as contactCRUD,
    message as messageCRUD,
)
from app.schema.conversation import (
    ConversationCreate,
    ConversationResponse,
)
from app.schema.company import CompanyItemGeneralResponse
from app.schema.account import AccountBasicResponse
from app.schema.conversation_member import ConversationMemberCreate
from app.schema.message import MessageBasicResponse
from app.schema.file import FileInfo
from app.common.exception import CustomException
from app.core.company.company_helper import company_helper
from app.hepler.enum import ConversationType, TypeAccount, Role
from app.storage.cache.message_cache_service import message_cache_service
from app.storage.cache.file_url_cache_service import file_url_cache_service


class ConversationHelper:
    def get_member_response(
        self,
        db: Session,
        conversation_member: ConversationMember,
        current_user: Account = None,
    ) -> AccountBasicResponse:
        account: Account = conversation_member.account
        if account.role == Role.BUSINESS:
            manager: Manager = account.manager
            business: Business = manager.business
            company: Company = business.company
            company_response: CompanyItemGeneralResponse = (
                company_helper.get_info_general(company)
            )
            return AccountBasicResponse(
                **account.__dict__,
                nickname=conversation_member.nickname,
                company=company_response,
                email=account.manager.email,
            )
        return AccountBasicResponse(
            **account.__dict__,
            nickname=conversation_member.nickname,
            email=account.user.email,
        )

    def get_private_conversation_response(
        self, db: Session, conversation: Conversation, current_user: Account
    ) -> ConversationResponse:
        member = [
            self.get_member_response(db, conversation_member, current_user)
            for conversation_member in conversation.conversation_member_secondary
            if conversation_member.account_id != current_user.id
        ]

        return ConversationResponse(
            **conversation.__dict__,
            members=member,
            last_message=MessageBasicResponse(
                **self.get_last_message(db, conversation.id).__dict__
            ),
        )

    def get_group_conversation_response(
        self, db: Session, conversation: Conversation, limit: int = 5
    ) -> ConversationResponse:
        conversation_members: List[ConversationMember] = (
            conversation_memberCRUD.get_by_conversation_id(
                db, conversation_id=conversation.id, limit=limit
            )
        )
        members = [
            self.get_member_response(db, conversation_member)
            for conversation_member in conversation_members
        ]
        return ConversationResponse(
            **conversation.__dict__,
            members=members,
            last_message=MessageBasicResponse(
                **self.get_last_message(db, conversation.id).__dict__
            ),
        )

    def filter_member(self, members: List[int], current_user: Account) -> List[int]:
        members = [member for member in members if member != current_user.id]
        if len(members) == 0:
            raise CustomException(status_code=404, msg="Members not found")
        return members

    def get_conversation_by_account_and_id(
        self, db: Session, account_id: int, conversation_id: int
    ) -> Conversation:
        conversation = conversationCRUD.get_by_account_id_and_conversation_id(
            db, account_id=account_id, conversation_id=conversation_id
        )
        if not conversation:
            raise CustomException(status_code=404, msg="Conversation not found")
        return conversation

    def create_private_conversation(
        self, db: Session, member: Account, current_user: Account
    ) -> ConversationResponse:
        if conversationCRUD.get_private_conversation(db, current_user.id, member.id):
            raise CustomException(msg="Conversation already exists")

        new_conversation = self.create_conversation(
            db,
            current_user,
            ConversationCreate(
                type=ConversationType.PRIVATE,
                account_id=current_user.id,
                count_member=2,
            ),
        )

        self.create_conversation_members(
            db, new_conversation.id, [member.id, current_user.id]
        )

        members = [
            self.get_user_response(db, member),
            self.get_user_response(db, current_user),
        ]
        return ConversationResponse(**new_conversation.__dict__, members=members)

    def create_group_conversation(
        self, db: Session, members: List[Account], current_user: Account
    ) -> ConversationResponse:
        all_members = members + [current_user]
        member_ids = [member.id for member in all_members]

        if conversation_memberCRUD.get_by_account_ids(db, member_ids):
            raise CustomException(msg="Conversation already exists")

        members_response: List[AccountBasicResponse] = [
            self.get_user_response(db, member) for member in all_members
        ]

        new_conversation: Conversation = self.create_conversation(
            db,
            current_user,
            ConversationCreate(
                type=ConversationType.GROUP,
                account_id=current_user.id,
                count_member=len(all_members),
                name=self.generate_conversation_name(all_members),
            ),
        )

        self.create_conversation_members(db, new_conversation.id, member_ids)

        return ConversationResponse(
            **new_conversation.__dict__, members=members_response
        )

    def generate_conversation_name(self, members: List[Account]) -> str:
        default_name = ", ".join([member.full_name for member in members])
        name = default_name if len(default_name) <= 50 else default_name[:47] + "..."
        return name

    def create_conversation_members(
        self, db: Session, conversation_id: int, members: List[int]
    ) -> None:
        for member in members:
            conversation_member = ConversationMemberCreate(
                conversation_id=conversation_id,
                account_id=member,
            )
            conversation_memberCRUD.create(db, obj_in=conversation_member)

    def create_conversation(
        self, db: Session, current_user: Account, conversation_data: ConversationCreate
    ) -> Conversation:
        return conversationCRUD.create(db, obj_in=conversation_data)

    def get_user_response(
        self,
        db: Session,
        account: Account,
    ) -> AccountBasicResponse:
        email: str = (
            account.user.email
            if account.type_account == TypeAccount.NORMAL
            else account.manager.email
        )
        return AccountBasicResponse(
            **account.__dict__,
            email=email,
        )

    def get_user_basic_response(
        self,
        db: Session,
        account: Account,
    ) -> AccountBasicResponse:
        if account.role == Role.BUSINESS:
            manager: Manager = account.manager
            business: Business = manager.business
            company: Company = business.company
            company_response: CompanyItemGeneralResponse = (
                company_helper.get_info_general(company)
            )
            return AccountBasicResponse(
                **account.__dict__,
                company=company_response,
                email=account.manager.email,
            )
        return AccountBasicResponse(**account.__dict__, email=account.user.email)

    def check_business_valid_contact(
        self, db: Session, members: List[Account], current_user: Account
    ) -> None:
        member_ids = [member.id for member in members]
        if not contactCRUD.check_business_can_contact(db, member_ids, current_user):
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN,
                msg="Business can not contact with user",
            )

    def check_valid_contact(
        self, db: Session, other_user: Account, current_user: Account
    ) -> None:
        other_user_type = other_user.type_account
        current_user_type = current_user.type_account

        if not (
            (
                other_user_type == TypeAccount.BUSINESS
                and current_user_type == TypeAccount.NORMAL
            )
            or (
                other_user_type == TypeAccount.NORMAL
                and current_user_type == TypeAccount.BUSINESS
            )
        ):
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN,
                msg="Only contact with relationship job",
            )

        candidate_id = (
            other_user.id if other_user_type == TypeAccount.NORMAL else current_user.id
        )
        business_id = (
            current_user.id
            if current_user_type == TypeAccount.BUSINESS
            else other_user.id
        )

        if not contactCRUD.check_can_contact(
            db, candidate_id=candidate_id, business_id=business_id
        ):
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN,
                msg="Only contact with relationship job",
            )

    async def is_join_conversation(
        self, db: Session, redis: Redis, conversation_id: int, account_id: int
    ) -> bool:
        is_exist: bool = None
        try:
            is_exist = await message_cache_service.exists_conversation_id_in_list(
                redis, user_id=account_id, conversation_id=conversation_id
            )
        except Exception as e:
            print(e)

        if is_exist is None:
            is_exist = (
                conversationCRUD.get_by_account_id_and_conversation_id(
                    db, account_id=account_id, conversation_id=conversation_id
                )
                is not None
            )

        return is_exist

    def get_last_message(self, db: Session, conversation_id: int) -> Message:
        message: Message = messageCRUD.get_last_message(
            db, conversation_id=conversation_id
        )
        user: Account = accountCRUD.get(db, message.account_id)
        conversation_member: ConversationMember = (
            conversation_memberCRUD.get_by_account_id_and_conversation_id(
                db, account_id=user.id, conversation_id=conversation_id
            )
        )
        return MessageBasicResponse(
            **message.__dict__,
            user=self.get_member_response(db, conversation_member, user),
        )

    async def validate_attachments(
        self,
        redis: Redis,
        attachments: List[str],
        current_user_id: int,
        conversation_id: int,
    ) -> List[FileInfo]:
        valid_attachment_list: List[FileInfo] = []
        for attachment in attachments:
            file_info: FileInfo = (
                await file_url_cache_service.get_cache_file_url_message(
                    redis,
                    name=attachment,
                    user_id=current_user_id,
                    conversation_id=conversation_id,
                )
            )
            if file_info:
                valid_attachment_list.append(file_info)

        return valid_attachment_list


conversation_helper = ConversationHelper()
