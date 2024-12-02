from fastapi import status
from sqlalchemy.orm import Session

from app.crud import job_approval_log as job_approval_logCRUD
from app.schema.job_approval_log import JobApprovalLogCreate
from app.core import constant
from app.core.job import job_helper
from app.crud.job import job as jobCRUD
from app.hepler.enum import JobStatus, JobApprovalStatus
from app.common.exception import CustomException
from app.common.response import CustomResponse

class JobApprovalLogService:
    def get_by_id(self, db: Session, id: int):
        job_approval_log = job_approval_logCRUD.get(db, id)
        if not job_approval_log:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Job approval log not found",
            )
        return CustomResponse(data=job_approval_log)

    def get(self, db: Session, data: dict):
        job_approval_log_data = JobApprovalLogGetListRequest(**data)

        response = job_approval_logCRUD.get_multi(
            db,
            **job_approval_log_data.model_dump(),
        )

        return CustomResponse(data=response)


job_approval_log_service = JobApprovalLogService()