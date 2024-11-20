from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone


from app.model import WorkMarket
from app.schema.work_market import WorkMarketCreate


class CRUDWorkMarket:

    def create(self, db: Session, *, obj_in: WorkMarketCreate) -> WorkMarket:
        db_obj = WorkMarket(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_lastest(self, db: Session) -> WorkMarket:
        return db.query(WorkMarket).order_by(WorkMarket.time_scan.desc()).first()

    def get_yesterday(self, db: Session) -> WorkMarket:
        today = datetime.now()
        yesterday = today - timedelta(days=1)

        start_of_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day)
        end_of_yesterday = datetime(
            yesterday.year, yesterday.month, yesterday.day, 23, 59, 59, 999999
        )

        return (
            db.query(WorkMarket)
            .filter(
                WorkMarket.time_scan >= start_of_yesterday,
                WorkMarket.time_scan <= end_of_yesterday,
            )
            .order_by(WorkMarket.time_scan.desc())
            .first()
        )

    def get_number_of_job_yesterday(self, db: Session) -> int:
        work_market = self.get_yesterday(db)
        if work_market:
            return work_market.quantity_job_recruitment
        return 0


work_market = CRUDWorkMarket()
