from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProvinceBase(BaseModel):
    name: str
    code: str
    name_with_type: str
    slug: str
    type: str
    country: Optional[str] = None

    model_config = ConfigDict(from_attribute=True, extra="ignore")


# request
class ProvinceCreateRequest(ProvinceBase):
    pass


class ProvinceUpdateRequest(ProvinceBase):
    name: Optional[str] = None
    code: Optional[str] = None
    name_with_type: Optional[str] = None
    slug: Optional[str] = None
    type: Optional[str] = None
    country: Optional[str] = None


# schema
class ProvinceCreate(ProvinceBase):
    pass


class ProvinceUpdate(ProvinceBase):
    name: Optional[str] = None
    code: Optional[str] = None
    name_with_type: Optional[str] = None
    slug: Optional[str] = None
    type: Optional[str] = None
    country: Optional[str] = None


# response
class ProvinceItemResponse(ProvinceBase):
    id: int
