from sqlalchemy import Column, Integer, Enum, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.hepler.enum import MessageType


class Message(Base):
    conversation_id = Column(
        Integer,
        ForeignKey("conversation.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id = Column(
        Integer,
        ForeignKey("account.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    type = Column(
        Enum(MessageType), nullable=False, default=MessageType.TEXT, index=True
    )
    content = Column(String(255), nullable=False)
    is_pinned = Column(Integer, default=0, nullable=False)
    parent_id = Column(Integer, ForeignKey("message.id"), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    like_count = Column(Integer, default=0, nullable=False)
    dislike_count = Column(Integer, default=0, nullable=False)

    conversation = relationship("Conversation", back_populates="messages")
    account = relationship("Account", back_populates="messages")
    parent = relationship(
        "Message", back_populates="childrens", remote_side="Message.id"
    )
    childrens = relationship("Message", back_populates="parent", passive_deletes=True)
    reactions = relationship("MessageReaction", back_populates="message")
    images = relationship("MessageImage", back_populates="message")
    pinned_message = relationship(
        "PinnedMessage", back_populates="message", uselist=False
    )
