from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.config_from_object("app.core.celery_config")

celery_app.conf.beat_schedule = {
    "periodic-task": {
        "task": "app.tasks.job_scan.scan_task",
        "schedule": crontab(minute=0, hour=0),
        "args": ("Scheduled Task",),
    },
    "periodic-task-2": {
        "task": "app.tasks.data_statistics.scan_task",
        "schedule": crontab(minute=0, hour="*/1"),
        "args": ("Scheduled Task",),
    },
}

celery_app.autodiscover_tasks(["app.tasks.data_statistics"])
