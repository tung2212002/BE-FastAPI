from pydantic import BaseModel, validator
from datetime import datetime


class WorkMarketCreate(BaseModel):
    quantity_company_recruitment: int
    quantity_job_recruitment: int
    quantity_job_recruitment_yesterday: int
    quantity_job_new_today: int
    time_scan: datetime
