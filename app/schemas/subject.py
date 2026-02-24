from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.schemas.student import StudentResponse

class TeacherBasic(BaseModel):
    id: int
    nombre: str
    model_config = {"from_attributes": True}

class SubjectCreate(BaseModel):
    nombre: str
    codigo: str
    semestre: str
    teacher_id: Optional[int] = None

class SubjectUpdate(BaseModel):
    nombre: str | None = None
    semestre: str | None = None
    teacher_id: Optional[int] = None

class SubjectResponse(BaseModel):
    id: int
    nombre: str
    codigo: str
    semestre: str
    created_by: int
    teacher_id: Optional[int] = None
    teacher: Optional[TeacherBasic] = None
    created_at: datetime

    model_config = {"from_attributes": True}

class SubjectDetailResponse(SubjectResponse):
    students: list[StudentResponse] = []

class EnrollmentRequest(BaseModel):
    student_ids: list[int]