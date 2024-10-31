from sqlalchemy.orm import Session

from .base import CRUDBase
from app.model import MessageImage
from app.schema.message_image import MessageImageCreate


class CRUDMessageImage:
    def get(self, db: Session, id: int) -> MessageImage:
        return db.query(MessageImage).filter(MessageImage.id == id).first()

    def get_by_message_id(self, db: Session, message_id: int) -> MessageImage:
        return (
            db.query(MessageImage).filter(MessageImage.message_id == message_id).all()
        )

    def create(self, db: Session, obj_in: MessageImageCreate) -> MessageImage:
        db_obj = MessageImage(
            message_id=obj_in.message_id, url=obj_in.url, position=obj_in.position
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, id: int) -> None:
        db.query(MessageImage).filter(MessageImage.id == id).delete()
        db.commit()


message_image = CRUDMessageImage()
