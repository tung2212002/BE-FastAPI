from typing import List
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.model import ApprovalLog, Job
from app.schema.job_approval_log import JobApprovalLogCreate


class CRUDJobLogRequest:
    def get(self, db: Session, id: int) -> ApprovalLog:
        return db.query(ApprovalLog).filter(ApprovalLog.id == id).first()

    def create(self, db: Session, obj_in: JobApprovalLogCreate) -> ApprovalLog:
        db_obj = ApprovalLog(
            job_id=obj_in.job_id,
            admin_id=obj_in.admin_id,
            previous_status=obj_in.previous_status,
            new_status=obj_in.new_status,
            reason=obj_in.reason,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_job_id(self, db: Session, job_id: int) -> ApprovalLog:
        return db.query(ApprovalLog).filter(ApprovalLog.job_id == job_id).all()


job_approval_log = CRUDJobLogRequest()
