from pydantic import BaseModel, ConfigDict, validator
from typing import Optional
from datetime import datetime

from app.hepler.enum import Role, TypeAccount
from app.hepler.schema_validator import SchemaValidator
from app.schema.company import CompanyItemGeneralResponse


class AccountCreate(BaseModel):
    full_name: str
    avatar: Optional[str] = None
    role: Role = Role.USER
    type_account: TypeAccount = TypeAccount.NORMAL

    @validator("role")
    def validate_role(cls, v):
        return v or Role.USER

    @validator("type_account")
    def validate_type_account(cls, v):
        return v or TypeAccount.NORMAL

    model_config = ConfigDict(from_attribute=True, extra="ignore")


class AccountUpdate(BaseModel):
    full_name: str
    avatar: Optional[str] = None

    model_config = ConfigDict(from_attribute=True, extra="ignore")


# response
class AccountBasicResponse(BaseModel):
    id: int
    full_name: str
    email: str
    avatar: Optional[str] = None
    role: Role
    type_account: TypeAccount
    last_login: Optional[datetime] = None
    company: Optional[CompanyItemGeneralResponse] = None

    @validator("avatar")
    def validate_avatar(cls, v):
        return SchemaValidator.validate_avatar_url(v)

    model_config = ConfigDict(from_attribute=True, extra="ignore")
