from sqlalchemy.orm import Session, aliased
from sqlalchemy.sql import func
from sqlalchemy import case
from typing import List

from .base import CRUDBase
from app.model import ConversationMember, Account, Message
from app.schema.conversation_member import (
    ConversationMemberCreate,
    ConversationMemberUpdate,
)
from app.hepler.enum import MemberType


class CRUDConversationMember(
    CRUDBase[ConversationMember, ConversationMemberCreate, ConversationMemberUpdate]
):
    def get_by_account_ids(self, db: Session, account_ids: list[int]) -> int:
        num_users = len(account_ids)
        # SELECT cm.conversation_id
        # FROM ConversationMember cm
        # WHERE cm.account_id IN (:account_ids)
        # GROUP BY cm.conversation_id
        # HAVING COUNT(DISTINCT cm.account_id) = :num_users
        #    AND (SELECT COUNT(*)
        #         FROM ConversationMember sub_cm
        #         WHERE sub_cm.conversation_id = cm.conversation_id) = :num_users
        # LIMIT 1;
        cm_subquery = aliased(ConversationMember)

        subquery = (
            db.query(func.count(cm_subquery.account_id))
            .filter(cm_subquery.conversation_id == ConversationMember.conversation_id)
            .scalar_subquery()
        )

        query = (
            db.query(ConversationMember.conversation_id)
            .filter(ConversationMember.account_id.in_(account_ids))
            .group_by(ConversationMember.conversation_id)
            .having(
                func.count(func.distinct(ConversationMember.account_id)) == num_users
            )
            .having(subquery == num_users)
            .limit(1)
        )

        return query.scalar()

    def get_member_by_conversation_id(
        self,
        db: Session,
        *,
        conversation_id: int,
        limit: int = 10,
        skip: int = 0
        # ) -> ConversationMember:
        #     role_priority = case(
        #         [
        #             (ConversationMember.type == MemberType.ADMIN, 1),
        #             (ConversationMember.type == MemberType.MEMBER, 2),
        #         ],
        #         else_=3,
        #     )
        #     return (
        #         db.query(ConversationMember)
        #         .filter_by(conversation_id=conversation_id)
        #         .order_by(role_priority)
        #         .limit(limit)
        #         .offset(skip)
        #         .all()
        #     )
    ) -> List[Account]:
        role_priority = case(
            (ConversationMember.type == MemberType.ADMIN, 1),
            (ConversationMember.type == MemberType.MEMBER, 2),
            else_=3,
        )
        return (
            db.query(Account)
            .join(
                ConversationMember,
                ConversationMember.account_id == Account.id,
            )
            .filter(ConversationMember.conversation_id == conversation_id)
            .order_by(role_priority)
            .limit(limit)
            .offset(skip)
            .all()
        )

    def get_by_conversation_id(
        self, db: Session, *, conversation_id: int, limit: int = 10, skip: int = 0
    ) -> ConversationMember:
        role_priority = case(
            (ConversationMember.type == MemberType.ADMIN, 1),
            (ConversationMember.type == MemberType.MEMBER, 2),
            else_=3,
        )
        return (
            db.query(ConversationMember)
            .filter_by(conversation_id=conversation_id)
            .order_by(role_priority)
            .limit(limit)
            .offset(skip)
            .all()
        )

    def get_by_account_id_and_conversation_id(
        self, db: Session, *, account_id: int, conversation_id: int
    ) -> ConversationMember:
        return (
            db.query(ConversationMember)
            .filter_by(account_id=account_id, conversation_id=conversation_id)
            .first()
        )


conversation_member = CRUDConversationMember(ConversationMember)
