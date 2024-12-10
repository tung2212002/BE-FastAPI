from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Boolean,
    DateTime,
    Enum,
    Date,
    JSON,
    Text,
    event,
    Index,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, Session

from app.db.base_class import Base
from app.hepler.enum import JobStatus, Gender, JobType, SalaryType
from app.model.job_position import JobPosition
from app.model.job_category import JobCategory
from app.model.category import Category


class Job(Base):
    business_id = Column(
        Integer, ForeignKey("business.id", ondelete="CASCADE"), nullable=False
    )
    campaign_id = Column(
        Integer,
        ForeignKey("campaign.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_experience_id = Column(
        Integer, ForeignKey("job_experience.id"), nullable=False, index=True
    )
    job_position_id = Column(Integer, nullable=False, index=True)
    title = Column(String(255), index=True, nullable=False)
    job_description = Column(Text, nullable=False)
    job_requirement = Column(Text, nullable=False)
    job_benefit = Column(Text, nullable=False)
    job_location = Column(String(255), nullable=False)
    max_salary = Column(Integer, default=0, nullable=True, index=True)
    min_salary = Column(Integer, default=0, nullable=True, index=True)
    salary_type = Column(
        Enum(SalaryType), default=SalaryType.VND, nullable=False, index=True
    )
    quantity = Column(Integer, default=1, nullable=False, index=True)
    full_name_contact = Column(String(50), nullable=False)
    phone_number_contact = Column(String(10), nullable=False)
    email_contact = Column(JSON, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, index=True)
    employment_type = Column(Enum(JobType), default=JobType.FULL_TIME, index=True)
    gender_requirement = Column(Enum(Gender), default=Gender.OTHER, index=True)
    deadline = Column(Date, nullable=False, index=True)
    employer_verified = Column(Boolean, default=False)
    is_job_flash = Column(Boolean, default=False)
    working_time_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    business = relationship("Business", back_populates="job", uselist=False)
    job_experience = relationship("JobExperience", back_populates="job", uselist=False)
    job_approval_request = relationship(
        "JobApprovalRequest", back_populates="job", uselist=False
    )
    must_have_skills = relationship(
        "Skill", secondary="job_skill", overlaps="job_skill_secondary,must_have_skills"
    )
    should_have_skills = relationship(
        "Skill", secondary="job_skill", overlaps="job_skill_secondary,must_have_skills"
    )
    job_categories = relationship(
        "Category", secondary="job_category", overlaps="job_category_secondary"
    )
    job_reports = relationship("JobReport", back_populates="job")
    user_job_save = relationship("UserJobSave", back_populates="job")
    working_times = relationship("WorkingTime", back_populates="job")
    campaign = relationship("Campaign", back_populates="job")
    work_locations = relationship("WorkLocation", back_populates="job", uselist=True)

    job_category_secondary = relationship(
        "JobCategory", back_populates="job", uselist=True, overlaps="job_categories"
    )
    job_skill_secondary = relationship(
        "JobSkill",
        back_populates="job",
        uselist=True,
        overlaps="must_have_skills,should_have_skills",
    )
    approval_log = relationship("ApprovalLog", back_populates="job")

    __table_args__ = (
        Index(
            "idx_job_min_salary_max_salary_salary_type_deadline",
            min_salary,
            max_salary,
            salary_type,
            deadline,
        ),
        Index(
            "idx_job_salary_status_dealine", min_salary, max_salary, status, deadline
        ),
    )


@event.listens_for(Job, "after_insert")
def receive_after_insert(mapper, connection, target):
    session = Session(bind=connection)
    # if target.status != JobStatus.DRAFT:
    #     job_approval_request = JobApprovalRequest(job_id=target.id)
    #     session.add(job_approval_request)
    #     session.commit()
    #     session.close()


@event.listens_for(Job.status, "set")
def receive_after_update(target, value, oldvalue, initiator):
    session = Session.object_session(target)

    if session is None:
        return

    try:
        if oldvalue == JobStatus.PUBLISHED and value != JobStatus.PUBLISHED:
            job_position = (
                session.query(JobPosition).filter_by(id=target.job_position_id).first()
            )
            if job_position.count is not None:
                job_position.count -= 1

            job_categories = (
                session.query(JobCategory).filter_by(job_id=target.id).all()
            )
            for item in job_categories:
                category = (
                    session.query(Category).filter_by(id=item.category_id).first()
                )
                if category:
                    category.count -= 1

        elif value == JobStatus.PUBLISHED and oldvalue != JobStatus.PUBLISHED:
            job_position = (
                session.query(JobPosition).filter_by(id=target.job_position_id).first()
            )

            if job_position.count is not None:
                job_position.count += 1

            job_categories = (
                session.query(JobCategory).filter_by(job_id=target.id).all()
            )
            for item in job_categories:
                category = (
                    session.query(Category).filter_by(id=item.category_id).first()
                )
                if category:
                    category.count += 1

    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.commit()


@event.listens_for(Job, "before_delete")
def receive_before_delete(mapper, connection, target):
    session = Session(bind=connection)
    try:
        job_position = (
            session.query(JobPosition).filter_by(id=target.job_position_id).first()
        )
        job_position.count -= 1
    except:
        pass
    job_category = session.query(JobCategory).filter_by(job_id=target.id).all()
    for item in job_category:
        try:
            category = session.query(Category).filter_by(id=item.category_id).first()
            category.count -= 1
        except:
            pass
    session.commit()
    session.close()
