from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class JobExperience(Base):
    title = Column(String(50), nullable=False)
    from_year = Column(Integer, default=0, nullable=False)
    to_year = Column(Integer, default=0, nullable=False)

    job = relationship("Job", back_populates="job_experience")
