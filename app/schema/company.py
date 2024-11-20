from pydantic import BaseModel, validator, ConfigDict
from fastapi import UploadFile
from typing import Optional, List

from app.hepler.enum import CompanyType
from app.schema.page import Pagination
from app.hepler.schema_validator import SchemaValidator
from app.schema.field import FieldItemResponse


class CompanyBase(BaseModel):
    name: str
    email: str
    phone_number: str
    is_premium: bool = False
    website: Optional[str] = None
    address: str
    company_short_description: Optional[str] = None
    scale: str
    tax_code: str
    type: CompanyType

    model_config = ConfigDict(from_attribute=True, extra="ignore")

    @validator("name")
    def validate_name(cls, v):
        return SchemaValidator.validate_company_name(v)

    @validator("email")
    def validate_email(cls, v):
        return SchemaValidator.validate_email(v)

    @validator("phone_number")
    def validate_phone_number(cls, v):
        return SchemaValidator.validate_phone_number(v)


# request


class CompanyPagination(Pagination):
    fields: Optional[List[int]] = None
    business_id: Optional[int] = None
    keyword: Optional[str] = None


class CompanyCreateRequest(CompanyBase):
    fields: List
    logo: Optional[UploadFile] = None

    @validator("logo")
    def validate_logo(cls, v):
        return SchemaValidator.validate_logo_upload_file(v)

    @validator("company_short_description")
    def validate_company_short_description(cls, v):
        return SchemaValidator.validate_json_dumps(v)

    @validator("fields")
    def validate_fields(cls, v):
        return SchemaValidator.validate_fields(v)


class CompanyCreate(CompanyBase):
    logo: Optional[str] = None
    business_id: int


class CompanyUpdateRequest(BaseModel):
    company_id: int
    email: Optional[str] = None
    phone_number: Optional[str] = None
    is_premium: Optional[bool] = None
    label: Optional[str] = None
    logo: Optional[UploadFile] = None
    website: Optional[str] = None
    address: Optional[str] = None
    type: Optional[CompanyType] = None
    company_short_description: Optional[str] = None
    scale: Optional[str] = None
    tax_code: Optional[str] = None
    fields: Optional[List] = None

    @validator("email")
    def validate_email(cls, v):
        return SchemaValidator.validate_email(v)

    @validator("phone_number")
    def validate_phone_number(cls, v):
        return SchemaValidator.validate_phone_number(v)

    @validator("logo")
    def validate_logo(cls, v):
        return SchemaValidator.validate_logo_upload_file(v)

    @validator("company_short_description")
    def validate_company_short_description(cls, v):
        return SchemaValidator.validate_json_dumps(v)


class CompanyUpdate(BaseModel):
    company_id: int
    email: Optional[str] = None
    phone_number: Optional[str] = None
    is_premium: Optional[bool] = None
    label: Optional[str] = None
    logo: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    type: Optional[CompanyType] = None
    company_short_description: Optional[str] = None
    scale: Optional[str] = None
    tax_code: Optional[str] = None
    business_id: Optional[int] = None

    @validator("email")
    def validate_email(cls, v):
        return SchemaValidator.validate_email(v)

    @validator("phone_number")
    def validate_phone_number(cls, v):
        return SchemaValidator.validate_phone_number(v)


# response


class CompanyItemGeneralResponse(BaseModel):
    id: int
    name: str
    type: CompanyType
    phone_number: str
    email: str
    company_short_description: Optional[str] = None
    is_premium: bool
    label: Optional[object] = None
    logo: Optional[str] = None
    website: Optional[str] = None
    address: str
    scale: str
    is_verified: bool
    total_active_jobs: int = None
    tax_code: str
    banner: Optional[str] = None

    @validator("logo")
    def validate_logo(cls, v):
        return SchemaValidator.validate_logo(v)

    @validator("banner")
    def validate_banner(cls, v):
        return SchemaValidator.validate_logo(v)

    @validator("company_short_description")
    def validate_company_short_description(cls, v):
        return SchemaValidator.validate_json_loads(v)


class CompanyItemResponse(CompanyItemGeneralResponse):
    fields: List[FieldItemResponse]


class CompanyItemDetailSearchResponse(CompanyItemResponse):
    total_active_jobs: int


class CompanyPrivateResponse(BaseModel):
    id: int
    name: str
    email: str
    type: CompanyType
    phone_number: str
    is_premium: bool
    label: Optional[object] = None
    logo: Optional[str] = None
    description: Optional[str] = None
    company_short_description: Optional[str] = None
    website: Optional[str] = None
    address: str
    company_short_description: Optional[str] = None
    scale: str
    tax_code: str
    is_verified: bool
    total_active_jobs: int = 0
    banner: Optional[str] = None
    fields: List[FieldItemResponse]

    model_config = ConfigDict(from_attribute=True, extra="ignore")

    @validator("logo")
    def validate_logo(cls, v):
        return SchemaValidator.validate_logo(v)

    @validator("company_short_description")
    def validate_company_short_description(cls, v):
        return SchemaValidator.validate_json_loads(v)

    @validator("banner")
    def validate_banner(cls, v):
        return SchemaValidator.validate_logo(v)


class CompanyJobResponse(CompanyBase):
    id: int
    name: str
    logo: Optional[str] = None

    @validator("logo")
    def validate_logo(cls, v):
        return SchemaValidator.validate_logo(v)

    @validator("company_short_description")
    def validate_company_short_description(cls, v):
        return SchemaValidator.validate_json_loads(v)
