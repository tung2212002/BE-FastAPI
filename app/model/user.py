from sqlalchemy import Column, String, Enum, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.hepler.enum import Gender


class User(Base):
    id = Column(Integer, ForeignKey("account.id", ondelete="CASCADE"), primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    phone_number = Column(String(10), nullable=True)
    gender = Column(Enum(Gender), nullable=True)
    count_job_apply = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    hashed_password = Column(String(255), nullable=True)

    user_job_save = relationship("UserJobSave", back_populates="user")
    cv_applications = relationship("CVApplication", back_populates="user")
    job_reports = relationship("JobReport", back_populates="user")
    social_network = relationship("SocialNetwork", back_populates="user")
    account = relationship("Account", back_populates="user")
