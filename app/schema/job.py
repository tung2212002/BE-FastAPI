from pydantic import BaseModel, validator, ConfigDict
from typing import Optional, List, Any
from datetime import datetime, date

from app.hepler.enum import (
    SalaryType,
    JobStatus,
    JobType,
    Gender,
    JobApprovalStatus,
    SortByJob,
    OrderType,
    AdminJobApprovalStatus,
    CVApplicationStatus,
)
from app.hepler.schema_validator import SchemaValidator
from app.schema.skill import SkillItemResponse
from app.schema.category import CategoryItemResponse
from app.schema.working_time import WorkingTimeResponse
from app.schema.work_location import WorkLocatioResponse


class JobBase(BaseModel):
    campaign_id: Optional[int] = None
    title: Optional[str] = None
    max_salary: Optional[int] = 0
    min_salary: Optional[int] = 0
    salary_type: SalaryType = SalaryType.VND
    job_description: str
    job_requirement: str
    job_benefit: str
    phone_number_contact: str
    full_name_contact: str
    employment_type: JobType = JobType
    gender_requirement: Gender = Gender.OTHER
    deadline: date
    quantity: int = 1
    job_location: str
    working_time_text: Optional[str] = None
    job_position_id: int
    job_experience_id: int

    @validator("phone_number_contact")
    def validate_phone_number_contact(cls, v):
        return SchemaValidator.validate_phone_number(v)

    @validator("full_name_contact")
    def validate_full_name_contact(cls, v):
        return SchemaValidator.validate_full_name(v)

    model_config = ConfigDict(from_attribute=True, extra="ignore")


# request


class JobUpdateRequest(BaseModel):
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
    is_featured: Optional[bool] = None
    is_highlight: Optional[bool] = None
    is_urgent: Optional[bool] = None
    is_paid_featured: Optional[bool] = None
    is_bg_featured: Optional[bool] = None
    is_vip_employer: Optional[bool] = None
    is_diamond_employer: Optional[bool] = None
    is_job_flash: Optional[bool] = None
    employer_verified: Optional[bool] = None
    working_time_text: Optional[str] = None
    quantity: Optional[int] = None
    working_times: Optional[Any] = None
    categories: Optional[Any] = None
    locations: Optional[Any] = None
    must_have_skills: Optional[Any] = None
    should_have_skills: Optional[Any] = None
    job_experience_id: Optional[int] = None
    job_position_id: Optional[int] = None
    job_id: Optional[int] = None

    @validator("email_contact")
    def validate_email_contact(cls, v):
        return SchemaValidator.validate_email_contact(v)

    @validator("job_description")
    def validate_job_description(cls, v):
        return SchemaValidator.validate_json_dumps(v)

    @validator("job_requirement")
    def validate_job_requirement(cls, v):
        return SchemaValidator.validate_json_dumps(v)

    @validator("job_benefit")
    def validate_job_benefit(cls, v):
        return SchemaValidator.validate_json_dumps(v)

    @validator("working_times")
    def validate_working_times(cls, v):
        return SchemaValidator.validate_working_times(v)

    @validator("categories")
    def validate_categories(cls, v):
        return SchemaValidator.validate_categories(v)

    @validator("locations")
    def validate_locations(cls, v):
        return SchemaValidator.validate_locations(v)

    @validator("must_have_skills")
    def validate_must_have_skills(cls, v):
        return SchemaValidator.validate_skills(v)

    @validator("should_have_skills")
    def validate_should_have_skills(cls, v):
        return SchemaValidator.validate_skills(v)


class JobApproveRequest(BaseModel):
    job_approval_request_id: int
    status: AdminJobApprovalStatus
    reason: Optional[str] = None

    @validator("status")
    def validate_status(cls, v):
        return SchemaValidator.validate_status_update_job(v)


class JobApproveUpdateJobRequest(BaseModel):
    job_approval_request_id: int
    status: AdminJobApprovalStatus
    reason: Optional[str] = None

    @validator("status")
    def validate_status(cls, v):
        return SchemaValidator.validate_status_update_job(v)


class PaginationJob(BaseModel):
    skip: Optional[int] = 0
    limit: Optional[int] = 10
    sort_by: Optional[SortByJob] = SortByJob.CREATED_AT
    order_by: Optional[OrderType] = OrderType.DESC

    model_config = ConfigDict(from_attribute=True, extra="ignore")

    @validator("limit")
    def validate_limit(cls, v):
        return SchemaValidator.validate_limit(v)

    @validator("skip")
    def validate_skip(cls, v):
        return SchemaValidator.validate_skip(v)

    @validator("sort_by")
    def validate_sort_by(cls, v):
        return SchemaValidator.validate_job_sort_by(v)

    @validator("order_by")
    def validate_order_by(cls, v):
        return v or OrderType.DESC


class JobFilterByBusiness(PaginationJob):
    job_status: Optional[JobStatus] = None
    job_approve_status: Optional[JobApprovalStatus] = None
    business_id: Optional[int] = None
    company_id: Optional[int] = None
    campaign_id: Optional[int] = None


class JobFilterByUser(PaginationJob):
    job_status: Optional[JobStatus] = None
    job_approve_status: Optional[JobApprovalStatus] = None
    business_id: Optional[int] = None
    company_id: Optional[int] = None
    deadline: Optional[date] = datetime.now().date()
    province_id: Optional[int] = None


class JobCount(BaseModel):
    job_status: Optional[JobStatus] = JobStatus.PUBLISHED
    job_approve_status: Optional[JobApprovalStatus] = JobApprovalStatus.APPROVED
    business_id: Optional[int] = None
    company_id: Optional[int] = None
    province_id: Optional[int] = None
    district_id: Optional[int] = None
    category_id: Optional[int] = None
    field_id: Optional[int] = None
    employment_type: Optional[JobType] = None
    job_experience_id: Optional[int] = None
    job_position_id: Optional[int] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    salary_type: Optional[SalaryType] = None
    deadline: Optional[date] = datetime.now().date()
    keyword: Optional[str] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attribute=True, extra="ignore")

    @validator("job_status")
    def validate_job_status(cls, v):
        return v or JobStatus.PUBLISHED

    @validator("updated_at")
    def validate_updated_at(cls, v):
        return SchemaValidator.validate_job_updated_at(v)

    @validator("job_approve_status")
    def validate_job_approve_status(cls, v):
        return v or JobApprovalStatus.APPROVED

    @validator("deadline")
    def validate_deadline(cls, v):
        return v or datetime.now().date()


class JobSearchByUser(PaginationJob):
    job_status: Optional[JobStatus] = JobStatus.PUBLISHED
    business_id: Optional[int] = None
    company_id: Optional[int] = None
    province_id: Optional[int] = None
    district_id: Optional[int] = None
    category_id: Optional[int] = None
    field_id: Optional[int] = None
    employment_type: Optional[JobType] = None
    job_experience_id: Optional[int] = None
    job_position_id: Optional[int] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    salary_type: Optional[SalaryType] = None
    deadline: Optional[date] = datetime.now().date()
    keyword: Optional[str] = None
    suggest: Optional[bool] = False
    updated_at: Optional[Any] = None

    @validator("deadline")
    def validate_deadline(cls, v):
        return v or datetime.now().date()

    @validator("updated_at")
    def validate_updated_at(cls, v):
        return SchemaValidator.validate_job_updated_at(v)

    @validator("job_status")
    def validate_job_status(cls, v):
        return v or JobStatus.PUBLISHED

    def get_count_job_user_search_key(self):
        return f"{self.province_id}_{self.district_id}_{self.province_id}_{self.category_id}_{self.field_id}_{self.employment_type}_{self.job_experience_id}_{self.job_position_id}_{self.min_salary}_{self.max_salary}_{self.salary_type}_{self.deadline}_{self.keyword}_{self.suggest}_{self.updated_at}_{self.sort_by}_{self.order_by}_{self.skip}_{self.limit}"

    def get_jobs_of_district_key(self):
        return f"{self.province_id}_{self.district_id}_{self.province_id}_{self.category_id}_{self.field_id}_{self.employment_type}_{self.job_experience_id}_{self.job_position_id}_{self.min_salary}_{self.max_salary}_{self.salary_type}_{self.deadline}_{self.keyword}_{self.suggest}_{self.updated_at}"


class JobSearchByBusiness(PaginationJob):
    job_status: Optional[JobStatus] = JobStatus.PUBLISHED
    job_approve_status: Optional[JobApprovalStatus] = JobApprovalStatus.APPROVED
    business_id: Optional[int] = None
    company_id: Optional[int] = None
    province_id: Optional[int] = None
    district_id: Optional[int] = None
    category_id: Optional[int] = None
    field_id: Optional[int] = None
    employment_type: Optional[JobType] = None
    job_experience_id: Optional[int] = None
    job_position_id: Optional[int] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    salary_type: Optional[SalaryType] = None
    deadline: Optional[Any] = datetime.now().date()
    keyword: Optional[str] = None

    @validator("job_status")
    def validate_deadline(cls, v):
        return v or datetime.now().date()

    @validator("job_status")
    def validate_job_status(cls, v):
        return v or JobStatus.PUBLISHED

    @validator("job_approve_status")
    def validate_job_approve_status(cls, v):
        return v or JobApprovalStatus.APPROVED


class JobCreateRequest(JobBase):
    working_times: List[object] = []
    working_time_text: Optional[str] = None
    categories: List[int]
    locations: List[object]
    email_contact: List[str]
    must_have_skills: List[int]
    should_have_skills: List[int]

    @validator("email_contact")
    def validate_email_contact(cls, v):
        return SchemaValidator.validate_email_contact(v)

    @validator("job_description")
    def validate_job_description(cls, v):
        return SchemaValidator.validate_json_dumps(v)

    @validator("job_requirement")
    def validate_job_requirement(cls, v):
        return SchemaValidator.validate_json_dumps(v)

    @validator("job_benefit")
    def validate_job_benefit(cls, v):
        return SchemaValidator.validate_json_dumps(v)

    @validator("working_times")
    def validate_working_times(cls, v):
        return v or []

    @validator("deadline")
    def validate_deadline(cls, v):
        if v:
            if v < datetime.now().date():
                raise ValueError("Invalid deadline")
        return v


# schema


class JobCreate(JobBase):
    email_contact: str
    business_id: int
    campaign_id: int
    employer_verified: bool = False


class JobUpdate(BaseModel):
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
    is_vip_employer: Optional[bool] = None
    is_diamond_employer: Optional[bool] = None
    is_job_flash: Optional[bool] = None
    employer_verified: Optional[bool] = None
    working_time_text: Optional[str] = None
    quantity: Optional[int] = None
    locations: Optional[List[object]] = None


# response
class CVApplicationInfoResponse(BaseModel):
    id: int
    status: CVApplicationStatus
    full_name: str
    email: str
    phone_number: str
    letter_cover: Optional[str] = None
    created_at: datetime
    cv: str
    count_apply: int

    @validator("cv")
    def validate_cv(cls, v):
        return SchemaValidator.validate_cv_url(v)

    model_config = ConfigDict(from_attribute=True, extra="ignore")


class JobItemResponse(JobBase):
    id: int
    updated_at: Optional[datetime] = None
    created_at: datetime
    is_featured: bool = False
    is_highlight: bool = False
    is_urgent: bool = False
    is_paid_featured: bool = False
    is_bg_featured: bool = False
    is_vip_employer: bool = False
    is_diamond_employer: bool = False
    is_job_flash: bool = False
    employer_verified: bool = False
    is_new: bool = False
    is_hot: bool = False
    email_contact: Any
    status: JobStatus
    locations: List[object]
    categories: List[object]
    working_times: List[object]
    must_have_skills: List[object]
    should_have_skills: List[object]
    company: object
    cv_application: Optional[CVApplicationInfoResponse] = None

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


class JobItemResponseGeneral(BaseModel):
    id: int
    updated_at: Optional[datetime] = None
    created_at: datetime
    is_featured: bool = False
    is_highlight: bool = False
    is_urgent: bool = False
    is_paid_featured: bool = False
    is_bg_featured: bool = False
    is_vip_employer: bool = False
    is_diamond_employer: bool = False
    is_job_flash: bool = False
    employer_verified: bool = False
    is_new: bool = False
    is_hot: bool = False
    status: JobStatus
    campaign_id: Optional[int] = None
    title: Optional[str] = None
    phone_number_contact: str
    full_name_contact: str
    deadline: date
    max_salary: Optional[int] = 0
    min_salary: Optional[int] = 0
    salary_type: SalaryType = SalaryType.VND


class JobItemResponseUser(BaseModel):
    id: int
    updated_at: Optional[datetime] = None
    created_at: datetime
    is_featured: bool = False
    is_highlight: bool = False
    is_urgent: bool = False
    is_paid_featured: bool = False
    is_bg_featured: bool = False
    is_vip_employer: bool = False
    is_diamond_employer: bool = False
    is_job_flash: bool = False
    employer_verified: bool = False
    is_new: bool = False
    is_hot: bool = False
    locations: List[WorkLocatioResponse]
    categories: List[CategoryItemResponse]
    working_times: List[WorkingTimeResponse]
    must_have_skills: List[SkillItemResponse]
    should_have_skills: List[SkillItemResponse]
    company: object
    title: Optional[str] = None
    max_salary: Optional[int] = 0
    min_salary: Optional[int] = 0
    salary_type: SalaryType = SalaryType.VND
    job_description: str
    job_requirement: str
    job_benefit: str
    employment_type: JobType = JobType
    gender_requirement: Gender = Gender.OTHER
    deadline: date
    quantity: int = 1
    job_location: str
    working_time_text: Optional[str] = None
    job_position_id: int
    job_experience_id: int

    model_config = ConfigDict(from_attribute=True, extra="ignore")

    @validator("job_description")
    def validate_job_description(cls, v):
        return SchemaValidator.validate_json_loads(v)

    @validator("job_requirement")
    def validate_job_requirement(cls, v):
        return SchemaValidator.validate_json_loads(v)

    @validator("job_benefit")
    def validate_job_benefit(cls, v):
        return SchemaValidator.validate_json_loads(v)


class JobSearchResponseUser(BaseModel):
    id: int
    updated_at: Optional[datetime] = None
    is_featured: bool = False
    is_highlight: bool = False
    is_urgent: bool = False
    is_paid_featured: bool = False
    is_bg_featured: bool = False
    is_vip_employer: bool = False
    is_diamond_employer: bool = False
    is_job_flash: bool = False
    is_new: bool = False
    is_hot: bool = False
    locations: List[dict]
    company: object
    title: Optional[str] = None
    max_salary: Optional[int] = 0
    min_salary: Optional[int] = 0
    salary_type: SalaryType = SalaryType.VND
    deadline: date
    quantity: int = 1
    job_position_id: int
    job_experience_id: int

    model_config = ConfigDict(from_attribute=True, extra="ignore")
