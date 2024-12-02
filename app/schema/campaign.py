from pydantic import BaseModel, validator, ConfigDict
from typing import Optional, List
from datetime import datetime

from app.hepler.enum import CampaignStatus, FilterCampaign
from app.schema.page import Pagination
from app.schema.business import BusinessBasicInfoResponse
from app.schema.company import CompanyItemGeneralResponse
from app.hepler.schema_validator import SchemaValidator
from app.schema.job import CVApplicationInfoResponse


class CampaignBase(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attribute=True)

    title: str
    is_flash: Optional[bool] = False

    @validator("title")
    def validate_title(cls, v):
        return SchemaValidator.validate_title(v)


# request
class CampaignCreateRequest(CampaignBase):
    pass


class CampaignUpdateRequest(CampaignBase):
    status: Optional[str] = CampaignStatus.OPEN
    optimal_score: Optional[int] = 0
    id: int

    @validator("status")
    def validate_status(cls, v):
        return SchemaValidator.validate_campaign_status(v)

    @validator("optimal_score")
    def validate_optimal_score(cls, v):
        return v or 0


class CampaignGetListPagination(Pagination):
    # business_id: Optional[int] = None
    # company_id: Optional[int] = None
    # status: Optional[CampaignStatus] = None

    # @validator("status")
    # def validate_status(cls, v):
    #     if v and not v in CampaignStatus.__members__.values():
    #         raise ValueError("Invalid status")
    #     return v
    business_id: Optional[int] = None
    company_id: Optional[int] = None
    filter_by: Optional[FilterCampaign] = None

    @validator("filter_by")
    def validate_filter(cls, v):
        return SchemaValidator.validate_filter_campaign(v)


class CampaignFilterListPagination(Pagination):
    business_id: Optional[int] = None
    company_id: Optional[int] = None
    filter_by: Optional[FilterCampaign] = None

    @validator("filter_by")
    def validate_filter(cls, v):
        return SchemaValidator.validate_filter_campaign(v)


class CampaignGetOnlyOpenPagination(Pagination):
    business_id: Optional[int] = None
    company_id: Optional[int] = None


class CampaignGetHasNewApplicationPagination(Pagination):
    business_id: Optional[int] = None
    company_id: Optional[int] = None


class CampaignGetHasPublishedJobPagination(Pagination):
    business_id: Optional[int] = None
    company_id: Optional[int] = None


class CampaignGetHasPublishedJobExpiredPagination(Pagination):
    business_id: Optional[int] = None
    company_id: Optional[int] = None


class CampaignGetHasPendingJobPagination(CampaignGetHasNewApplicationPagination):
    pass


class CampaignGetMutilPagination(Pagination):
    business_id: Optional[int] = None
    company_id: Optional[int] = None
    status: Optional[CampaignStatus] = None


class CountGetListPagination(BaseModel):
    business_id: Optional[int] = None
    company_id: Optional[int] = None
    status: Optional[CampaignStatus] = None


class CountGetListStatusPagination(BaseModel):
    business_id: Optional[int] = None
    company_id: Optional[int] = None


# schema
class CampaignCreate(CampaignBase):
    business_id: int


class CampaignUpdate(CampaignBase):
    status: Optional[str] = CampaignStatus.OPEN
    optimal_score: Optional[int] = 0
    id: int

    @validator("status")
    def validate_status(cls, v):
        return SchemaValidator.validate_campaign_status(v)

    @validator("optimal_score")
    def validate_optimal_score(cls, v):
        return v or 0


# response
class CampaignItemResponse(CampaignBase):
    id: int
    created_at: datetime
    updated_at: datetime
    status: Optional[CampaignStatus] = CampaignStatus.OPEN
    optimal_score: Optional[int] = 0
    job: Optional[dict] = None
    count_apply: Optional[int] = 0
    latest_cvs: Optional[List[CVApplicationInfoResponse]] = []
    business: Optional[BusinessBasicInfoResponse] = None
    company: Optional[CompanyItemGeneralResponse] = None

    @validator("status")
    def validate_status(cls, v):
        return v or CampaignStatus.OPEN

    @validator("optimal_score")
    def validate_optimal_score(cls, v):
        return v or 0
