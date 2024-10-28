from typing import Type, List
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.crud.base import CRUDBase
from app.model import Job, CVApplication
from app.schema.cv_application import CVApplicationCreate, CVApplicationUpdate
from app.hepler.enum import (
    CVApplicationStatus,
    SortBy,
    OrderType,
)


class CRUDCVApplication(CRUDBase[Job, CVApplicationCreate, CVApplicationUpdate]):
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
        status: CVApplicationStatus,
        **kwargs
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

    def get_by_campaign_id(
        self,
        db: Session,
        *,
        skip=0,
        limit=10,
        sort_by: SortBy = SortBy.CREATED_AT,
        order_by: OrderType = OrderType.DESC,
        campaign_id: int,
        status: CVApplicationStatus
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
        self, db: Session, campaign_id: int, status: CVApplicationStatus
    ) -> int:
        query = db.query(func.count(self.model.id))
        if status:
            query = query.filter(
                self.model.status == status, self.model.campaign_id == campaign_id
            )
        else:
            query = query.filter(self.model.campaign_id == campaign_id)
        return query.scalar()

    def count(self, db: Session, status: CVApplicationStatus) -> int:
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
        status: CVApplicationStatus
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
