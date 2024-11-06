from pydantic import BaseModel, validator, ConfigDict, Field
from fastapi import UploadFile
from typing import Optional, Union
from datetime import datetime

from app.hepler.enum import (
    CVApplicationStatus,
    CVApplicationUpdateStatus,
    AttachmentType,
)
from app.schema.page import Pagination
from app.hepler.schema_validator import SchemaValidator
from app.schema.job import JobItemResponseGeneral
from app.schema.company import CompanyItemGeneralResponse


class CVApplicationBase(BaseModel):
    full_name: str
    email: str
    phone_number: str
    letter_cover: Optional[str] = None

    model_config = ConfigDict(from_attribute=True, extra="ignore")


# request
class CVApplicationUserFilter(Pagination):
    status: Optional[CVApplicationStatus] = None

    def get_key(self, user_id: int) -> str:
        return f"{user_id}_{self.status}"


class CVApplicationUserFilterCount(BaseModel):
    status: Optional[CVApplicationStatus] = None

    model_config = ConfigDict(from_attribute=True, extra="ignore")


class CVApplicationCreateRequest(BaseModel):
    job_id: int
    cv: UploadFile
    full_name: str
    email: str
    phone_number: str
    letter_cover: Optional[str] = Field(None, max_length=500)

    model_config = ConfigDict(from_attribute=True, extra="ignore")

    @validator("full_name")
    def validate_full_name(cls, v):
        return SchemaValidator.validate_full_name(v)

    @validator("email")
    def validate_email(cls, v):
        return SchemaValidator.validate_email(v)

    @validator("phone_number")
    def validate_phone_number(cls, v):
        return SchemaValidator.validate_phone_number(v)

    @validator("cv")
    def validate_cv(cls, v):
        return SchemaValidator.validate_cv_upload_file(v)


class CVApplicationUpdateRequest(BaseModel):
    status: CVApplicationUpdateStatus
    job_id: int
    cv_application_id: int

    model_config = ConfigDict(from_attribute=True, extra="ignore")


# schema
class CVApplicationCreate(CVApplicationBase):
    campaign_id: int
    user_id: int
    cv: str
    name: str
    size: int
    type: AttachmentType
    status: CVApplicationStatus = CVApplicationStatus.PENDING


class CVApplicationUpdate(BaseModel):
    status: CVApplicationStatus

    model_config = ConfigDict(from_attribute=True, extra="ignore")


class CVApplicationUpdateInfo(BaseModel):
    cv: str
    name: str
    size: int
    type: AttachmentType
    status: CVApplicationStatus
    full_name: str
    email: str
    phone_number: str
    letter_cover: Optional[str] = None
    count_apply: int

    model_config = ConfigDict(from_attribute=True, extra="ignore")


# response
class CVApplicationUserItemResponse(CVApplicationBase):
    id: int
    status: CVApplicationStatus
    created_at: datetime
    job: JobItemResponseGeneral
    company: CompanyItemGeneralResponse
    cv: str
    name: str
    size: int
    type: AttachmentType
    count_apply: int

    @validator("cv")
    def validate_cv(cls, v):
        return SchemaValidator.validate_cv_url(v)


class CVApplicationGeneralResponse(CVApplicationBase):
    id: int
    status: CVApplicationStatus
    created_at: datetime
    job: JobItemResponseGeneral
    cv: str
    name: str
    size: int
    type: AttachmentType
    count_apply: int

    @validator("cv")
    def validate_cv(cls, v):
        return SchemaValidator.validate_cv_url(v)
