from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.hepler.enum import AttachmentType


class MessageAttachment(Base):
    message_id = Column(
        Integer,
        ForeignKey("message.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    url = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(Enum(AttachmentType), nullable=False)
    size = Column(Integer, nullable=False)
    position = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    message = relationship("Message", back_populates="attachments")
