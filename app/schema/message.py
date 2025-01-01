from pydantic import BaseModel, ConfigDict, Field, validator
from typing import Optional
from datetime import datetime
from typing import List

from app.hepler.enum import MessageType
from app.schema.user import UserBasicResponse
from app.schema.account import AccountBasicResponse
from app.schema.message_attachment import AttachmentResponse
from app.schema.company import CompanyItemGeneralResponse


# request
class GetMessagesRequest(BaseModel):
    conversation_id: int
    limit: Optional[int] = Field(10, ge=1, le=20)
    skip: Optional[int] = Field(0, ge=0)

    @validator("limit")
    def validate_limit(cls, v):
        return v or 10

    @validator("skip")
    def validate_skip(cls, v):
        return v or 0

    model_config = ConfigDict(from_attribute=True, extra="ignore")


# schema
class Attachment(BaseModel):
    filename: str
    uploaded_filename: str

    model_config = ConfigDict(from_attribute=True, extra="ignore")


class MessageCreate(BaseModel):
    conversation_id: int
    account_id: int
    type: MessageType = MessageType.TEXT
    content: Optional[str] = None
    parent_id: Optional[int] = None

    model_config = ConfigDict(from_attribute=True, extra="ignore")


# response
class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    account_id: int
    type: MessageType
    content: Optional[str] = None
    parent_id: Optional[int] = None
    like_count: int
    dislike_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    user: AccountBasicResponse
    parent: Optional[dict] = None
    attachments: Optional[List[AttachmentResponse]] = None
    is_pinned: bool

    model_config = ConfigDict(from_attribute=True, extra="ignore")


class MessageBasicResponse(BaseModel):
    id: int
    conversation_id: int
    account_id: int
    type: MessageType
    content: Optional[str] = None
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: AccountBasicResponse
    parent: Optional[dict] = None
    attachments: Optional[List[AttachmentResponse]] = None
    is_pinned: bool

    model_config = ConfigDict(from_attribute=True, extra="ignore")


class MessageUpdate(BaseModel):
    content: str

    model_config = ConfigDict(from_attribute=True, extra="ignore")
