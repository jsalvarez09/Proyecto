from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base

class ModalidadEnum(str, enum.Enum):
    presencial = "presencial"
    virtual = "virtual"
    mixta = "mixta"

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    codigo = Column(String(20), unique=True, nullable=False, index=True)
    edad = Column(Integer, nullable=False)
    promedio = Column(Numeric(3, 2), nullable=False)
    trabaja = Column(Boolean, default=False)
    recien_graduado = Column(Boolean, default=False)
    disciplina = Column(Integer, nullable=False)
    madurez_emocional = Column(Integer, nullable=False)
    modalidad = Column(Enum(ModalidadEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    enrollments = relationship("Enrollment", back_populates="student")
    grades = relationship("Grade", back_populates="student")