from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    weight_percent = Column(Numeric(5, 2), nullable=False)

    subject = relationship("Subject", back_populates="assessments")
    grades = relationship("Grade", back_populates="assessment", cascade="all, delete")