from sqlalchemy.orm import Session
from redis.asyncio import Redis
from fastapi import status

from app.crud import cv_applications as cv_applicationCRUD, job as jobCRUD
from app.model import CVApplication, Job, Campaign, Company, User, Account
from app.core.job.job_helper import job_helper
from app.core.company.company_helper import company_helper
from app.core.user.user_helper import user_helper
from app.schema.cv_application import (
    CVApplicationUserItemResponse,
    CVApplicationGeneralResponse,
)
from app.common.exception import CustomException
from app.schema.user import UserBasicResponse
from app.schema.job import CVApplicationInfoResponse
from app.schema.job import JobItemResponseGeneral
from app.hepler.common import CommonHelper
from app.hepler.enum import JobStatus


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
            **cv_application.__dict__,
            job=job_info,
            company=company_info,
            user=self.get_user_info(db, cv_application)
        )

    async def get_info_general(
        self, db: Session, cv_application: CVApplication
    ) -> CVApplicationGeneralResponse:
        campaign: Campaign = cv_application.campaign
        job: Job = campaign.job
        job_info: JobItemResponseGeneral = job_helper.get_info_general(job)

        return CVApplicationGeneralResponse(
            **cv_application.__dict__,
            job=job_info,
            user=self.get_user_info(db, cv_application)
        )

    def get_info(
        self, db: Session, cv_application: CVApplication
    ) -> CVApplicationInfoResponse:

        return CVApplicationInfoResponse(
            **cv_application.__dict__, user=self.get_user_info(db, cv_application)
        )

    def job_open(sefl, db: Session, job_id: int) -> Job:
        job = jobCRUD.get(db, job_id)
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
            cv_applicationCRUD.get_by_user_id_and_campaign_id(db, user_id, campaign_id)
            is not None
        )

    def get_user_info(
        self, db: Session, cv_application: CVApplication
    ) -> UserBasicResponse:
        user: User = cv_application.user
        account: Account = user.account
        return user_helper.get_basic_info(db, account, user)

    def list_info_by_campaign_id(
        self, db: Session, campaign_id: int, skip: int, limit: int
    ) -> list[CVApplicationInfoResponse]:
        cv_applications = cv_applicationCRUD.get_by_campaign_id(
            db, campaign_id=campaign_id, skip=skip, limit=limit
        )
        return [self.get_info(db, cv_application) for cv_application in cv_applications]


cv_applications_helper = CVApplicationsHelper()
