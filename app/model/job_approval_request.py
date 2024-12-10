from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    Enum,
    DateTime,
    Date,
    JSON,
    Text,
    Boolean,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.hepler.enum import (
    JobApprovalStatus,
    SalaryType,
    Gender,
    JobType,
    RequestApproval,
)


class JobApprovalRequest(Base):
    job_id = Column(Integer, ForeignKey("job.id", ondelete="CASCADE"), index=True)
    status = Column(
        Enum(JobApprovalStatus),
        nullable=False,
        index=True,
        default=JobApprovalStatus.PENDING,
    )
    # request = Column(
    #     Enum(RequestApproval),
    #     nullable=False,
    #     index=True,
    #     default=RequestApproval.CREATE,
    # )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), index=True)
    data = Column(JSON, nullable=False)
    # job_experience_id = Column(
    #     Integer, ForeignKey("job_experience.id"), nullable=True, index=True
    # )
    # job_position_id = Column(Integer, nullable=True, index=True)
    # title = Column(String(255), index=True, nullable=True)
    # job_description = Column(Text, nullable=True)
    # job_requirement = Column(Text, nullable=True)
    # job_benefit = Column(Text, nullable=True)
    # job_location = Column(String(255), nullable=True)
    # max_salary = Column(Integer, nullable=True, index=True)
    # min_salary = Column(Integer, nullable=True, index=True)
    # salary_type = Column(Enum(SalaryType), nullable=True, index=True)
    # quantity = Column(Integer, nullable=True, index=True)
    # full_name_contact = Column(String(50), nullable=True)
    # phone_number_contact = Column(String(10), nullable=True)
    # email_contact = Column(JSON, nullable=True)
    # employment_type = Column(Enum(JobType), index=True)
    # gender_requirement = Column(Enum(Gender), index=True)
    # deadline = Column(Date, nullable=True, index=True)
    # working_time_text = Column(Text, nullable=True)

    # must_have_skills = Column(JSON, nullable=True)
    # should_have_skills = Column(JSON, nullable=True)
    # categories = Column(JSON, nullable=True)
    # work_locations = Column(JSON, nullable=True)
    # working_times = Column(JSON, nullable=True)

    job = relationship(
        "Job",
        back_populates="job_approval_request",
        uselist=False,
    )
