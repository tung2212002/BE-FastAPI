from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.crud import work_market as work_market_crud
from app.crud import job as job_crud
from app.schema.work_market import WorkMarketCreate
from app.db.base import SessionLocal
from app.hepler.enum import JobApprovalStatus, JobStatus
from app.hepler.common import CommonHelper
from datetime import timedelta


@celery_app.task(bind=True, name="app.tasks.data_statistics.scan_task")
def scan_task(self, name: str) -> str:
    try:
        db: Session = SessionLocal()
        quantity_company_recruitment = job_crud.count_company_active_job(db)
        time_scan = CommonHelper.utc_now()
        approved_time = time_scan - timedelta(days=1)

        quantity_job_recruitment = job_crud.count(
            db,
            job_status=JobStatus.PUBLISHED,
            approval_status=JobApprovalStatus.APPROVED,
            deadline=time_scan,
        )
        quantity_job_recruitment_yesterday = (
            work_market_crud.get_number_of_job_yesterday(db)
        )
        number_of_job_24h = job_crud.count(
            db,
            job_status=JobStatus.PUBLISHED,
            approval_status=JobApprovalStatus.APPROVED,
            approved_time=approved_time,
        )
        work_market_data = {
            "quantity_company_recruitment": quantity_company_recruitment,
            "quantity_job_recruitment": quantity_job_recruitment,
            "quantity_job_recruitment_yesterday": quantity_job_recruitment_yesterday,
            "quantity_job_new_today": number_of_job_24h,
            "time_scan": time_scan,
        }
        new_work_market = WorkMarketCreate(**work_market_data)
        work_market_crud.create(db, obj_in=new_work_market)

        return f"Task {name} executed successfully"
    except Exception as exc:
        raise self.retry(exc=exc)
