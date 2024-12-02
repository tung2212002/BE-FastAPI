from typing import List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase

from app.model import JobApprovalRequest, Job, Campaign
from app.schema.job_approval_request import (
    JobApprovalRequestCreate,
    JobApprovalRequestUpdate,
)
from app.hepler.enum import (
    JobApprovalStatus,
    OrderType,
    SortBy,
)


class CRUDJobApprovalRequest(
    CRUDBase[JobApprovalRequest, JobApprovalRequestCreate, JobApprovalRequestUpdate]
):
    def get_by_job_id(self, db, job_id: int) -> List[JobApprovalRequest]:
        return db.query(self.model).filter(self.model.job_id == job_id).all()

    def get_pending_by_job_id(self, db, job_id: int) -> List[JobApprovalRequest]:
        return (
            db.query(self.model)
            .filter(
                self.model.job_id == job_id,
                self.model.status == JobApprovalStatus.PENDING,
            )
            .all()
        )

    def get_last_by_job_id(self, db, job_id: int) -> JobApprovalRequest:
        return (
            db.query(self.model)
            .filter(self.model.job_id == job_id)
            .order_by(self.model.id.desc())
            .first()
        )

    def get_multi(
        self,
        db: Session,
        *,
        business_id: int = None,
        company_id: int = None,
        skip=0,
        limit=10,
        sort_by: SortBy = SortBy.ID,
        order_by: OrderType = OrderType.DESC,
        status: JobApprovalStatus = None,
    ) -> List[JobApprovalRequest]:
        query = db.query(self.model)
        query = self.apply_filter(
            query, business_id=business_id, company_id=company_id, status=status
        )
        return (
            query.order_by(
                getattr(self.model, sort_by.value).desc()
                if order_by == OrderType.DESC
                else getattr(self.model, sort_by.value)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def apply_filter(
        self,
        query,
        business_id: int = None,
        company_id: int = None,
        status: JobApprovalStatus = None,
    ):
        if business_id or company_id:
            query = query.join(Job, Job.id == self.model.job_id)
            if business_id:
                query = query.filter(Job.business_id == business_id)
            if company_id:
                query = query.join(Campaign, Campaign.id == Job.campaign_id).filter(
                    Campaign.company_id == company_id
                )
        if status:
            query = query.filter(self.model.status == status)
        return query


job_approval_request = CRUDJobApprovalRequest(JobApprovalRequest)
