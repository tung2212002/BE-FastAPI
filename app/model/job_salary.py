from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class JobSalary(Base):
    salary = Column(Integer, unique=True, nullable=False)