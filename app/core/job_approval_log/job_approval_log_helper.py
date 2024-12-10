from sqlalchemy.orm import Session
from typing import List

from app.crud import (
    job_approval_log as job_approval_logCRUD,
)
from app.schema.job_approval_log import JobApprovalLogCreate, JobApprovalLogResponse
from app.model import ApprovalLog


class JobApprovalLogHelper:
    def create(
        self,
        db: Session,
        job_id: int,
        previous_status: str,
        new_status: str,
        admin_id: int,
        reason: str,
    ) -> ApprovalLog:
        job_approval_log = JobApprovalLogCreate(
            **{
                "job_id": job_id,
                "previous_status": previous_status,
                "new_status": new_status,
                "admin_id": admin_id,
                "reason": reason,
            }
        )
        job_approval_log: ApprovalLog = job_approval_logCRUD.create(
            db, obj_in=job_approval_log
        )

        return job_approval_log

    def get_by_job_id(self, db: Session, job_id: int) -> List[JobApprovalLogResponse]:
        job_approval_logs: List[ApprovalLog] = job_approval_logCRUD.get_by_job_id(
            db, job_id
        )
        return [
            JobApprovalLogResponse(**job_approval_log.__dict__)
            for job_approval_log in job_approval_logs
        ]


job_approval_log_helper = JobApprovalLogHelper()
