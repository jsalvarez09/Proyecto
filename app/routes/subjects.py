from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, RoleEnum
from app.models.subject import Subject
from app.models.student import Student
from app.models.enrollment import Enrollment
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse, SubjectDetailResponse, EnrollmentRequest
from app.core.dependencies import get_current_user, require_roles

router = APIRouter(prefix="/subjects", tags=["Materias"])

@router.get("/", response_model=list[SubjectResponse])
def list_subjects(
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    return db.query(Subject).all()

@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject(
    data: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.COORDINADOR))
):
    existing = db.query(Subject).filter(Subject.codigo == data.codigo).first()
    if existing:
        raise HTTPException(status_code=409, detail="Código de materia ya existe")

    subject = Subject(**data.model_dump(), created_by=current_user.id)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject

@router.get("/{subject_id}", response_model=SubjectDetailResponse)
def get_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    students = [e.student for e in subject.enrollments]
    return SubjectDetailResponse(
        **SubjectResponse.model_validate(subject).model_dump(),
        students=students
    )

@router.put("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: int,
    data: SubjectUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleEnum.ADMIN, RoleEnum.COORDINADOR))
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(subject, field, value)

    db.commit()
    db.refresh(subject)
    return subject

@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleEnum.ADMIN))
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    db.delete(subject)
    db.commit()

@router.get("/available", response_model=list[SubjectResponse])
def list_available_subjects(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Materias disponibles con info del profesor — para estudiantes"""
    return db.query(Subject).all()

@router.post("/{subject_id}/self-enroll", status_code=status.HTTP_201_CREATED)
def self_enroll(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.ESTUDIANTE))
):
    """El estudiante se inscribe a sí mismo buscando por su email"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    # Buscar estudiante por email
    student = db.query(Student).filter(Student.codigo == current_user.email).first()
    if not student:
        raise HTTPException(
            status_code=404,
            detail="No se encontró un perfil de estudiante vinculado a tu cuenta. Contacta al administrador."
        )

    existing = db.query(Enrollment).filter(
        Enrollment.subject_id == subject_id,
        Enrollment.student_id == student.id
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Ya estás inscrito en esta materia")

    enrollment = Enrollment(subject_id=subject_id, student_id=student.id)
    db.add(enrollment)
    db.commit()
    return {"message": "Inscripción exitosa", "subject": subject.nombre}


def enroll_students(
    subject_id: int,
    data: EnrollmentRequest,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleEnum.ADMIN, RoleEnum.COORDINADOR))
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    enrolled = []
    for student_id in data.student_ids:
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student:
            continue

        existing = db.query(Enrollment).filter(
            Enrollment.subject_id == subject_id,
            Enrollment.student_id == student_id
        ).first()
        if existing:
            continue

        enrollment = Enrollment(subject_id=subject_id, student_id=student_id)
        db.add(enrollment)
        enrolled.append(student_id)

    db.commit()
    return {"enrolled": enrolled, "total": len(enrolled)}

@router.delete("/{subject_id}/enrollments/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_enrollment(
    subject_id: int,
    student_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleEnum.ADMIN, RoleEnum.COORDINADOR))
):
    enrollment = db.query(Enrollment).filter(
        Enrollment.subject_id == subject_id,
        Enrollment.student_id == student_id
    ).first()
    if not enrollment:
        raise HTTPException(status_code=404, detail="Inscripción no encontrada")

    db.delete(enrollment)
    db.commit()