from sqlalchemy import Column, Integer, Enum, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.hepler.enum import ConversationType


class Conversation(Base):
    account_id = Column(
        Integer,
        ForeignKey("account.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(
        Enum(ConversationType),
        nullable=False,
        default=ConversationType.PRIVATE,
        index=True,
    )
    name = Column(String(50), nullable=True)
    is_renamed = Column(Integer, default=0, nullable=False)
    avatar = Column(String(255), nullable=True)
    count_member = Column(Integer, default=2, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    messages = relationship(
        "Message", back_populates="conversation", lazy=True, passive_deletes=True
    )
    conversation_member_secondary = relationship(
        "ConversationMember",
        back_populates="conversation",
        lazy=True,
        passive_deletes=True,
    )
