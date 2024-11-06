from redis.asyncio import Redis
from sqlalchemy.orm import Session


from app.crud import account as accountCRUD, message as messageCRUD
from app.model import Account
from app.schema.account import AccountBasicResponse


class MessageHelper:
    async def check_parent_message(
        self, db: Session, redis: Redis, parent_message_id: int, conversation_id: int
    ) -> bool:
        message = messageCRUD.get(db, parent_message_id)
        if message is None:
            return False

        return message.conversation_id == conversation_id


message_helper = MessageHelper()
