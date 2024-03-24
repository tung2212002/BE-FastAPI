from sqlalchemy import Column, DateTime, Integer

from app.db.base_class import Base


class WorkMarket(Base):
    quantity_company_recruitment = Column(Integer, nullable=False)
    quantity_job_recruitment = Column(Integer, nullable=False)
    quantity_job_recruitment_yesterday = Column(Integer, nullable=False)
    quantity_job_new_today = Column(Integer, nullable=False)
    time_scan = Column(DateTime, nullable=False)
