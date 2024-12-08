from sqlalchemy.orm import Session
from typing import List

from app.schema.job_approval_request import (
    JobApprovalRequestList,
    JobApprovalRequestCreate,
    JobApprovalRequestUpdate,
    JobApprovalRequestUpdateRequest,
)
from app.schema.job import JobApproveRequest
from app.schema.job_approval_log import JobApprovalLogCreate
from app.core.job_approval_log.job_approval_log_helper import job_approval_log_helper
from app.crud.job import job as jobCRUD
from app.crud import job_approval_request as job_approval_requestCRUD
from app.hepler.enum import JobStatus, JobApprovalStatus
from app.model import Account, JobApprovalRequest, Business, Job
from fastapi import status
from app.common.exception import CustomException
from app.common.response import CustomResponse


class JobApprovalRequestService:
    async def get(self, db: Session, data: dict):
        job_approval_request_data = JobApprovalRequestList(**data)

        response = job_approval_requestCRUD.get_multi(
            db,
            **job_approval_request_data.model_dump(),
        )

        return CustomResponse(data=response)

    async def get_by_id(self, db: Session, id: int):
        response = job_approval_requestCRUD.get(db, id)
        if not response:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Job approval request not found",
            )

        return CustomResponse(data=response)

    async def approve(self, db: Session, current_user: Account, data: dict):
        job_approval_request_data = JobApproveRequest(**data)

        job_approval_request: JobApprovalRequest = job_approval_requestCRUD.get(
            db, job_approval_request_data.job_approval_request_id
        )
        if not job_approval_request:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Job approval request not found",
            )

        job: Job = job_approval_request.job
        job_status = job.status
        if job_status == job_approval_request_data.status:
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, msg="Job already approved"
            )

        if job_approval_request_data.status == JobApprovalStatus.APPROVED:
            if job_status == JobStatus.PENDING:
                jobCRUD.update(db, db_obj=job, obj_in={"status": JobStatus.PUBLISHED})
        else:
            jobCRUD.update(db, db_obj=job, obj_in={"status": JobStatus.REJECTED})

        job_approval_request.id
        job_approval_requestCRUD.update(
            db,
            db_obj=job_approval_request,
            obj_in={"status": job_approval_request_data.status},
        )

        job_approval_log_helper.create(
            db,
            job_approval_request.id,
            job_status,
            job_approval_request_data.status,
            current_user.id,
            job_approval_request_data.reason,
        )

        return CustomResponse(data=job_approval_request)

    async def approve_update(self, db: Session, current_user: Account, data: dict):
        job_approval_update_data = JobApprovalRequestUpdateRequest(**data)

        job_approval_request = job_approval_requestCRUD.get(
            db, job_approval_update_data.id
        )
        if not job_approval_request:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Job approval request not found",
            )

        job = job_approval_request.job
        if job_approval_request.status == job_approval_update_data.status:
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, msg="Job already approved"
            )

        if (
            job_approval_update_data.status == job_approval_request.status
            or job_approval_request.status != JobApprovalStatus.PENDING
        ):
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, msg="Invalid status"
            )

        job_approval_request.id
        if job_approval_request.status == JobApprovalStatus.APPROVED:
            job_update_in = JobApprovalRequestUpdate(**job_approval_request.__dict__)
            jobCRUD.update(db, db_obj=job, obj_in=job_update_in)
        job_approval_requestCRUD.update(
            db,
            db_obj=job_approval_request,
            obj_in={"status": job_approval_update_data.status},
        )

        job_approval_log_helper.create(
            db,
            job_approval_request.id,
            job_approval_request.status,
            job_approval_update_data.status,
            current_user.id,
            job_approval_update_data.reason,
        )

        return CustomResponse(data=job_approval_request)


job_approval_request_service = JobApprovalRequestService()
