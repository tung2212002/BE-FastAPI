from pydantic import BaseModel, Field, validator, ConfigDict
from typing import Optional

from app.hepler.enum import AttachmentType


class FileInfo(BaseModel):
    url: str
    type: AttachmentType
    size: int
    name: str

    model_config = ConfigDict(from_attribute=True, extra="ignore")
