from sqlalchemy.orm import Session
from redis.asyncio import Redis
from fastapi import status
from typing import List

from app.crud import (
    cv_applications as cv_applicationCRUD,
    campaign as campaignCRUD,
    user as userCRUD,
)
from app.schema.cv_application import (
    CVApplicationCreate,
    CVApplicationUpdate,
    CVApplicationUpdateInfo,
    CVApplicationCreateRequest,
    CVApplicationUpdateRequest,
    CVApplicationUserFilter,
    CVApplicationUserFilterCount,
    CVApplicationUserItemResponse,
)
from app.schema.file import FileInfo
from app.common.exception import CustomException
from app.model import Account, CVApplication, Job
from app.common.response import CustomResponse
from app.storage.cache.cv_cache_service import cv_cache_service
from app.core.cv_applications.cv_applications_helper import cv_applications_helper
from app.core.file.file_helper import file_helper
from app.hepler.enum import CVApplicationStatus, FolderBucket


class CVApplicationsService:
    async def get(
        self, db: Session, redis: Redis, data: dict, current_user: Account
    ) -> CustomResponse:
        page = CVApplicationUserFilter(**data)
        count_page = CVApplicationUserFilterCount(**data)

        count: int = cv_applicationCRUD.count_by_user_id(
            db, user_id=current_user.id, **count_page.model_dump()
        )

        if count < page.skip:
            return CustomResponse(data={"jobs": [], "count": count})

        cv_applications: List[CVApplication] = cv_applicationCRUD.get_by_user_id(
            db, user_id=current_user.id, **page.model_dump()
        )

        cv_applications_response: List[CVApplicationUserItemResponse] = [
            await cv_applications_helper.get_full_info(db, cv_application)
            for cv_application in cv_applications
        ]

        return CustomResponse(data={"jobs": cv_applications_response, "count": count})

    async def get_by_id(
        self, db: Session, id: int, current_user: Account
    ) -> CustomResponse:
        cv_application: CVApplication = cv_applicationCRUD.get(db, id)

        if not cv_application:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="CV application not found"
            )

        if cv_application.user_id != current_user.id:
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN, msg="Forbidden"
            )

        response: CVApplicationUserItemResponse = (
            await cv_applications_helper.get_full_info(db, cv_application)
        )

        return CustomResponse(data=response)

    async def create(
        self, db: Session, redis: Redis, data: dict, current_user: Account
    ) -> CustomResponse:
        cv_applications_data: CVApplicationCreateRequest = CVApplicationCreateRequest(
            **data
        )

        job: Job = cv_applications_helper.job_open(db, cv_applications_data.job_id)
        if not job:
            raise CustomException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE, msg="Job is not open"
            )

        cv_application: CVApplication = (
            cv_applicationCRUD.get_by_user_id_and_campaign_id(
                db, user_id=current_user.id, campaign_id=job.campaign.id
            )
        )
        if cv_application:
            if cv_application.count_apply == 3:
                raise CustomException(
                    status_code=status.HTTP_409_CONFLICT,
                    msg="CV application is max apply",
                )

        file_info: FileInfo = await file_helper.upload_file(
            cv_applications_data.cv, FolderBucket.CV
        )

        if cv_application:
            obj_in = CVApplicationUpdateInfo(
                cv=file_info.url,
                name=file_info.name,
                size=file_info.size,
                type=file_info.type,
                letter_cover=cv_applications_data.letter_cover,
                status=CVApplicationStatus.PENDING,
                full_name=cv_applications_data.full_name,
                email=cv_applications_data.email,
                phone_number=cv_applications_data.phone_number,
                count_apply=cv_application.count_apply + 1,
            )
            cv_application: CVApplication = cv_applicationCRUD.update(
                db, db_obj=cv_application, obj_in=obj_in
            )
        else:
            obj_in = CVApplicationCreate(
                **{k: v for k, v in cv_applications_data.__dict__.items() if k != "cv"},
                **file_info.model_dump(),
                cv=file_info.url,
                user_id=current_user.id,
                campaign_id=job.campaign.id,
            )
            cv_application: CVApplication = cv_applicationCRUD.create(db, obj_in=obj_in)
            campaignCRUD.increase_count_apply(db, job.campaign)
            userCRUD.increase_count_job_apply(db, current_user.user)

            try:
                await cv_cache_service.incr(
                    redis, f"{current_user.id}_{cv_application.status}"
                )
            except Exception as e:
                print(e)

        response: CVApplicationUserItemResponse = (
            await cv_applications_helper.get_full_info(db, cv_application)
        )

        return CustomResponse(data=response)

    async def update(
        self, db: Session, data: dict, current_user: Account
    ) -> CustomResponse:
        cv_application_data = CVApplicationUpdateRequest(**data)

        cv_application = cv_applicationCRUD.get(
            db, cv_application_data.cv_application_id
        )
        if not cv_application:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="CV application not found"
            )

        if cv_application.campaign.business_id != current_user.id:
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN, msg="Forbidden"
            )

        cv_application = cv_applicationCRUD.update(
            db,
            db_obj=cv_application,
            obj_in=CVApplicationUpdate(**cv_application_data.model_dump()),
        )

        response: CVApplicationUserItemResponse = (
            await cv_applications_helper.get_full_info(db, cv_application)
        )

        return CustomResponse(data=response)


cv_applications_service = CVApplicationsService()
