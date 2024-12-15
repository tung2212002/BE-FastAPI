from sqlalchemy import Column, Integer, ForeignKey, Enum, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.hepler.enum import JobLogStatus


class ApprovalLog(Base):
    job_id = Column(Integer, ForeignKey("job.id", ondelete="CASCADE"), index=True)
    admin_id = Column(Integer, ForeignKey("admin.id", ondelete="CASCADE"), index=True)
    previous_status = Column(Enum(JobLogStatus), nullable=False, index=True)
    new_status = Column(Enum(JobLogStatus), nullable=False, index=True)
    reason = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    admin = relationship(
        "Admin",
        back_populates="approval_log",
        uselist=False,
        single_parent=True,
    )

    job = relationship(
        "Job",
        back_populates="approval_log",
        uselist=False,
        single_parent=True,
    )
