from typing import List
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.model import ApprovalLog, Job
from app.schema.job_approval_log import JobApprovalLogCreate


class CRUDJobLogRequest:
    def get(self, db: Session, job_approval_request_id: int) -> Job:
        return db.query(Job).filter(Job.id == job_approval_request_id).first()

    def create(self, db: Session, obj_in: JobApprovalLogCreate) -> ApprovalLog:
        db_obj = ApprovalLog(
            job_approval_request_id=obj_in.job_approval_request_id,
            admin_id=obj_in.admin_id,
            previous_status=obj_in.previous_status,
            new_status=obj_in.new_status,
            reason=obj_in.reason,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


job_approval_log = CRUDJobLogRequest()
