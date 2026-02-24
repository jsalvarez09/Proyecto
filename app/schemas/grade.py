from pydantic import BaseModel, Field
from typing import Optional

class GradeCreate(BaseModel):
    assessment_id: int
    student_id: int
    score: float = Field(ge=0.0, le=5.0)

class GradeUpdate(BaseModel):
    score: float = Field(ge=0.0, le=5.0)

class GradeResponse(BaseModel):
    id: int
    assessment_id: int
    student_id: int
    score: float

    model_config = {"from_attributes": True}

class StudentGradeResponse(BaseModel):
    student_id: int
    student_nombre: str
    student_codigo: str
    score: Optional[float] = None