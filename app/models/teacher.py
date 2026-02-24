from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.student import ModalidadEnum
from app.database import Base

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    edad = Column(Integer, nullable=False)
    rigurosidad = Column(Integer, nullable=False)
    flexibilidad = Column(Integer, nullable=False)
    carga_tareas = Column(Integer, nullable=False)
    estilo = Column(Integer, nullable=False)  # 1=amigable, 2=neutro, 3=formal
    exp_jovenes = Column(Integer, nullable=False)
    exp_adultos = Column(Integer, nullable=False)
    modalidad_preferida = Column(Enum(ModalidadEnum), nullable=False)
    is_active = Column(Boolean, default=True)

    recommendations = relationship("Recommendation", back_populates="teacher")