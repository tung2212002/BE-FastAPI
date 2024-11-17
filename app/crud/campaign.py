from sqlalchemy.orm import Session
from datetime import date, timedelta
from sqlalchemy.sql import func, text
from typing import List

from .base import CRUDBase
from app.model import Job, Campaign, CVApplication
from app.schema.campaign import CampaignCreate, CampaignUpdate
from app.hepler.enum import (
    CampaignStatus,
    OrderType,
    SortBy,
    JobStatus,
    CVApplicationStatus,
)


class CRUDCampaign(CRUDBase[Campaign, CampaignCreate, CampaignUpdate]):
    def get_multi(
        self,
        db: Session,
        *,
        business_id: int = None,
        company_id: int = None,
        skip: int = 0,
        limit: int = 10,
        sort_by: SortBy = SortBy.ID,
        order_by: OrderType = OrderType.DESC,
        status: CampaignStatus = None,
    ) -> List[Campaign]:
        query = db.query(self.model)
        query = self.apply_filter(
            query, business_id=business_id, company_id=company_id, status=status
        )
        result = self.return_campaign(query, skip, limit, sort_by, order_by)
        return result

    def count(
        self,
        db: Session,
        *,
        business_id: int = None,
        company_id: int = None,
        status: CampaignStatus = None,
    ) -> int:
        query = db.query(func.count(self.model.id))
        query = self.apply_filter(
            query, business_id=business_id, company_id=company_id, status=status
        )
        result = query.scalar()
        return result

    def get_has_published_job(
        self,
        db: Session,
        *,
        business_id: int = None,
        company_id: int = None,
        skip=0,
        limit=10,
        sort_by: SortBy = SortBy.ID,
        order_by: OrderType = OrderType.DESC,
    ) -> List[Campaign]:
        query = db.query(self.model)
        query = self.apply_filter(
            query,
            business_id=business_id,
            company_id=company_id,
            # status=CampaignStatus.OPEN,
            job_status=JobStatus.PUBLISHED,
            job_deadline=True,
        )
        result = self.return_campaign(query, skip, limit, sort_by, order_by)
        return result

    def count_has_published_job(
        self,
        db: Session,
        *,
        business_id: int = None,
        company_id: int = None,
    ) -> int:
        query = db.query(func.count(self.model.id))
        query = self.apply_filter(
            query,
            business_id=business_id,
            company_id=company_id,
            # status=CampaignStatus.OPEN,
            job_status=JobStatus.PUBLISHED,
            job_deadline=True,
        )
        result = query.scalar()
        return result

    def get_open(
        self,
        db: Session,
        *,
        business_id: int = None,
        company_id: int = None,
        skip=0,
        limit=10,
        sort_by: SortBy = SortBy.ID,
        order_by: OrderType = OrderType.DESC,
    ) -> List[Campaign]:
        query = db.query(self.model)
        query = self.apply_filter(
            query,
            business_id=business_id,
            company_id=company_id,
            status=CampaignStatus.OPEN,
        )
        result = self.return_campaign(query, skip, limit, sort_by, order_by)
        return result

    def count_open(
        self,
        db: Session,
        *,
        business_id: int = None,
        company_id: int = None,
    ) -> int:
        query = db.query(func.count(self.model.id))
        query = self.apply_filter(
            query,
            business_id=business_id,
            company_id=company_id,
            status=CampaignStatus.OPEN,
        )
        result = query.scalar()
        return result

    def get_has_new_application(
        self,
        db: Session,
        *,
        business_id: int = None,
        company_id: int = None,
        skip=0,
        limit=10,
        sort_by: SortBy = SortBy.ID,
        order_by: OrderType = OrderType.DESC,
    ) -> List[Campaign]:
        query = db.query(self.model)
        query = self.apply_filter(
            query,
            business_id=business_id,
            company_id=company_id,
            job_status=JobStatus.PUBLISHED,
            job_deadline=True,
        )
        query = query.join(CVApplication).filter(
            CVApplication.status == CVApplicationStatus.PENDING
            and CVApplication.created_at >= func.now() - text("INTERVAL 1 DAY")
        )
        result = self.return_campaign(query, skip, limit, sort_by, order_by)
        return result

    def count_has_new_application(
        self, db: Session, *, business_id: int = None, company_id: int = None, **kwargs
    ) -> int:
        query = db.query(func.count(self.model.id))
        query = self.apply_filter(query, business_id=business_id, company_id=company_id)
        query = query.join(Job).filter(
            Job.status == JobStatus.PUBLISHED, Job.deadline >= func.now()
        )
        query = query.join(CVApplication).filter(
            CVApplication.status == CVApplicationStatus.PENDING
            and CVApplication.created_at >= func.now() == date.timedelta(days=1)
        )
        result = query.scalar()
        return result

    def get_has_published(
        self,
        db: Session,
        *,
        business_id: int = None,
        company_id: int = None,
    ) -> List[Campaign]:
        query = db.query(func.count(self.model.id))
        query = self.apply_filter(
            query,
            business_id=business_id,
            company_id=company_id,
            status=CampaignStatus.OPEN,
        )
        query = query.join(Job).filter(Job.status == JobStatus.PUBLISHED)
        result = query.scalar()
        return result

    def count_has_published(
        self,
        db: Session,
        *,
        business_id: int = None,
        company_id: int = None,
    ) -> int:
        query = db.query(func.count(self.model.id))
        query = self.apply_filter(
            query,
            business_id=business_id,
            company_id=company_id,
            job_status=JobStatus.PUBLISHED,
        )
        result = query.scalar()
        return result

    def get_has_published_job_expired(
        self,
        db: Session,
        *,
        business_id: int = None,
        company_id: int = None,
        skip=0,
        limit=10,
        sort_by: SortBy = SortBy.ID,
        order_by: OrderType = OrderType.DESC,
    ) -> List[Campaign]:
        query = db.query(self.model)
        query = self.apply_filter(
            query,
            business_id=business_id,
            company_id=company_id,
            status=CampaignStatus.OPEN,
        )
        query = query.join(Job).filter(
            Job.status == JobStatus.PUBLISHED, Job.deadline < func.now()
        )
        result = self.return_campaign(query, skip, limit, sort_by, order_by)
        return result

    def count_has_published_job_expired(
        self,
        db: Session,
        *,
        business_id: int = None,
        company_id: int = None,
    ) -> int:
        query = db.query(func.count(self.model.id))
        query = self.apply_filter(
            query,
            business_id=business_id,
            company_id=company_id,
        )
        query = query.join(Job).filter(
            Job.status == JobStatus.PUBLISHED, Job.deadline < func.now()
        )
        result = query.scalar()
        return result

    def get_has_pending_job(
        self,
        db: Session,
        *,
        business_id: int = None,
        company_id: int = None,
        skip=0,
        limit=10,
        sort_by: SortBy = SortBy.ID,
        order_by: OrderType = OrderType.DESC,
    ) -> List[Campaign]:
        query = db.query(self.model)
        query = self.apply_filter(
            query,
            business_id=business_id,
            company_id=company_id,
            job_status=JobStatus.PENDING,
        )
        result = self.return_campaign(query, skip, limit, sort_by, order_by)
        return result

    def count_has_pending_job(
        self,
        db: Session,
        *,
        business_id: int = None,
        company_id: int = None,
    ) -> int:
        query = db.query(func.count(self.model.id))
        query = self.apply_filter(
            query,
            business_id=business_id,
            company_id=company_id,
            job_status=JobStatus.PENDING,
        )
        result = query.scalar()
        return result

    def apply_filter(
        self,
        query,
        *,
        business_id: int = None,
        company_id: int = None,
        status: CampaignStatus = None,
        job_status: JobStatus = None,
        job_deadline: bool = False,
    ):
        if business_id:
            query = query.filter(self.model.business_id == business_id)
        if status:
            query = query.filter(self.model.status == status)
        if company_id:
            query = query.filter(self.model.company_id == company_id)
        if job_status or job_deadline:
            query = query.join(Job)
            if job_deadline:
                query = query.filter(Job.deadline >= func.now())
            if job_status:
                query = query.filter(Job.status == job_status)

        return query

    def return_campaign(self, query, skip, limit, sort_by, order_by) -> List[Campaign]:
        query = (
            query.order_by(
                getattr(self.model, sort_by).desc()
                if order_by == "desc"
                else getattr(self.model, sort_by)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

        return query

    def increase_count_apply(self, db: Session, campaign: Campaign) -> Campaign:
        campaign.count_apply += 1
        db.commit()
        db.refresh(campaign)
        return campaign


campaign = CRUDCampaign(Campaign)
