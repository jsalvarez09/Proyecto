from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("subject_id", "student_id", name="uq_enrollment"),
    )

    subject = relationship("Subject", back_populates="enrollments")
    student = relationship("Student", back_populates="enrollments")