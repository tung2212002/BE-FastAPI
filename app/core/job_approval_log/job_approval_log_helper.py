from sqlalchemy.orm import Session

from app.crud import (
    job_approval_log as job_approval_logCRUD,
)
from app.schema.job_approval_log import JobApprovalLogCreate, JobApprovalLogResponse
from app.model import ApprovalLog


class JobApprovalLogHelper:
    def create_job_approval_log(
        self, db: Session, data: JobApprovalLogCreate
    ) -> ApprovalLog:
        job_approval_log = job_approval_logCRUD.create(db, obj_in=data)
        return job_approval_log

    def get_by_job_approval_id(
        self, db: Session, job_approval_id: int
    ) -> JobApprovalLogResponse:
        job_approval_log: ApprovalLog = job_approval_logCRUD.get_by_job_approval_id(
            db, job_approval_id
        )
        return (
            JobApprovalLogResponse(**job_approval_log.__dict__)
            if job_approval_log
            else None
        )


job_approval_log_helper = JobApprovalLogHelper()
