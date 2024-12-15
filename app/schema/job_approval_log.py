from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

from app.schema.page import Pagination
from app.hepler.enum import JobLogStatus
from app.schema.account import AccountBasicResponse


class JobApprovalLogBase(BaseModel):
    model_config = ConfigDict(from_attribute=True, extra="ignore")

    job_id: int
    previous_status: Optional[JobLogStatus]
    new_status: Optional[JobLogStatus]
    reason: Optional[str] = None


# request
class JobApprovalLogGetListRequest(Pagination):
    status: Optional[JobLogStatus] = None
    admin_id: Optional[int] = None


# schema
class JobApprovalLogCreate(JobApprovalLogBase):
    admin_id: int


# response
class JobApprovalLogResponse(JobApprovalLogBase):
    id: int
    created_at: datetime


class JobApprovalLogDetailResponse(JobApprovalLogBase):
    id: int
    created_at: datetime
    admin: AccountBasicResponse
