from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

from app.schema.page import Pagination
from app.hepler.enum import JobApprovalStatus
from app.schema.account import AccountBasicResponse


class JobApprovalLogBase(BaseModel):
    model_config = ConfigDict(from_attribute=True, extra="ignore")

    job_approval_request_id: int
    previous_status: Optional[JobApprovalStatus]
    new_status: Optional[JobApprovalStatus]
    reason: Optional[str] = None


# request
class JobApprovalLogGetListRequest(Pagination):
    job_approval_request_id: Optional[JobApprovalStatus] = None
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