from pydantic import BaseModel, validator, ConfigDict
from fastapi import UploadFile
from typing import Optional, Any
from datetime import datetime

from app.hepler.enum import Role, Gender, TypeAccount
from app.hepler.schema_validator import SchemaValidator
from app.schema.province import ProvinceItemResponse
from app.schema.district import DistrictItemResponse
from app.schema.company import CompanyItemResponse, CompanyItemGeneralResponse


# request
class BusinessUpdateRequest(BaseModel):
    phone_number: Optional[str] = None
    gender: Optional[Gender] = None
    company_name: Optional[str] = None
    work_position: Optional[str] = None
    work_location: Optional[str] = None
    province_id: Optional[int] = None
    district_id: Optional[int] = None
    avatar: Optional[UploadFile] = None
    full_name: Optional[str] = None

    @validator("phone_number")
    def validate_phone_number(cls, v):
        return SchemaValidator.validate_phone_number(v)

    @validator("gender")
    def validate_gender(cls, v):
        return SchemaValidator.validate_gender(v)

    @validator("avatar")
    def validate_avatar(cls, v):
        return SchemaValidator.validate_avatar_upload_file(v)

    @validator("full_name")
    def validate_full_name(cls, v):
        return SchemaValidator.validate_full_name(v)


class BusinessGetByEmailRequest(BaseModel):
    email: str

    @validator("email")
    def validate_email(cls, v):
        return SchemaValidator.validate_email(v)


class BusinessCreateRequest(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attribute=True)

    province_id: int
    district_id: Optional[int] = None
    phone_number: str
    gender: str
    company_name: str
    work_position: str
    work_location: Optional[str] = None
    role: Role = Role.BUSINESS
    type_account: TypeAccount = TypeAccount.BUSINESS
    avatar: Optional[UploadFile] = None
    full_name: str
    email: str
    password: str
    confirm_password: str

    @validator("phone_number")
    def validate_phone_number(cls, v):
        return SchemaValidator.validate_phone_number(v)

    @validator("gender")
    def validate_gender(cls, v):
        return SchemaValidator.validate_gender(v)

    @validator("company_name")
    def validate_company_name(cls, v):
        return SchemaValidator.validate_company_name(v)

    @validator("role")
    def validate_role(cls, v):
        return Role.BUSINESS

    @validator("type_account")
    def validate_type_account(cls, v):
        return TypeAccount.BUSINESS

    @validator("avatar")
    def validate_avatar(cls, v):
        return SchemaValidator.validate_avatar_upload_file(v)

    @validator("full_name")
    def validate_full_name(cls, v):
        return SchemaValidator.validate_full_name(v)

    @validator("email")
    def validate_email(cls, v):
        return SchemaValidator.validate_email(v)

    @validator("password")
    def validate_password(cls, v):
        return SchemaValidator.validate_password(v)

    @validator("confirm_password")
    def validate_confirm_password(cls, v, values):
        return SchemaValidator.validate_confirm_password(v, values)


# schema
class BusinessCreate(BaseModel):
    id: int
    province_id: int
    district_id: Optional[int] = None
    gender: Optional[Gender] = None
    company_name: str
    work_position: str
    work_location: Optional[str] = None


class BusinessUpdate(BaseModel):
    phone_number: Optional[str] = None
    gender: Optional[Gender] = None
    company_name: Optional[str] = None
    work_position: Optional[str] = None
    work_location: Optional[str] = None
    province_id: Optional[int] = None
    district_id: Optional[int] = None
    avatar: Optional[str] = None
    full_name: Optional[str] = None


# response
class BusinessItemResponse(BaseModel):
    model_config = ConfigDict(extra="ignore", from_attribute=True)

    id: int
    full_name: str
    email: str
    phone_number: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool
    role: Role
    work_location: Optional[str] = None
    work_position: str
    province: Optional[ProvinceItemResponse] = None
    district: Optional[DistrictItemResponse] = None
    company: Optional[CompanyItemResponse] = None
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_verified_email: bool
    is_verified_phone: bool
    is_verified_company: bool
    is_verified_identity: bool

    @validator("avatar")
    def validate_avatar(cls, v):
        return SchemaValidator.validate_avatar_url(v)


class BusinessBasicInfoResponse(BaseModel):
    id: int
    full_name: str
    avatar: Optional[str] = None
    role: Role
    type_account: TypeAccount
    nickname: Optional[str] = None
    work_position: str
    company: Optional[CompanyItemGeneralResponse] = None
    last_login: Optional[datetime] = None

    @validator("avatar")
    def validate_avatar(cls, v):
        return SchemaValidator.validate_avatar_url(v)
