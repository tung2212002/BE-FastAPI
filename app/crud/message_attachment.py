from sqlalchemy.orm import Session

from .base import CRUDBase
from app.model import MessageAttachment
from app.schema.message_attachment import MessageAttachmentCreate


class CRUDMessageAttachment:
    def get(self, db: Session, id: int) -> MessageAttachment:
        return db.query(MessageAttachment).filter(MessageAttachment.id == id).first()

    def get_by_message_id(self, db: Session, message_id: int) -> MessageAttachment:
        return (
            db.query(MessageAttachment)
            .filter(MessageAttachment.message_id == message_id)
            .all()
        )

    def create(self, db: Session, obj_in: MessageAttachmentCreate) -> MessageAttachment:
        db_obj = MessageAttachment(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int) -> None:
        db.query(MessageAttachment).filter(MessageAttachment.id == id).delete()
        db.commit()


message_attachment = CRUDMessageAttachment()
