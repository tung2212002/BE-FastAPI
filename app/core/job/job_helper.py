from sqlalchemy.orm import Session
from redis.asyncio import Redis
from typing import Union, List
from fastapi import status

from app.schema.job import (
    JobItemResponse,
    JobBusinessItemResponse,
    JobItemResponseGeneral,
    JobSearchByUser,
)
from app.schema.job import CVApplicationInfoResponse, JobUpdate, JobUpdateRequest
from app.schema.job_approval_request import (
    JobApprovalRequestResponse,
    JobApprovalRequestCreate,
)
from app.schema.job_approval_log import JobApprovalLogResponse, JobApprovalLogCreate
from app.crud import (
    job as jobCRUD,
    company as companyCRUD,
    cv_applications as cv_applicationCRUD,
    job_approval_request as job_approval_requestCRUD,
)
from app.schema.user import UserBasicResponse
from app.core.working_times.working_times_helper import working_times_helper
from app.storage.cache.job_cache_service import job_cache_service
from app.model import (
    Job,
    Account,
    CVApplication,
    JobApprovalRequest,
    Campaign,
    JobApprovalLog,
    Company,
)
from app.core.working_times.working_times_helper import working_times_helper
from app.core.expericence.expericence_helper import experience_helper
from app.core.user.user_helper import user_helper
from app.core.job_position.job_position_hepler import job_position_helper
from app.core.skill.skill_helper import skill_helper
from app.core.category.category_helper import category_helper
from app.core.work_locations.work_locations_hepler import work_location_helper
from app.core.job_approval_requests.job_approval_request_helper import (
    job_approval_request_helper,
)
from app.core.job_approval_log.job_approval_log_helper import job_approval_log_helper
from app.core.company.company_helper import company_helper
from app.hepler.enum import JobSkillType, JobStatus, JobApprovalStatus
from app.common.exception import CustomException
from app.common.response import CustomResponse


class JobHepler:
    async def get_list_job(self, db: Session, redis: Redis, data: dict):
        jobs = jobCRUD.get_multi(db, **data)
        jobs_response = []
        for job in jobs:
            job_res = await self.get_info(db, redis, job)
            if isinstance(job_res, dict):
                jobs_response.append(job_res) if job_res.get("company") else None
            else:
                jobs_response.append(job_res) if job_res.company else None

        return jobs_response

    async def get_list_job_info(
        self, db: Session, redis: Redis, jobs: List[Job]
    ) -> List[JobItemResponse]:
        return [await self.get_info(db, redis, job) for job in jobs]

    def check_fields(
        self,
        db: Session,
        *,
        must_have_skills: list,
        should_have_skills: list,
        locations: list,
        categories: list,
        working_times: list,
        experience_id: int,
        position_id: int,
    ):
        skill_helper.check_list_valid(db, must_have_skills)
        skill_helper.check_list_valid(db, should_have_skills)
        work_location_helper.check_list_valid(db, locations)
        category_helper.check_list_valid(db, categories)
        working_times_helper.check_list_valid(db, working_times)
        experience_helper.check_valid(db, experience_id)
        job_position_helper.check_valid(db, position_id)

    def update_fields(
        self,
        db: Session,
        job_id: int,
        *,
        must_have_skills: list,
        should_have_skills: list,
        locations: list,
        categories: list,
        working_times: list,
    ) -> None:
        skill_helper.update_with_job_id(
            db, job_id, must_have_skills, JobSkillType.MUST_HAVE
        )
        skill_helper.update_with_job_id(
            db, job_id, should_have_skills, JobSkillType.SHOULD_HAVE
        )
        work_location_helper.update_with_job_id(db, job_id, locations)
        category_helper.update_with_job_id(db, job_id, categories)
        working_times_helper.update_with_job_id(db, job_id, working_times)

    async def get_info(
        self, db: Session, redis: Redis, job: Job, Schema=JobItemResponse
    ) -> Union[JobItemResponse, dict]:
        job_id = job.id
        try:
            job_response: JobItemResponse = await job_cache_service.get_cache_job_info(
                redis, job_id
            )
            if job_response:
                return job_response
        except Exception as e:
            print(e)

        working_times_response = working_times_helper.get_by_job_id(db, job.id)
        work_locations_response = work_location_helper.get_by_job_id(db, job.id)
        company = companyCRUD.get_by_business_id(db, job.business_id)
        company_response = company_helper.get_info(db, company)
        categories_response = category_helper.get_list_info(job.job_categories)
        must_have_skills_response = skill_helper.get_list_info(job.must_have_skills)
        should_have_skills_response = skill_helper.get_list_info(job.should_have_skills)
        job_response = Schema(
            **{
                k: v
                for k, v in job.__dict__.items()
                if k
                not in [
                    "working_times",
                    "must_have_skills",
                    "should_have_skills",
                    "locations",
                    "job_categories",
                ]
            },
            working_times=working_times_response,
            locations=work_locations_response,
            company=company_response,
            categories=categories_response,
            must_have_skills=must_have_skills_response,
            should_have_skills=should_have_skills_response,
        )

        try:
            await job_cache_service.cache_job_info(redis, job_id, job_response)
        except Exception as e:
            print(e)
        return job_response

    async def get_info_business(
        self, db: Session, redis: Redis, job: Job
    ) -> JobBusinessItemResponse:
        job = await self.get_info(db, redis, job)
        job_approval_request = job_approval_request_helper.get_info_by_job_id(
            db, job.id
        )
        job_logs: List[JobApprovalLogResponse] = job_approval_log_helper.get_by_job_id(
            db, job.id
        )
        return JobBusinessItemResponse(
            **job.__dict__,
            job_logs=job_logs,
            last_approval_request=job_approval_request,
        )

    def get_info_general(self, job: Job) -> JobItemResponseGeneral:
        job_response = JobItemResponseGeneral(
            **job.__dict__,
        )
        return job_response

    def get_count_job_user_search_key(self, data: JobSearchByUser) -> str:
        return f"{data.province_id}_{data.district_id}_{data.province_id}_{data.category_id}_{data.field_id}_{data.employment_type}_{data.job_experience_id}_{data.job_position_id}_{data.min_salary}_{data.max_salary}_{data.salary_type}_{data.deadline}_{data.keyword}_{data.suggest}_{data.updated_at}"

    def search_job_user_search_key(self, data: JobSearchByUser) -> str:
        return f"{data.province_id}_{data.district_id}_{data.province_id}_{data.category_id}_{data.field_id}_{data.employment_type}_{data.job_experience_id}_{data.job_position_id}_{data.min_salary}_{data.max_salary}_{data.salary_type}_{data.deadline}_{data.keyword}_{data.suggest}_{data.updated_at}_{data.skip}_{data.limit}_{data.sort_by}_{data.order_by}"

    def create_fields(
        self,
        db: Session,
        job_id: int,
        must_have_skills: list,
        should_have_skills: list,
        locations: list,
        categories: list,
        working_times: list,
    ):
        skill_helper.create_with_job_id(
            db, job_id, must_have_skills, JobSkillType.MUST_HAVE
        )
        skill_helper.create_with_job_id(
            db, job_id, should_have_skills, JobSkillType.SHOULD_HAVE
        )
        work_location_helper.create_with_job_id(db, job_id, locations)
        category_helper.create_with_job_id(db, job_id, categories)
        working_times_helper.create_with_job_id(db, job_id, working_times)

    def get_info_with_cv_application(
        self, db: Session, job: JobItemResponse, account: Account
    ) -> JobItemResponse:
        cv_application: CVApplication = (
            cv_applicationCRUD.get_by_user_id_and_campaign_id(
                db, account.id, job.campaign_id
            )
        )

        if cv_application:
            user: UserBasicResponse = user_helper.get_basic_info_by_account(db, account)
            job.cv_application = CVApplicationInfoResponse(
                **cv_application.__dict__, user=user
            )
        return job

    def has_permission(
        self, job: Job, campaign: Campaign, company: Company, current_user: Account
    ) -> bool:
        return (
            job.business_id == current_user.id
            and company
            and campaign.business_id == current_user.id
            and campaign.company_id == company.id
        )

    def update_pending_job(
        self,
        db: Session,
        job: Job,
        job_data: JobUpdateRequest,
        job_approval_request: JobApprovalRequest,
    ):
        job_data_in = JobUpdate(**job_data.model_dump())
        jobCRUD.update(db, obj_in=job_data_in)
        self.update_job_fields(db, job.id, job_data)
        job_approval_requestCRUD.update_job(db, job_approval_request)

    def handle_rejected_job(self, db: Session, job: Job, job_data: JobUpdateRequest):
        job_data_in = JobUpdate(**job_data.model_dump(), status=JobStatus.PENDING)
        jobCRUD.update(db, obj_in=job_data_in)
        self.update_job_fields(db, job.id, job_data)
        self.create_job_approval_request(
            db, job, job_data, status=JobApprovalStatus.PENDING
        )

    def handle_stopped_job(
        self,
        db: Session,
        job: Job,
        job_data: JobUpdateRequest,
        job_approval_request: JobApprovalRequest,
    ):
        if job_approval_request.status == JobApprovalStatus.APPROVED:
            self.create_job_approval_request(
                db, job, job_data, status=JobApprovalStatus.PENDING
            )
        else:
            job_data_in = JobUpdate(**job_data.model_dump(), status=JobStatus.PENDING)
            jobCRUD.update(db, obj_in=job_data_in)
            self.update_job_fields(db, job.id, job_data)

    def update_job_fields(self, db: Session, job_id: int, job_data: JobUpdateRequest):
        self.update_fields(
            db,
            job_id=job_id,
            must_have_skills=job_data.must_have_skills,
            should_have_skills=job_data.should_have_skills,
            locations=job_data.locations,
            categories=job_data.categories,
            working_times=job_data.working_times,
        )

    def create_job_approval_request(
        self,
        db: Session,
        job: Job,
        job_data: JobUpdateRequest,
        status=JobApprovalStatus.PENDING,
    ):
        job_approval_request_in = JobApprovalRequestCreate(
            job_id=job.id,
            status=status,
            data=job_data.model_dump(),
        )
        job_approval_requestCRUD.create(db, obj_in=job_approval_request_in)


job_helper = JobHepler()
