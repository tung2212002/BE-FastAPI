from sqlalchemy.orm import Session
from typing import Any, Optional

from app.model import JobApprovalRequest
from app.schema.job_approval_request import (
    JobApprovalCreate,
    JobApprovalRequestResponse,
)
from app.crud.job_approval_request import (
    job_approval_request as job_approval_requestCRUD,
)
from app.hepler.enum import JobApprovalStatus


class JobApprovalRequestHelper:
    def create(
        self,
        db: Session,
        job_id: int,
        status: JobApprovalStatus,
        data: Optional[Any] = None,
    ) -> JobApprovalRequest:
        job_approval_request = JobApprovalCreate(
            job_id=job_id, status=status, data=data
        )
        return job_approval_requestCRUD.create(db, obj_in=job_approval_request)

    def get_by_job_id(self, db: Session, job_id: int) -> JobApprovalRequest:
        return job_approval_requestCRUD.get_last_by_job_id(db, job_id=job_id)


job_approval_request_helper = JobApprovalRequestHelper()
