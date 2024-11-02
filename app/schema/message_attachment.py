from pydantic import BaseModel, ConfigDict, validator
from datetime import datetime
from typing import List, Optional
from fastapi import UploadFile

from app.hepler.schema_validator import SchemaValidator


# request
class AttachmentCreateRequest(BaseModel):
    files: List[UploadFile]
    conversation_id: int = None

    @validator("files")
    def validate_files(cls, v):
        return SchemaValidator.validate_files(v)

    @validator("conversation_id")
    def validate_conversation_id(cls, v):
        if v is None:
            return 0
        return v

    model_config = ConfigDict(from_attribute=True, extra="ignore")


# schema
class MessageAttachmentCreate(BaseModel):
    message_id: int
    url: str
    position: int

    model_config = ConfigDict(from_attribute=True, extra="ignore")


# response
class MessageAttachmentResponse(BaseModel):
    id: int
    message_id: int
    url: str
    position: int

    model_config = ConfigDict(from_attribute=True, extra="ignore")


class AttachmentResponse(BaseModel):
    upload_filename: str
    url: str = None
    id: Optional[int] = None
    position: Optional[int] = None

    @validator("url")
    def validate_url(cls, v, values):
        return SchemaValidator.validate_attachment_url(v, values)
