from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.crud import job as job_crud
from app.db.base import SessionLocal


@celery_app.task(bind=True, name="app.tasks.job_scan.scan_task")
def scan_task(self, name: str) -> str:
    try:
        db: Session = SessionLocal()
        job_crud.update_expired_job(db)
        return f"Task {name} executed successfully"
    except Exception as exc:
        raise self.retry(exc=exc)
