from fastapi import status
from sqlalchemy.orm import Session
from datetime import timedelta
from redis.asyncio import Redis

from app.schema.job import (
    JobCreate,
    JobUpdate,
    JobCreateRequest,
    JobUpdateRequest,
    JobFilterByBusiness,
    JobFilterByUser,
    JobSearchByUser,
    JobSearchByBusiness,
    JobCount,
    JobItemResponse,
)
from app.schema.job_approval_request import (
    JobApprovalRequestCreate,
    JobApprovalRequestResponse,
)
from app.schema.job_statistics import JobCountBySalary
from app.crud import (
    job as jobCRUD,
    company as companyCRUD,
    job_approval_request as job_approval_requestCRUD,
    campaign as campaignCRUD,
    cv_applications as cv_applicationCRUD,
    work_market as work_marketCRUD,
)
from app.core import constant
from app.hepler.enum import (
    Role,
    JobStatus,
    SalaryType,
    JobApprovalStatus,
    CampaignStatus,
    RequestApproval,
)
from app.core.job_approval_requests import job_approval_request_helper
from app.storage.cache.job_cache_service import job_cache_service
from app.hepler.common import CommonHelper
from app.model import (
    Manager,
    Account,
    Business,
    Company,
    Job,
    CVApplication,
    WorkMarket,
)
from app.core.location.location_helper import location_helper
from app.core.job.job_helper import job_helper
from app.core.category.category_helper import category_helper
from app.core.auth.business_auth_helper import business_auth_helper
from app.core.campaign.campaign_helper import campaign_helper
from app.core.cv_applications.cv_applications_helper import cv_applications_helper
from app.core.job_approval_requests.job_approval_request_helper import (
    job_approval_request_helper,
)

from app.common.exception import CustomException
from app.common.response import CustomResponse


class JobService:
    async def get_by_business(
        self, db: Session, redis: Redis, data: dict, current_user: Account
    ):
        page = JobFilterByBusiness(**data)

        if current_user.role == Role.BUSINESS:
            if page.business_id and page.business_id != current_user.id:
                raise CustomException(
                    status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
                )

            page.business_id = current_user.id
            company = companyCRUD.get_by_business_id(db, current_user.id)
            if not company:
                raise CustomException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    msg="Business not join company",
                )

            if page.company_id and page.company_id != company.id:
                raise CustomException(
                    status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
                )

            page.company_id = company.id
        response = await job_helper.get_list_job(db, redis, page.model_dump())

        return CustomResponse(data=response)

    async def get_by_user(
        self, db: Session, redis: Redis, data: dict, current_user: Account
    ):
        page = JobFilterByUser(**data)
        page.job_status = JobStatus.PUBLISHED
        page.job_approve_status = JobApprovalStatus.APPROVED

        jobs = await job_helper.get_list_job(db, redis, page.model_dump())

        params = JobCount(**data)
        number_of_all_jobs = jobCRUD.count(db, **params.model_dump())

        response = {
            "count": number_of_all_jobs,
            "jobs": jobs,
        }

        return CustomResponse(data=response)

    async def search_by_user(
        self, db: Session, redis: Redis, data: dict, current_user: Account
    ):
        page = JobSearchByUser(**data)
        page.job_status = JobStatus.PUBLISHED
        jobs = None
        count = 0
        jobs_of_district_response = []

        try:
            jobs = await job_cache_service.get_cache_user_search(
                redis, page.get_count_job_user_search_key()
            )
        except Exception as e:
            print(e)

        if not jobs:
            jobs = jobCRUD.user_search(db, **page.model_dump())
            jobs = await job_helper.get_list_job_info(db, redis, jobs)
            try:
                await job_cache_service.cache_user_search(
                    redis, page.get_count_job_user_search_key(), jobs
                )
            except Exception as e:
                print(e)

        if (page.province_id or page.district_id) and page.suggest:
            try:
                cache_key = page.get_jobs_of_district_key()
                jobs_of_district_response = await job_cache_service.get_list(
                    redis, cache_key
                )
            except Exception as e:
                print(e)

            if not jobs_of_district_response:
                jobs_of_district = jobCRUD.get_number_job_of_district(
                    db, **page.model_dump()
                )
                jobs_of_district_response = []
                for key, value in jobs_of_district:
                    count += value
                    if value > 0 and key is not None:
                        district = location_helper.get_district_info(db, key)
                        jobs_of_district_response.append(
                            {
                                "district": district,
                                "count": value,
                            }
                        )
                try:
                    await job_cache_service.cache_province_district_search_by_user(
                        redis,
                        cache_key,
                        [
                            {
                                "district": jobs_of_district_data["district"].__dict__,
                                "count": jobs_of_district_data["count"],
                            }
                            for jobs_of_district_data in jobs_of_district_response
                        ],
                    )
                except Exception as e:
                    print(e)

        else:
            cache_key = page.get_count_job_user_search_key()
            count = None
            try:
                count = await job_cache_service.get_cache_count_search_by_user(
                    redis, cache_key
                )
            except Exception as e:
                print(e)

            if not count:
                params = JobCount(**data)
                count = jobCRUD.user_count(db, **params.model_dump())
                try:
                    await job_cache_service.cache_count_search_by_user(
                        redis, cache_key, count
                    )
                except Exception as e:
                    print(e)
        jobs_response = []
        if current_user:
            for job in jobs:
                jobs_response.append(
                    job_helper.get_info_with_cv_application(db, job, current_user)
                )
        else:
            jobs_response = jobs

        response = {
            "count": count,
            "option": page,
            "jobs": jobs_response,
            "jobs_of_district": jobs_of_district_response,
        }

        return CustomResponse(data=response)

    async def search_by_business(
        self, db: Session, redis: Redis, current_user: Account, data: dict
    ):
        page = JobSearchByBusiness(**data)

        if current_user.role == Role.BUSINESS:
            if page.business_id and page.business_id != current_user.id:
                raise CustomException(
                    status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
                )

            page.business_id = current_user.id
            company = companyCRUD.get_by_business_id(db, current_user.id)
            if not company:
                raise CustomException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    msg="Business not join company",
                )

            if page.company_id and page.company_id != company.id:
                raise CustomException(
                    status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
                )
            page.company_id = company.id

        jobs = jobCRUD.search(db, **page.model_dump())
        params = JobCount(**page.model_dump())
        count = jobCRUD.count(db, **params.model_dump())

        jobs_response = []
        for job in jobs:
            job_res = await job_helper.get_info(db, redis, job)
            if isinstance(job_res, dict):
                jobs_response.append(job_res) if job_res.get("company") else None
            else:
                jobs_response.append(job_res) if job_res.company else None

        response = {
            "count": count,
            "option": page,
            "jobs": jobs_response,
        }

        return CustomResponse(data=response)

    async def get_by_id_for_business(
        self, db: Session, redis: Redis, job_id: int, current_user: Account
    ):
        job = jobCRUD.get(db, job_id)
        company = companyCRUD.get_by_business_id(db, current_user.id)
        if not job:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Job not found"
            )

        if (
            job.business_id != current_user.id
            or job.campaign.company_id != company.id
            or not company
        ) and current_user.role not in [
            Role.SUPER_USER,
            Role.ADMIN,
        ]:
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
            )

        response = await job_helper.get_info_business(db, redis, job)

        return CustomResponse(data=response)

    async def get_by_id_for_user(
        self, db: Session, redis: Redis, job_id: int, current_user: Account
    ):
        job: Job = jobCRUD.get(db, job_id)
        if not job:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Job not found"
            )

        if (
            job.status != JobStatus.PUBLISHED
            or job.job_approval_request.status != JobApprovalStatus.APPROVED
        ):
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Job not found"
            )

        response: JobItemResponse = await job_helper.get_info(db, redis, job)

        if current_user:
            cv_application: CVApplication = (
                cv_applicationCRUD.get_by_user_id_and_campaign_id(
                    db, current_user.id, job.campaign_id
                )
            )
            if cv_application:
                response.cv_application = cv_applications_helper.get_info(
                    db, cv_application
                )

        return CustomResponse(data=response)

    async def get_by_campaign_id(
        self, db: Session, redis: Redis, campaign_id: int, current_user: Account
    ):
        campaign = campaignCRUD.get(db, campaign_id)
        company = companyCRUD.get_by_business_id(db, current_user.id)
        if not campaign:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Campaign not found"
            )
        if (
            (
                campaign.business_id != current_user.id
                or campaign.company_id != company.id
            )
            and current_user.role
            not in [
                Role.SUPER_USER,
                Role.ADMIN,
            ]
            or not company
        ):
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
            )

        job = jobCRUD.get_by_campaign_id(db, campaign_id)
        response = await job_helper.get_info(db, redis, job)

        return CustomResponse(data=response)

    async def count_job_by_category(self, db: Session, redis: Redis):
        time_scan = CommonHelper.get_current_time(db)
        response = None
        try:
            response = await job_cache_service.get_cache_count_job_by_category(redis)
        except Exception as e:
            print(e)

        if not response:
            data = jobCRUD.count_job_by_category(db)
            response = []

            for id, count in data:
                category = category_helper.get_info_by_id(db, id)
                response.append(
                    {
                        **category.model_dump(),
                        "count": count,
                        "time_scan": str(time_scan),
                    }
                )
            try:
                await job_cache_service.cache_count_job_by_category(redis, response)
            except Exception as e:
                print(e)

        return CustomResponse(data=response)

    async def count_job_by_salary(self, db: Session, redis: Redis):
        data = None
        salary_ranges = [
            (0, 3, SalaryType.VND),
            (3, 10, SalaryType.VND),
            (10, 20, SalaryType.VND),
            (20, 30, SalaryType.VND),
            (30, 999, SalaryType.VND),
        ]
        other_salary = [
            SalaryType.DEAL,
            SalaryType.USD,
            "other",
        ]
        try:
            data = await job_cache_service.get_cache_count_job_by_salary(redis)
        except Exception as e:
            print(e)

        time_scan = CommonHelper.get_current_time(db)
        if not data:
            data = jobCRUD.count_job_by_salary(db, salary_ranges)
            try:
                await job_cache_service.cache_count_job_by_salary(redis, data)
            except Exception as e:
                print(e)

        response = []
        for index, (idx, count) in enumerate(data[:-3]):
            min, max, salary_type = salary_ranges[idx]
            response.append(
                JobCountBySalary(
                    min_salary=min,
                    max_salary=max if max != 999 else 0,
                    salary_type=salary_type,
                    count=count,
                    time_scan=time_scan,
                )
            )

        for index, (idx, count) in enumerate(data[-3:]):
            salary_type = other_salary[index]
            response.append(
                JobCountBySalary(
                    min_salary=0,
                    max_salary=0,
                    salary_type=salary_type,
                    count=count,
                    time_scan=time_scan,
                )
            )

        return CustomResponse(data=response)

    async def count_job_by_district(self, db: Session):
        response = jobCRUD.count_job_by_district(db)
        return constant.SUCCESS, 200, response

    async def get_cruitment_demand(self, db: Session, redis: Redis):
        time_scan = CommonHelper.get_current_time(db)
        approved_time = time_scan - timedelta(days=1)

        response = None
        params = JobCount(
            job_status=JobStatus.PUBLISHED,
            job_approve_status=JobApprovalStatus.APPROVED,
        )
        work_market_data: WorkMarket = None

        try:
            response = await job_cache_service.get_cache_job_cruiment_demand(redis)
        except Exception as e:
            print(e)

        if not response:
            number_of_job_24h = await job_cache_service.get_cache_count_job_24h(redis)
            if not number_of_job_24h:
                work_market_data = work_marketCRUD.get_lastest(db)
                if work_market_data:
                    number_of_job_24h = work_market_data.quantity_job_new_today
                try:
                    await job_cache_service.cache_count_job_24h(
                        redis, number_of_job_24h
                    )
                except Exception as e:
                    print(e)

            number_of_job_active = await job_cache_service.get_cache_count_job_active(
                redis
            )
            if not number_of_job_active:
                if work_market_data:
                    number_of_job_active = work_market_data.quantity_job_recruitment
                else:
                    work_market_data = work_marketCRUD.get_lastest(db)
                    if work_market_data:
                        number_of_job_active = work_market_data.quantity_job_recruitment
                try:
                    await job_cache_service.cache_count_job_active(
                        redis, number_of_job_active
                    )
                except Exception as e:
                    print(e)
            number_of_company_active = (
                await job_cache_service.get_cache_count_job_active(redis)
            )
            if not number_of_company_active:
                if work_market_data:
                    number_of_company_active = (
                        work_market_data.quantity_company_recruitment
                    )
                else:
                    work_market_data = work_marketCRUD.get_lastest(db)
                    if work_market_data:
                        number_of_company_active = (
                            work_market_data.quantity_company_recruitment
                        )
                try:
                    await job_cache_service.cache_count_job_active(
                        redis, number_of_company_active
                    )
                except Exception as e:
                    print(e)
            response = {
                "number_of_job_24h": number_of_job_24h,
                "number_of_job_active": number_of_job_active,
                "number_of_company_active": number_of_company_active,
                "time_scan": str(time_scan),
            }
            try:
                await job_cache_service.cache_job_cruiment_demand(redis, response)
            except Exception as e:
                print(e)

        return CustomResponse(data=response)

    async def create(
        self, db: Session, redis: Redis, data: dict, current_user: Account
    ):
        manager: Manager = current_user.manager
        business: Business = manager.business
        business_auth_helper.verified_level(business, 2)
        job_data = JobCreateRequest(**data)

        company: Company = business.company
        if not company:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Require join company"
            )

        job_helper.check_fields(
            db,
            must_have_skills=job_data.must_have_skills,
            should_have_skills=job_data.should_have_skills,
            locations=job_data.locations,
            categories=job_data.categories,
            working_times=job_data.working_times,
            experience_id=job_data.job_experience_id,
            position_id=job_data.job_position_id,
        )

        campaign = campaign_helper.check_exist(
            db,
            business_id=current_user.id,
            campaign_id=job_data.campaign_id,
            status=CampaignStatus.OPEN,
            title=job_data.title,
        )
        if jobCRUD.get_by_campaign_id(db, campaign.id):
            raise CustomException(
                status_code=status.HTTP_400_BAD_REQUEST, msg="Campaign already has job"
            )

        job_data.campaign_id = campaign.id

        is_verified_company = company.is_verified
        job_data_in = JobCreate(
            **job_data.model_dump(),
            business_id=current_user.id,
            status=JobStatus.PENDING,
            employer_verified=is_verified_company,
        )

        job = jobCRUD.create(db=db, obj_in=job_data_in)
        job_helper.create_fields(
            db,
            job_id=job.id,
            must_have_skills=job_data.must_have_skills,
            should_have_skills=job_data.should_have_skills,
            locations=job_data.locations,
            categories=job_data.categories,
            working_times=job_data.working_times,
        )
        job_response = await job_helper.get_info(db, redis, job)

        job_approval_request_helper.create(
            db,
            job_id=job.id,
            status=JobApprovalStatus.PENDING,
        )

        return CustomResponse(status_code=status.HTTP_201_CREATED, data=job_response)

    async def update(self, db: Session, data: dict, current_user: Account):
        job_data = JobUpdateRequest(**data)

        job = jobCRUD.get(db, job_data.job_id)
        if not job:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Job not found"
            )

        company: Company = companyCRUD.get_by_business_id(db, current_user.id)
        if (
            job.business_id != current_user.id
            or not company
            or job.campaign.business_id != current_user.id
            or job.campaign.company_id != company.id
        ):
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
            )

        must_have_skills_data = job_data.must_have_skills
        should_have_skills_data = job_data.should_have_skills
        locations_data = job_data.locations
        categories_data = job_data.categories
        working_times_data = job_data.working_times

        job_helper.check_fields(
            db,
            must_have_skills=must_have_skills_data,
            should_have_skills=should_have_skills_data,
            locations=locations_data,
            categories=categories_data,
            working_times=working_times_data,
            experience_id=job_data.job_experience_id,
            position_id=job_data.job_position_id,
        )

        job_approval_request_data = {
            "work_locations": job_data.locations,
            **job_data.model_dump(),
        }
        job_approval_request = JobApprovalRequestCreate(**job_approval_request_data)
        job_approval_requests_pending_before = (
            job_approval_requestCRUD.get_pending_by_job_id(db, job.id)
        )
        if job_approval_requests_pending_before:
            for (
                job_approval_request_pending_before
            ) in job_approval_requests_pending_before:
                job_approval_requestCRUD.remove(
                    db, id=job_approval_request_pending_before.id
                )
        job_approval_request = (
            job_approval_request_helper.create_job_update_approval_request(
                db,
                {
                    **job_approval_request_data,
                    "request": RequestApproval.UPDATE,
                },
            )
        )
        job_approval_request_response = JobApprovalRequestResponse(
            **job_approval_request.__dict__
        )

        return CustomResponse(
            status_code=status.HTTP_201_CREATED, data=job_approval_request_response
        )

    async def delete(self, db: Session, job_id: int, current_user: Account):
        job = jobCRUD.get(db, job_id)
        company = companyCRUD.get_by_business_id(db, current_user.id)
        if not job:
            raise CustomException(
                status_code=status.HTTP_404_NOT_FOUND, msg="Job not found"
            )

        if (
            not company
            or job.business_id != current_user.id
            or job.campaign.company_id != company.id
        ):
            raise CustomException(
                status_code=status.HTTP_403_FORBIDDEN, msg="Permission denied"
            )

        response = jobCRUD.remove(db, id=job_id)

        return CustomResponse(data=response)


job_service = JobService()
