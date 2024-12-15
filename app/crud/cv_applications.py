from typing import Type, List
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from sqlalchemy import or_

from app.crud.base import CRUDBase
from app.model import Job, CVApplication, Campaign
from app.schema.cv_application import CVApplicationCreate, CVApplicationUpdate
from app.hepler.enum import (
    CVApplicationStatus,
    SortBy,
    OrderType,
)


class CRUDCVApplication(
    CRUDBase[CVApplication, CVApplicationCreate, CVApplicationUpdate]
):
    def __init__(self, model: Type[CVApplication]):
        super().__init__(model)

    def get_by_user_id(
        self,
        db: Session,
        *,
        skip=0,
        limit=10,
        sort_by: SortBy = SortBy.CREATED_AT,
        user_id: int,
        status: CVApplicationStatus = None,
        **kwargs,
    ) -> List[CVApplication]:
        query = db.query(self.model)
        if status:
            query = query.filter(
                self.model.status == status, self.model.user_id == user_id
            )
        else:
            query = query.filter(self.model.user_id == user_id)
        return (
            query.order_by(getattr(self.model, sort_by).desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_user_id(
        self, db: Session, user_id: int, status: CVApplicationStatus
    ) -> int:
        query = db.query(func.count(self.model.id))
        if status:
            query = query.filter(
                self.model.status == status, self.model.user_id == user_id
            )
        else:
            query = query.filter(self.model.user_id == user_id)
        return query.scalar()

    def count_by_business_id(self, db: Session, business_id: int, **kwargs) -> int:
        status = kwargs.get("status")
        campaign_id = kwargs.get("campaign_id")
        keyword = kwargs.get("keyword")

        query = (
            db.query(func.count(self.model.id))
            .join(Campaign)
            .filter(Campaign.business_id == business_id)
        )
        query = self.query_filter(
            query, status=status, campaign_id=campaign_id, keyword=keyword
        )
        return query.scalar()

    def get_by_business_id(
        self,
        db: Session,
        *,
        skip=0,
        limit=10,
        sort_by: SortBy = SortBy.CREATED_AT,
        order_by: OrderType = OrderType.DESC,
        business_id: int,
        **kwargs,
    ) -> List[CVApplication]:
        status = kwargs.get("status")
        campaign_id = kwargs.get("campaign_id")
        keyword = kwargs.get("keyword")

        query = (
            db.query(self.model)
            .join(Campaign)
            .filter(Campaign.business_id == business_id)
        )
        query = self.query_filter(
            query, status=status, campaign_id=campaign_id, keyword=keyword
        )
        return (
            query.order_by(
                getattr(self.model, sort_by).desc()
                if order_by == OrderType.DESC
                else getattr(self.model, sort_by)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def query_filter(self, query, **kwargs):
        status = kwargs.get("status")
        campaign_id = kwargs.get("campaign_id")
        keyword = kwargs.get("keyword")

        if status:
            query = query.filter(self.model.status == status)
        if campaign_id:
            query = query.filter(self.model.campaign_id == campaign_id)
        if keyword:
            query = query.filter(
                or_(
                    self.model.full_name.ilike(f"%{keyword}%"),
                    self.model.email.ilike(f"%{keyword}%"),
                    self.model.phone_number.ilike(f"%{keyword}%"),
                )
            )
        return query

    def get_by_campaign_id(
        self,
        db: Session,
        *,
        skip=0,
        limit=10,
        sort_by: SortBy = SortBy.UPDATED_AT,
        order_by: OrderType = OrderType.DESC,
        campaign_id: int,
        status: CVApplicationStatus = None,
    ) -> List[CVApplication]:
        query = db.query(self.model)
        if status:
            query = query.filter(
                self.model.status == status, self.model.campaign_id == campaign_id
            )
        else:
            query = query.filter(self.model.campaign_id == campaign_id)
        return (
            query.order_by(
                getattr(self.model, sort_by).desc()
                if order_by == OrderType.DESC
                else getattr(self.model, sort_by)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_campaign_id(
        self, db: Session, campaign_id: int, status: CVApplicationStatus = None
    ) -> int:
        query = db.query(func.count(self.model.id))
        if status:
            query = query.filter(
                self.model.status == status, self.model.campaign_id == campaign_id
            )
        else:
            query = query.filter(self.model.campaign_id == campaign_id)
        return query.scalar()

    def count(self, db: Session, status: CVApplicationStatus = None) -> int:
        query = db.query(func.count(self.model.id))
        if status:
            query = query.filter(self.model.status == status)
        return query.scalar()

    def get_multi(
        self,
        db: Session,
        *,
        skip=0,
        limit=10,
        sort_by: SortBy = SortBy.CREATED_AT,
        order_by: OrderType = OrderType.DESC,
        status: CVApplicationStatus = None,
    ) -> List[CVApplication]:
        query = db.query(self.model)
        if status:
            query = query.filter(self.model.status == status)
        return (
            query.order_by(
                getattr(self.model, sort_by).desc()
                if order_by == OrderType.DESC
                else getattr(self.model, sort_by)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user_id_and_campaign_id(
        self,
        db: Session,
        user_id: int,
        campaign_id: int,
    ) -> CVApplication:
        return (
            db.query(self.model)
            .filter(
                self.model.user_id == user_id, self.model.campaign_id == campaign_id
            )
            .first()
        )


cv_applications = CRUDCVApplication(CVApplication)
