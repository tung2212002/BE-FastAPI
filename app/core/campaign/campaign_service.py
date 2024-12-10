from fastapi import status
from sqlalchemy.orm import Session

from app.crud.campaign import campaign as campaignCRUD
from app.crud.company import company as companyCRUD
from app.core.auth.business_auth_helper import business_auth_helper
from app.schema.campaign import (
    CampaignGetListPagination,
    CampaignCreateRequest,
    CampaignUpdateRequest,
)
from app.hepler.enum import Role, FilterCampaign
from app.model import Manager, Account, Business, Company, Campaign
from app.core.campaign.campaign_helper import campaign_helper
from app.common.exception import CustomException
from app.common.response import CustomResponse


filter_functions = {
    None: lambda db, page: campaign_helper.get_list_campaign(db, page),
    FilterCampaign.ONLY_OPEN: lambda db, page: campaign_helper.get_list_campaign_open(
        db, page
    ),
    FilterCampaign.HAS_NEW_CV: lambda db, page: campaign_helper.get_list_campaign_has_new_application(
        db, page
    ),
    FilterCampaign.HAS_PUBLISHING_JOB: lambda db, page: campaign_helper.get_list_campaign_has_published_job(
        db, page
    ),
    FilterCampaign.EXPIRED_JOB: lambda db, page: campaign_helper.get_list_campaign_has_published_job_expired(
        db, page
    ),
    FilterCampaign.WAITING_APPROVAL_JOB: lambda db, page: campaign_helper.get_list_campaign_has_pending_job(
        db, page
    ),
    FilterCampaign.EMPTY_JOB: lambda db, page: campaign_helper.get_list_campaign_empty_job(
        db, page
    ),
}

from datetime import datetime


class CampaignService:
    async def get(self, db: Session, data: dict, current_user: Account):
        page = CampaignGetListPagination(**data)

        campaigns = []
        count = 0
        business_id = page.business_id

        role = business_auth_helper.check_permission_business(
            current_user,
            roles=[Role.BUSINESS, Role.ADMIN, Role.SUPER_USER],
            business_id=business_id,
        )
        if role == Role.BUSINESS:
            manager: Manager = current_user.manager
            business: Business = manager.business
            company: Company = business.company
            if not company:
                raise CustomException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    msg="Business not join any company",
                )

            if (business_id and business_id != business.id) or (
                page.company_id
                and (page.company_id != company.id)
                or (page.company_id and page.company_id != company.id)
            ):
                raise CustomException(
                    status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
                )

            page.business_id = business_id
            page.company_id = company.id
            campaigns, count = filter_functions.get(page.filter_by)(db, page)
        else:
            campaigns, count = filter_functions.get(page.filter_by)(db, page)

        campaigns_response = [
            campaign_helper.get_info(db, campaign) for campaign in campaigns
        ]

        return CustomResponse(data={"count": count, "campaigns": campaigns_response})

    async def get_list(self, db: Session, data: dict):
        page = CampaignGetListPagination(**data)

        campaigns = filter_functions.get(page.filter_by)(db, page)
        response = [campaign_helper.get_info(db, campaign) for campaign in campaigns]

        return CustomResponse(data={"campaigns": response})

    async def get_by_id(self, db: Session, campaign_id: int, current_user: Account):
        campaign = campaignCRUD.get(db, campaign_id)
        if not campaign:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Campaign not found"
            )

        company = companyCRUD.get_by_business_id(db, current_user.id)
        if current_user.role == Role.BUSINESS and (
            campaign.business_id != current_user.id
            or not company
            or campaign.company_id != company.id
        ):
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
            )

        response = campaign_helper.get_info(db, campaign)

        return CustomResponse(data=response)

    async def create(self, db: Session, data: dict, current_user: Account):
        campaign_data = CampaignCreateRequest(**data)

        if current_user.role == Role.BUSINESS:
            manager: Manager = current_user.manager
            business: Business = manager.business
            company: Company = business.company
            if not company:
                raise CustomException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    msg="Business not join any company",
                )

            campaign_data = {
                **campaign_data.model_dump(),
                "business_id": business.id,
                "company_id": company.id,
            }
        campaign = campaignCRUD.create(db, obj_in=campaign_data)
        response = campaign_helper.get_info(db, campaign)

        return CustomResponse(status_code=status.HTTP_201_CREATED, data=response)

    async def update(self, db: Session, data: dict, current_user: Account):
        campaign_id = data.get("id")
        campaign = campaignCRUD.get(db, campaign_id)
        company = companyCRUD.get_by_business_id(db, current_user.id)
        if not campaign:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Campaign not found"
            )

        if current_user.role == Role.BUSINESS and (
            campaign.business_id != current_user.id
            or not company
            or company.id != campaign.company_id
        ):
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
            )

        campaign_data = CampaignUpdateRequest(**data)

        campaign = campaignCRUD.update(db, db_obj=campaign, obj_in=campaign_data)
        response = campaign_helper.get_info(db, campaign)

        return CustomResponse(data=response)

    async def delete(self, db: Session, id: int, current_user: Account):
        campaign = campaignCRUD.get(db, id)
        company = companyCRUD.get_by_business_id(db, current_user.id)
        if not campaign:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Campaign not found"
            )

        if current_user.role == Role.BUSINESS and (
            campaign.business_id != current_user.id
            or not company
            or company.id != campaign.company_id
        ):
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
            )

        campaign = campaignCRUD.remove(db, id=id)

        return CustomResponse(msg="Campaign has been deleted")


campaign_service = CampaignService()
