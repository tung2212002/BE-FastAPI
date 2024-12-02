from fastapi import status as status_code
from sqlalchemy.orm import Session
from typing import Optional, Union, Tuple, List
from pydantic import BaseModel

from app.crud import campaign as campaignCRUD, company as companyCRUD
from app.hepler.enum import CampaignStatus
from app.core.business.business_helper import business_helper
from app.core.company.company_helper import company_helper
from app.core.job.job_helper import job_helper
from app.core.cv_applications.cv_applications_helper import cv_applications_helper
from app.model import Campaign, Business, Company
from app.schema.campaign import (
    CampaignItemResponse,
    CampaignGetMutilPagination,
    CountGetListPagination,
    CampaignGetOnlyOpenPagination,
    CampaignGetHasNewApplicationPagination,
    CampaignGetHasPublishedJobPagination,
    CampaignGetHasPublishedJobExpiredPagination,
    CampaignGetHasPendingJobPagination,
    CountGetListStatusPagination,
)
from app.schema.job import CVApplicationInfoResponse
from app.schema.business import BusinessBasicInfoResponse
from app.schema.company import CompanyItemGeneralResponse
from app.common.exception import CustomException


class CampaignHelper:
    def check_exist(
        self,
        db: Session,
        business_id: int,
        campaign_id: Optional[int],
        status: Optional[CampaignStatus],
        title: str,
    ) -> Campaign:
        if campaign_id:
            campaign = campaignCRUD.get(db, campaign_id)
            if not campaign:
                raise CustomException(
                    status_code=status_code.HTTP_404_NOT_FOUND, msg="Campaign not found"
                )

            if campaign.business_id != business_id:
                raise CustomException(
                    status_code=status_code.HTTP_403_FORBIDDEN, msg="Permission denied"
                )

            if campaign.status != status:
                raise CustomException(
                    status_code=status_code.HTTP_400_BAD_REQUEST,
                    msg="Campaign is not active",
                )

            return campaign
        else:
            company = companyCRUD.get_by_business_id(db, business_id)
            campaign = campaignCRUD.create(
                db,
                obj_in={
                    "business_id": business_id,
                    "title": title,
                    "company_id": company.id,
                },
            )

            return campaign

    def get_info(self, db: Session, campaign: Campaign) -> CampaignItemResponse:
        job = job_helper.get_info_general(campaign.job) if campaign.job else None
        business: Business = campaign.business
        company: Company = campaign.company

        campaign_response = CampaignItemResponse(
            **{
                k: v
                for k, v in campaign.__dict__.items()
                if k not in ["job", "company", "business"]
            },
            job=job.model_dump() if job else None,
            latest_cvs=(
                cv_applications_helper.list_info_by_campaign_id(db, campaign.id, 0, 5)
                if campaign.count_apply > 0
                else []
            )
            business=business_helper.get_basic_info_by_business(db, business),
            company=company_helper.get_info_general(company),
        )

        return campaign_response

    def get_list_campaign(
        self, db: Session, page: Union[dict, BaseModel]
    ) -> Tuple[List[Campaign], int]:
        multi_paigination = CampaignGetMutilPagination(**page.model_dump())
        count_pagination = CountGetListPagination(**page.model_dump())

        count = campaignCRUD.count(db, **count_pagination.model_dump())
        if count < multi_paigination.skip:
            return [], count

        return campaignCRUD.get_multi(db, **multi_paigination.model_dump()), count

    def get_list_campaign_open(
        self, db: Session, page: Union[dict, BaseModel]
    ) -> Tuple[List[Campaign], int]:
        multi_paigination = CampaignGetOnlyOpenPagination(**page.model_dump())
        count_pagination = CountGetListStatusPagination(**page.model_dump())

        count = campaignCRUD.count(db, **count_pagination.model_dump())
        if count < multi_paigination.skip:
            return [], count

        return campaignCRUD.get_open(db, **multi_paigination.model_dump()), count

    def get_list_campaign_has_new_application(
        self, db: Session, page: Union[dict, BaseModel]
    ) -> Tuple[List[Campaign], int]:
        multi_paigination = CampaignGetHasNewApplicationPagination(**page.model_dump())
        count_pagination = CountGetListPagination(**page.model_dump())

        count = campaignCRUD.count_has_new_application(
            db, **count_pagination.model_dump()
        )
        if count < multi_paigination.skip:
            return [], count

        return (
            campaignCRUD.get_has_new_application(db, **multi_paigination.model_dump()),
            count,
        )

    def get_list_campaign_has_published_job(
        self, db: Session, page: Union[dict, BaseModel]
    ) -> Tuple[List[Campaign], int]:
        multi_paigination = CampaignGetHasPublishedJobPagination(**page.model_dump())
        count_pagination = CountGetListStatusPagination(**page.model_dump())

        count = campaignCRUD.count_has_published_job(
            db, **count_pagination.model_dump()
        )
        if count < multi_paigination.skip:
            return [], count

        return (
            campaignCRUD.get_has_published_job(db, **multi_paigination.model_dump()),
            count,
        )

    def get_list_campaign_has_published_job_expired(
        self, db: Session, page: Union[dict, BaseModel]
    ) -> Tuple[List[Campaign], int]:
        multi_paigination = CampaignGetHasPublishedJobExpiredPagination(
            **page.model_dump()
        )
        count_pagination = CountGetListStatusPagination(**page.model_dump())

        count = campaignCRUD.count_has_published_job_expired(
            db, **count_pagination.model_dump()
        )
        if count < multi_paigination.skip:
            return [], count

        return (
            campaignCRUD.get_has_published_job_expired(
                db, **multi_paigination.model_dump()
            ),
            count,
        )

    def get_list_campaign_has_pending_job(
        self, db: Session, page: Union[dict, BaseModel]
    ) -> Tuple[List[Campaign], int]:
        multi_paigination = CampaignGetHasPendingJobPagination(**page.model_dump())
        count_pagination = CountGetListStatusPagination(**page.model_dump())

        count = campaignCRUD.count_has_pending_job(db, **count_pagination.model_dump())
        if count < multi_paigination.skip:
            return [], count

        return (
            campaignCRUD.get_has_pending_job(db, **multi_paigination.model_dump()),
            count,
        )


campaign_helper = CampaignHelper()
