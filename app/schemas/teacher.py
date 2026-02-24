from pydantic import BaseModel, Field
from app.models.student import ModalidadEnum

class TeacherCreate(BaseModel):
    nombre: str
    edad: int = Field(ge=25, le=70)
    rigurosidad: int = Field(ge=1, le=5)
    flexibilidad: int = Field(ge=1, le=5)
    carga_tareas: int = Field(ge=1, le=5)
    estilo: int = Field(ge=1, le=3)
    exp_jovenes: int = Field(ge=1, le=5)
    exp_adultos: int = Field(ge=1, le=5)
    modalidad_preferida: ModalidadEnum
    is_active: bool = True

class TeacherUpdate(BaseModel):
    nombre: str | None = None
    edad: int | None = Field(default=None, ge=25, le=70)
    rigurosidad: int | None = Field(default=None, ge=1, le=5)
    flexibilidad: int | None = Field(default=None, ge=1, le=5)
    carga_tareas: int | None = Field(default=None, ge=1, le=5)
    estilo: int | None = Field(default=None, ge=1, le=3)
    exp_jovenes: int | None = Field(default=None, ge=1, le=5)
    exp_adultos: int | None = Field(default=None, ge=1, le=5)
    modalidad_preferida: ModalidadEnum | None = None
    is_active: bool | None = None

class TeacherResponse(BaseModel):
    id: int
    nombre: str
    edad: int
    rigurosidad: int
    flexibilidad: int
    carga_tareas: int
    estilo: int
    exp_jovenes: int
    exp_adultos: int
    modalidad_preferida: ModalidadEnum
    is_active: bool

    model_config = {"from_attributes": True}