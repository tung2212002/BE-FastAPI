from sqlalchemy.orm import Session
from redis.asyncio import Redis
from typing import List
from fastapi import status

from app import crud
from app.model import CVApplication, Job
from app.core.job.job_helper import job_helper
from app.core.company.company_helper import company_helper
from app.schema.cv_application import (
    CVApplicationUserItemResponse,
    CVApplicationGeneralResponse,
)
from app.hepler.common import CommonHelper
from app.hepler.enum import JobStatus
from app.common.exception import CustomException


class CVApplicationsHelper:
    async def get_full_info(
        self, db: Session, cv_application: CVApplication
    ) -> CVApplicationUserItemResponse:
        campaign = cv_application.campaign
        job = campaign.job
        company = campaign.company
        job_info = job_helper.get_info_general(job)
        company_info = company_helper.get_info_general(company)

        return CVApplicationUserItemResponse(
            **cv_application.__dict__, job=job_info, company=company_info
        )

    async def get_info_general(
        self, db: Session, cv_application: CVApplication
    ) -> CVApplicationGeneralResponse:
        campaign = cv_application.campaign
        job = campaign.job
        job_info = job_helper.get_info_general(job)

        return CVApplicationGeneralResponse(**cv_application.__dict__, job=job_info)

    def job_open(sefl, db: Session, job_id: int) -> Job:
        job = crud.job.get(db, job_id)
        if not job:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Job not found"
            )

        time_now = CommonHelper.get_current_time(db).date()
        if job.status != JobStatus.PUBLISHED or job.deadline < time_now:
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, msg="Job is not open"
            )

        return job

    def check_cv_application_exists(
        self, db: Session, user_id: int, campaign_id: int
    ) -> bool:
        return (
            crud.cv_applications.get_by_user_id_and_campaign_id(
                db, user_id, campaign_id
            )
            is not None
        )


cv_applications_helper = CVApplicationsHelper()