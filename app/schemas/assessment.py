from pydantic import BaseModel, Field
from typing import Optional

class AssessmentCreate(BaseModel):
    name: str
    weight_percent: float = Field(gt=0, le=100)

class AssessmentUpdate(BaseModel):
    name: Optional[str] = None
    weight_percent: Optional[float] = Field(default=None, gt=0, le=100)

class AssessmentResponse(BaseModel):
    id: int
    subject_id: int
    name: str
    weight_percent: float

    model_config = {"from_attributes": True}