from fastapi import status
from sqlalchemy.orm import Session
from redis.asyncio import Redis
from typing import List
import json

from app.schema.job_approval_request import (
    JobApprovalRequestList,
    JobApprovalRequestCreate,
    JobApprovalRequestUpdate,
    JobApprovalRequestUpdateRequest,
)
from app.schema.job import JobApproveRequest, JobUpdate, JobUpdateRequest
from app.schema.job_approval_log import JobApprovalLogCreate
from app.core.job_approval_log.job_approval_log_helper import job_approval_log_helper
from app.crud.job import job as jobCRUD
from app.crud import job_approval_request as job_approval_requestCRUD
from app.hepler.enum import JobStatus, JobApprovalStatus, JobLogStatus
from app.model import Account, JobApprovalRequest, Business, Job
from app.common.exception import CustomException
from app.common.response import CustomResponse
from app.storage.cache.job_cache_service import job_cache_service
from app.core.job.job_helper import job_helper


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

    async def approve(
        self, db: Session, redis: Redis, current_user: Account, data: dict
    ):
        job_approval_request_data = JobApproveRequest(**data)
        print(job_approval_request_data)
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
        if (
            job_status == job_approval_request_data.status
            or job_status != JobStatus.PENDING
        ):
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, msg="Invalid status"
            )

        if job_approval_request_data.status == JobApprovalStatus.APPROVED:
            if job_status == JobStatus.PENDING:
                jobCRUD.update_status_job(db, job, JobStatus.PUBLISHED)
            job_approval_log_helper.create(
                db,
                job.id,
                JobLogStatus.PENDING,
                JobLogStatus.APPROVED,
                current_user.id,
                job_approval_request_data.reason,
            )
        else:
            print("REJECTED")
            jobCRUD.update_status_job(db, job, JobStatus.REJECTED)
            job_approval_log_helper.create(
                db,
                job.id,
                JobLogStatus.PENDING,
                JobLogStatus.REJECTED,
                current_user.id,
                job_approval_request_data.reason,
            )

        job_approval_request.id
        job_approval_requestCRUD.update(
            db,
            db_obj=job_approval_request,
            obj_in={"status": job_approval_request_data.status},
        )

        try:
            await job_cache_service.delete_job_info(redis, job.id)
        except Exception as e:
            print(e)

        return CustomResponse(data=job_approval_request)

    async def approve_update(
        self, db: Session, redis: Redis, current_user: Account, data: dict
    ):
        job_approval_update_data = JobApprovalRequestUpdateRequest(**data)

        job_approval_request: JobApprovalRequest = job_approval_requestCRUD.get(
            db, job_approval_update_data.id
        )
        if not job_approval_request:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND,
                msg="Job approval request not found",
            )

        job: Job = job_approval_request.job
        job_approval_request.id

        if job_approval_request.status == job_approval_update_data.status:
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, msg="Job already approved"
            )

        if (
            job_approval_update_data.status == JobApprovalStatus.STOPPED
            and job.status != JobStatus.PUBLISHED
        ):
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, msg="Invalid status"
            )

        if (
            job_approval_update_data.status == JobApprovalStatus.STOPPED
            and job.status == JobStatus.PUBLISHED
        ):
            jobCRUD.update_status_job(db, job, JobStatus.STOPPED)
            job_approval_log_helper.create(
                db,
                job.id,
                JobLogStatus.PUBLISHED,
                JobLogStatus.STOPPED,
                current_user.id,
                job_approval_update_data.reason,
            )
            if job_approval_request.status == JobApprovalStatus.PENDING:
                job_approval_requestCRUD.update(
                    db,
                    db_obj=job_approval_request,
                    obj_in={"status": JobApprovalStatus.STOPPED},
                )
            try:
                await job_cache_service.delete_job_info(redis, job.id)
            except Exception as e:
                print(e)
            return CustomResponse(data=job_approval_request)

        if (
            job_approval_update_data.status == job_approval_request.status
            or job_approval_request.status != JobApprovalStatus.PENDING
        ):
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, msg="Invalid status"
            )

        job_approval_request.id
        print(job_approval_update_data.status)
        if job_approval_update_data.status == JobApprovalStatus.APPROVED:
            data = job_approval_request.data
            job_data = JobUpdateRequest(**data)
            job_in = JobUpdate(**job_data.dict())
            jobCRUD.update(db, db_obj=job, obj_in=job_in)
            job_helper.update_job_fields(db, job.id, job_data)

            job_approval_requestCRUD.update(
                db,
                db_obj=job_approval_request,
                obj_in={"status": JobApprovalStatus.APPROVED},
            )

            job_approval_log_helper.create(
                db,
                job.id,
                JobLogStatus.PENDING,
                JobLogStatus.APPROVED,
                current_user.id,
                job_approval_update_data.reason,
            )
        elif job_approval_update_data.status == JobApprovalStatus.REJECTED:
            print("REJECTED......")
            print(job_approval_request)
            print(job)
            job_approval_requestCRUD.update(
                db,
                db_obj=job_approval_request,
                obj_in={"status": JobApprovalStatus.REJECTED},
            )

            job_approval_log_helper.create(
                db,
                job.id,
                JobLogStatus.PENDING,
                JobLogStatus.REJECTED,
                current_user.id,
                job_approval_update_data.reason,
            )

        try:
            await job_cache_service.delete_job_info(redis, job.id)
        except Exception as e:
            print(e)

        return CustomResponse(data=job_approval_request)


job_approval_request_service = JobApprovalRequestService()
