from sqlalchemy.orm import Session

from app.crud import (
    job_approval_log as job_approval_logCRUD,
)
from app.schema.job_approval_log import JobApprovalLogCreate
from app.model import ApprovalLog


class JobApprovalLogHelper:
    def create_job_approval_log(
        self, db: Session, data: JobApprovalLogCreate
    ) -> ApprovalLog:
        job_approval_log = job_approval_logCRUD.create(db, obj_in=data)
        return job_approval_log


job_approval_log_helper = JobApprovalLogHelper()
