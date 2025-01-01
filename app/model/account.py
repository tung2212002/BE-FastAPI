from sqlalchemy import Column, Enum, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.hepler.enum import Role, TypeAccount


class Account(Base):
    full_name = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    avatar = Column(String(255), nullable=True)
    role = Column(Enum(Role), default=Role.USER)
    type_account = Column(Enum(TypeAccount), default=TypeAccount.NORMAL)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    last_login = Column(DateTime(timezone=True), default=func.now())

    manager = relationship(
        "Manager",
        back_populates="account",
        lazy=True,
        uselist=False,
        passive_deletes=True,
    )
    user = relationship(
        "User",
        back_populates="account",
        lazy=True,
        uselist=False,
        passive_deletes=True,
    )
    conversation_member_secondary = relationship(
        "ConversationMember",
        back_populates="account",
    )
    messages = relationship(
        "Message", back_populates="account", lazy=True, passive_deletes=True
    )