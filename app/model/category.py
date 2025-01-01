from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Category(Base):
    name = Column(String(50), nullable=False)
    slug = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    count = Column(Integer, default=0, nullable=False)

    job_category_secondary = relationship(
        "JobCategory", back_populates="category", overlaps="categories"
    )