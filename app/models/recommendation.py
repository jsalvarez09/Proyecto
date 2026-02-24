from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    recommended_teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    group_profile = Column(JSONB, nullable=False)
    weights_used = Column(JSONB, nullable=False)
    scores = Column(JSONB, nullable=False)
    top3 = Column(JSONB, nullable=False)
    justification = Column(Text, nullable=False)
    generated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)

    subject = relationship("Subject", back_populates="recommendations")
    teacher = relationship("Teacher", back_populates="recommendations")
    generated_by_user = relationship("User", back_populates="recommendations")