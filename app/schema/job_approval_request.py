from pydantic import BaseModel, ConfigDict, validator
from typing import Optional, List, Any, Union
from datetime import datetime, date
import json
import re

from app.schema.page import Pagination
from app.hepler.enum import (
    SalaryType,
    JobType,
    Gender,
    JobApprovalStatus,
)
from app.hepler.schema_validator import SchemaValidator


class JobApprovalRequestBase(BaseModel):
    model_config = ConfigDict(from_attribute=True, extra="ignore")

    job_id: int
    status: Optional[JobApprovalStatus] = None


# request
class JobApprovalRequestList(Pagination):
    status: Optional[JobApprovalStatus] = None
    company_id: Optional[int] = None
    business_id: Optional[int] = None


class JobApprovalFilter(Pagination):
    status: Optional[JobApprovalStatus] = None
    job_id: Optional[int] = None


# schema
class JobApprovalCreate(BaseModel):
    job_id: int
    status: JobApprovalStatus = JobApprovalStatus.PENDING
    data: Optional[Any] = None


class JobApprovalRequestCreate(BaseModel):
    title: Optional[str] = None
    max_salary: Optional[int] = None
    min_salary: Optional[int] = None
    salary_type: SalaryType = None
    job_description: Optional[str] = None
    job_requirement: Optional[str] = None
    job_benefit: Optional[str] = None
    phone_number_contact: Optional[str] = None
    email_contact: Optional[Any] = None
    full_name_contact: Optional[str] = None
    employment_type: JobType = None
    gender_requirement: Gender = None
    deadline: Optional[date] = None
    is_featured: Optional[bool] = False
    is_highlight: Optional[bool] = False
    is_urgent: Optional[bool] = False
    is_paid_featured: Optional[bool] = False
    is_bg_featured: Optional[bool] = False
    is_job_flash: Optional[bool] = False
    working_time_text: Optional[str] = None
    quantity: Optional[int] = None
    working_times: Optional[Any] = None
    categories: Optional[Any] = None
    work_locations: Optional[Any] = None
    must_have_skills: Optional[Any] = None
    should_have_skills: Optional[Any] = None
    job_experience_id: Optional[int] = None
    job_position_id: Optional[int] = None
    job_id: Optional[int] = None

    @validator("working_times")
    def validate_working_times(cls, v):
        return SchemaValidator.validate_json_dumps_list(v)

    @validator("categories")
    def validate_categories(cls, v):
        return SchemaValidator.validate_json_dumps_list(v)

    @validator("work_locations")
    def validate_work_locations(cls, v):
        return SchemaValidator.validate_json_dumps_list(v)

    @validator("must_have_skills")
    def validate_must_have_skills(cls, v):
        return SchemaValidator.validate_json_dumps_list(v)

    @validator("should_have_skills")
    def validate_should_have_skills(cls, v):
        return SchemaValidator.validate_json_dumps_list(v)

    @validator("email_contact")
    def validate_email_contact(cls, v):
        return SchemaValidator.validate_email_contact(set(v))


class JobApprovalRequestUpdate(JobApprovalRequestBase):
    pass


# response
class JobApprovalRequestResponse(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    max_salary: Optional[int] = None
    min_salary: Optional[int] = None
    salary_type: SalaryType = None
    job_description: Optional[str] = None
    job_requirement: Optional[str] = None
    job_benefit: Optional[str] = None
    phone_number_contact: Optional[str] = None
    email_contact: Optional[str] = None
    full_name_contact: Optional[str] = None
    employment_type: JobType = None
    gender_requirement: Gender = None
    deadline: Optional[date] = None
    is_featured: Optional[bool] = None
    is_highlight: Optional[bool] = None
    is_urgent: Optional[bool] = None
    is_paid_featured: Optional[bool] = None
    is_bg_featured: Optional[bool] = None
    is_job_flash: Optional[bool] = None
    working_time_text: Optional[str] = None
    quantity: Optional[int] = None
    working_times: Optional[Any] = None
    categories: Optional[Any] = None
    work_locations: Optional[Any] = None
    must_have_skills: Optional[Any] = None
    should_have_skills: Optional[Any] = None
    job_experience_id: Optional[int] = None
    job_position_id: Optional[int] = None
    job_id: Optional[int] = None

    @validator("working_times")
    def validate_working_times(cls, v):
        return SchemaValidator.validate_json_loads(v)

    @validator("categories")
    def validate_categories(cls, v):
        return SchemaValidator.validate_json_loads(v)

    @validator("work_locations")
    def validate_locations(cls, v):
        return SchemaValidator.validate_json_loads(v)

    @validator("must_have_skills")
    def validate_must_have_skills(cls, v):
        return SchemaValidator.validate_json_loads(v)

    @validator("should_have_skills")
    def validate_should_have_skills(cls, v):
        return SchemaValidator.validate_json_loads(v)

    @validator("email_contact")
    def validate_email_contact(cls, v):
        return SchemaValidator.validate_json_loads(v)

    @validator("job_description")
    def validate_job_description(cls, v):
        return SchemaValidator.validate_json_loads(v)

    @validator("job_requirement")
    def validate_job_requirement(cls, v):
        return SchemaValidator.validate_json_loads(v)

    @validator("job_benefit")
    def validate_job_benefit(cls, v):
        return SchemaValidator.validate_json_loads(v)
