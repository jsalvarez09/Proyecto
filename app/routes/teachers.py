from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import RoleEnum
from app.models.teacher import Teacher
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherResponse
from app.core.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/teachers", tags=["Profesores"])

@router.get("/", response_model=list[TeacherResponse])
def list_teachers(
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    return db.query(Teacher).all()

@router.post("/", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher(
    data: TeacherCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleEnum.ADMIN, RoleEnum.COORDINADOR))
):
    teacher = Teacher(**data.model_dump())
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher

@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return teacher

@router.put("/{teacher_id}", response_model=TeacherResponse)
def update_teacher(
    teacher_id: int,
    data: TeacherUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleEnum.ADMIN, RoleEnum.COORDINADOR))
):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(teacher, field, value)

    db.commit()
    db.refresh(teacher)
    return teacher

@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleEnum.ADMIN))
):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")

    teacher.is_active = False
    db.commit()