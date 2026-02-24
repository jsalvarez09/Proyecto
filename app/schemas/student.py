from pydantic import BaseModel, Field
from app.models.student import ModalidadEnum
from datetime import datetime

class StudentCreate(BaseModel):
    nombre: str
    codigo: str
    edad: int = Field(ge=15, le=60)
    promedio: float = Field(ge=0.0, le=5.0)
    trabaja: bool = False
    recien_graduado: bool = False
    disciplina: int = Field(ge=1, le=5)
    madurez_emocional: int = Field(ge=1, le=5)
    modalidad: ModalidadEnum

class StudentUpdate(BaseModel):
    nombre: str | None = None
    edad: int | None = Field(default=None, ge=15, le=60)
    promedio: float | None = Field(default=None, ge=0.0, le=5.0)
    trabaja: bool | None = None
    recien_graduado: bool | None = None
    disciplina: int | None = Field(default=None, ge=1, le=5)
    madurez_emocional: int | None = Field(default=None, ge=1, le=5)
    modalidad: ModalidadEnum | None = None

class StudentResponse(BaseModel):
    id: int
    nombre: str
    codigo: str
    edad: int
    promedio: float
    trabaja: bool
    recien_graduado: bool
    disciplina: int
    madurez_emocional: int
    modalidad: ModalidadEnum
    created_at: datetime

    model_config = {"from_attributes": True}