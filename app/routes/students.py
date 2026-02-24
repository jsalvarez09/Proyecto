from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import RoleEnum
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.core.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/students", tags=["Estudiantes"])

@router.get("/", response_model=list[StudentResponse])
def list_students(
    search: str = None,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    query = db.query(Student)
    if search:
        query = query.filter(
            Student.nombre.ilike(f"%{search}%") |
            Student.codigo.ilike(f"%{search}%")
        )
    return query.all()

@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    data: StudentCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleEnum.ADMIN, RoleEnum.COORDINADOR))
):
    existing = db.query(Student).filter(Student.codigo == data.codigo).first()
    if existing:
        raise HTTPException(status_code=409, detail="Código de estudiante ya existe")

    student = Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return student

@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    data: StudentUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleEnum.ADMIN, RoleEnum.COORDINADOR))
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleEnum.ADMIN))
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")

    db.delete(student)
    db.commit()