from sqlalchemy import Column, Integer, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    score = Column(Numeric(4, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint("assessment_id", "student_id", name="uq_grade"),
    )

    assessment = relationship("Assessment", back_populates="grades")
    student = relationship("Student", back_populates="grades")