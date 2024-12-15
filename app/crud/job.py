from typing import Type, List
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import distinct
from sqlalchemy import case, func, or_, and_, text, exists

from .base import CRUDBase
from app.model import (
    Job,
    JobApprovalRequest,
    Business,
    WorkLocation,
    Province,
    District,
    Campaign,
    Field,
    JobCategory,
    Company,
    CompanyField,
)
from app.schema.job import JobCreate, JobUpdate
from app.hepler.enum import JobStatus, SalaryType, JobApprovalStatus


class CRUDJob(CRUDBase[Job, JobCreate, JobUpdate]):
    def __init__(self, model: Type[Job]):
        super().__init__(model)
        self.job_approval_request = JobApprovalRequest
        self.business = Business
        self.work_location = WorkLocation
        self.province = Province
        self.district = District
        self.job_category = JobCategory
        self.field = Field
        self.company = Company
        self.company_field = CompanyField
        self.campaign = Campaign

    def get_multi(
        self,
        db: Session,
        **kwargs,
    ) -> List[Job]:
        query = db.query(self.model)
        if kwargs.get("province_id") or kwargs.get("district_id"):
            query = query.join(
                self.work_location, self.model.id == self.work_location.job_id
            )

        query = self.apply_filters(
            query,
            **kwargs,
        )
        skip = kwargs.get("skip", 0)
        limit = kwargs.get("limit", 10)
        sort_by = kwargs.get("sort_by", "id")
        order_by = kwargs.get("order_by", "desc")
        return (
            query.order_by(
                getattr(self.model, sort_by).desc()
                if order_by == "desc"
                else getattr(self.model, sort_by)
            )
            .offset(skip)
            .limit(limit)
            .distinct()
            .all()
        )

    def get_by_campaign_id(self, db: Session, campaign_id: int) -> Job:
        return (
            db.query(self.model).filter(self.model.campaign_id == campaign_id).first()
        )

    def count(
        self,
        db: Session,
        **kwargs,
    ) -> int:
        query = db.query(func.count(self.model.id))
        if kwargs.get("province_id") or kwargs.get("district_id"):
            query = query.join(
                self.work_location, self.model.id == self.work_location.job_id
            )
        query = self.apply_filters(
            query,
            **kwargs,
        )
        result = query.scalar()

        return result

    def search(
        self,
        db: Session,
        **kwargs,
    ) -> List[Job]:
        skip = kwargs.get("skip", 0)
        limit = kwargs.get("limit", 10)
        sort_by = kwargs.get("sort_by", "id")
        order_by = kwargs.get("order_by", "desc")
        province_id = kwargs.get("province_id")
        district_id = kwargs.get("district_id")

        jobs_query = db.query(self.model)
        if province_id or district_id:
            jobs_query = jobs_query.join(
                self.work_location, self.model.id == self.work_location.job_id
            )
        jobs = (
            self.apply_filters(jobs_query, **kwargs)
            .order_by(
                getattr(self.model, sort_by).desc()
                if order_by == "desc"
                else getattr(self.model, sort_by)
            )
            .offset(skip)
            .limit(limit)
            .distinct()
            .all()
        )

        return jobs

    def user_count(
        self,
        db: Session,
        **kwargs,
    ) -> int:
        query = db.query(func.count(self.model.id)).filter(
            Job.status == JobStatus.PUBLISHED, Job.deadline >= func.now()
        )

        query = self.user_apply_filters(query, **kwargs)

        return query.scalar()

    def user_search(
        self,
        db: Session,
        **kwargs,
    ) -> List[Job]:
        skip = kwargs.get("skip", 0)
        limit = kwargs.get("limit", 10)
        sort_by = kwargs.get("sort_by", "id")
        order_by = kwargs.get("order_by", "desc")

        query = db.query(Job).filter(
            Job.status == JobStatus.PUBLISHED, Job.deadline >= func.now()
        )

        query = (
            self.user_apply_filters(query, **kwargs)
            .order_by(
                getattr(self.model, sort_by).desc()
                if order_by == "desc"
                else getattr(self.model, sort_by)
            )
            .offset(skip)
            .limit(limit)
        )
        jobs = query.all()
        return jobs

    def user_apply_filters(self, query, **filters):
        company_id = filters.get("company_id")
        field_id = filters.get("field_id")
        province_id = filters.get("province_id")
        district_id = filters.get("district_id")
        category_id = filters.get("category_id")
        employment_type = filters.get("employment_type")
        job_experience_id = filters.get("job_experience_id")
        job_position_id = filters.get("job_position_id")
        min_salary = filters.get("min_salary")
        max_salary = filters.get("max_salary")
        salary_type = filters.get("salary_type")
        keyword = filters.get("keyword")
        updated_at = filters.get("updated_at")

        if updated_at:
            query = query.filter(self.model.updated_at >= updated_at)
        if company_id or field_id:
            query = query.join(
                self.campaign, self.model.campaign_id == self.campaign.id
            )
            if company_id:
                query = query.filter(self.campaign.company_id == company_id)
            if field_id:
                query = query.join(
                    self.company, self.campaign.company_id == self.company.id
                )
                query = query.join(
                    self.company_field, self.company.id == self.company_field.company_id
                ).filter(self.company_field.field_id == field_id)
        if province_id or district_id:
            query = query.join(
                self.work_location, self.model.id == self.work_location.job_id
            )
            if province_id:
                query = query.filter(self.work_location.province_id == province_id)
            if district_id:
                query = query.filter(self.work_location.district_id == district_id)
        if category_id:
            query = query.join(
                self.job_category, self.model.id == self.job_category.job_id
            ).filter(self.job_category.category_id == category_id)
        if employment_type:
            query = query.filter(self.model.employment_type == employment_type)
        if job_experience_id:
            query = query.filter(self.model.job_experience_id == job_experience_id)
        if job_position_id:
            query = query.filter(self.model.job_position_id == job_position_id)
        if salary_type:
            query = query.filter(self.model.salary_type == salary_type)
        if min_salary:
            query = query.filter(self.model.min_salary >= min_salary)
        if max_salary:
            query = query.filter(self.model.max_salary <= max_salary)
        if salary_type:
            query = query.filter(self.model.salary_type == salary_type)
        if min_salary or max_salary and not salary_type:
            query = query.filter(self.model.salary_type != SalaryType.DEAL)
        if keyword:
            query = query.filter(self.model.title.ilike(f"%{keyword}%"))
        return query

    def get_number_job_of_district(self, db: Session, **filters):
        query = db.query(
            self.work_location.district_id,
            func.count(distinct(self.model.id)),
        )
        query = query.join(self.model, self.work_location.job_id == self.model.id)
        query = self.apply_filters(query, **filters)
        query = query.group_by(
            self.work_location.district_id,
        )
        return query.all()

    def apply_filters(self, query, **filters):
        company_id = filters.get("company_id")
        field_id = filters.get("field_id")
        campaign_id = filters.get("campaign_id")
        business_id = filters.get("business_id")
        job_status = filters.get("job_status")
        job_approve_status = filters.get("job_approve_status")
        province_id = filters.get("province_id")
        district_id = filters.get("district_id")
        category_id = filters.get("category_id")
        employment_type = filters.get("employment_type")
        job_experience_id = filters.get("job_experience_id")
        job_position_id = filters.get("job_position_id")
        min_salary = filters.get("min_salary")
        max_salary = filters.get("max_salary")
        salary_type = filters.get("salary_type")
        deadline = filters.get("deadline")
        keyword = filters.get("keyword")
        approved_time = filters.get("approved_time")

        if company_id or field_id:
            query = query.join(
                self.campaign, self.model.campaign_id == self.campaign.id
            )
            if company_id:
                query = query.filter(self.campaign.company_id == company_id)
            if field_id:
                query = query.join(
                    self.company, self.campaign.company_id == self.company.id
                )
                query = query.join(
                    self.company_field, self.company.id == self.company_field.company_id
                ).filter(self.company_field.field_id == field_id)
        if campaign_id:
            query = query.filter(self.model.campaign_id == campaign_id)
        if business_id:
            query = query.filter(self.model.business_id == business_id)
        if job_status:
            query = query.filter(self.model.status == job_status)
        if job_approve_status or approved_time:
            query = query.join(
                self.job_approval_request,
                self.model.id == self.job_approval_request.job_id,
            )
            if approved_time:
                query = query.filter(
                    self.job_approval_request.updated_at >= approved_time,
                    self.job_approval_request.status == JobApprovalStatus.APPROVED,
                )
            elif job_approve_status:
                query = query.filter(
                    self.job_approval_request.status == job_approve_status
                )
        if province_id or district_id:
            if province_id:
                query = query.filter(self.work_location.province_id == province_id)
            if district_id:
                query = query.filter(self.work_location.district_id == district_id)
        if category_id:
            query = query.join(
                self.job_category, self.model.id == self.job_category.job_id
            ).filter(self.job_category.category_id == category_id)
        if employment_type:
            query = query.filter(self.model.employment_type == employment_type)
        if job_experience_id:
            query = query.filter(self.model.job_experience_id == job_experience_id)
        if job_position_id:
            query = query.filter(self.model.job_position_id == job_position_id)
        if salary_type:
            query = query.filter(self.model.salary_type == salary_type)
        if min_salary:
            query = query.filter(self.model.min_salary >= min_salary)
        if max_salary:
            query = query.filter(self.model.max_salary <= max_salary)
        if salary_type:
            query = query.filter(self.model.salary_type == salary_type)
        if min_salary or max_salary and not salary_type:
            query = query.filter(self.model.salary_type != SalaryType.DEAL)
        if deadline:
            query = query.filter(self.model.deadline >= deadline)
        if keyword:
            query = query.filter(self.model.title.ilike(f"%{keyword}%"))
        return query

    def count_job_by_category(self, db: Session):
        query = (
            db.query(
                self.job_category.category_id.label("category_id"),
                func.count(self.model.id).label("job_count"),
            )
            .join(self.job_category, self.model.id == self.job_category.job_id)
            .filter(
                self.model.deadline >= func.now(),
                self.model.status == JobStatus.PUBLISHED,
            )
            .group_by("category_id")
            .order_by(func.count(self.model.id).desc())
        )
        return query.all()

    def count_job_by_salary(self, db: Session, salary_ranges):
        unit = 1000000

        query = (
            db.query(
                case(
                    *[
                        (
                            and_(
                                self.model.min_salary >= salary_range[0] * unit,
                                self.model.max_salary < salary_range[1] * unit,
                                self.model.salary_type == salary_range[2],
                                self.model.status == JobStatus.PUBLISHED,
                            ),
                            idx,
                        )
                        for idx, salary_range in enumerate(salary_ranges)
                    ],
                    (
                        and_(
                            self.model.salary_type == SalaryType.DEAL,
                            self.model.status == JobStatus.PUBLISHED,
                        ),
                        len(salary_ranges),
                    ),
                    (
                        and_(
                            self.model.salary_type == SalaryType.USD,
                            self.model.status == JobStatus.PUBLISHED,
                        ),
                        len(salary_ranges) + 1,
                    ),
                    else_=len(salary_ranges) + 2,
                ).label("salary_range"),
                func.count(self.model.id).label("job_count"),
            )
            .filter(self.model.deadline >= func.now())
            .group_by("salary_range")
            .order_by("salary_range")
            .all()
        )
        results = query
        return results

    def count_company_active_job(self, db: Session) -> int:
        return (
            db.query(func.count(func.distinct(self.company.id)).label("count_1"))
            .filter(
                exists()
                .where(self.campaign.company_id == self.company.id)
                .where(self.model.campaign_id == self.campaign.id)
                .where(
                    self.model.deadline >= func.now(),
                    self.model.status == JobStatus.PUBLISHED,
                )
            )
            .scalar()
        )

    def update_expired_job(self, db: Session):
        return (
            db.query(self.model)
            .filter(
                self.model.deadline < func.now(),
                self.model.status == JobStatus.PUBLISHED,
            )
            .update({"status": JobStatus.EXPIRED}, synchronize_session=False)
        )

    def update_status_job(self, db: Session, job: Job, status: JobStatus):
        job.status = status
        db.add(job)
        db.commit()
        db.refresh(job)
        return job


job = CRUDJob(Job)
