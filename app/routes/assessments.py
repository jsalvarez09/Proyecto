from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import RoleEnum
from app.models.subject import Subject
from app.models.assessment import Assessment
from app.models.grade import Grade
from app.models.enrollment import Enrollment
from app.schemas.assessment import AssessmentCreate, AssessmentUpdate, AssessmentResponse
from app.schemas.grade import GradeCreate, GradeUpdate, GradeResponse, StudentGradeResponse
from app.core.dependencies import get_current_user, require_roles
from decimal import Decimal

router = APIRouter(tags=["Evaluaciones y Notas"])

# ─── ASSESSMENTS ───

@router.get("/subjects/{subject_id}/assessments", response_model=list[AssessmentResponse])
def list_assessments(
    subject_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")
    return subject.assessments

@router.post("/subjects/{subject_id}/assessments", response_model=AssessmentResponse, status_code=201)
def create_assessment(
    subject_id: int,
    data: AssessmentCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleEnum.ADMIN, RoleEnum.COORDINADOR, RoleEnum.PROFESOR))
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    # Validar que no supere 100% al agregar
    total_actual = sum(float(a.weight_percent) for a in subject.assessments)
    if total_actual + data.weight_percent > 100:
        raise HTTPException(
            status_code=400,
            detail=f"La suma de pesos supera 100%. Disponible: {100 - total_actual:.1f}%"
        )

    assessment = Assessment(subject_id=subject_id, **data.model_dump())
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment

@router.put("/subjects/{subject_id}/assessments/{assessment_id}", response_model=AssessmentResponse)
def update_assessment(
    subject_id: int,
    assessment_id: int,
    data: AssessmentUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleEnum.ADMIN, RoleEnum.COORDINADOR, RoleEnum.PROFESOR))
):
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.subject_id == subject_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    if data.weight_percent is not None:
        subject = db.query(Subject).filter(Subject.id == subject_id).first()
        total_otros = sum(
            float(a.weight_percent) for a in subject.assessments
            if a.id != assessment_id
        )
        if total_otros + data.weight_percent > 100:
            raise HTTPException(
                status_code=400,
                detail=f"La suma de pesos supera 100%. Disponible: {100 - total_otros:.1f}%"
            )

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(assessment, field, value)

    db.commit()
    db.refresh(assessment)
    return assessment

@router.delete("/subjects/{subject_id}/assessments/{assessment_id}", status_code=204)
def delete_assessment(
    subject_id: int,
    assessment_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleEnum.ADMIN, RoleEnum.COORDINADOR, RoleEnum.PROFESOR))
):
    assessment = db.query(Assessment).filter(
        Assessment.id == assessment_id,
        Assessment.subject_id == subject_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Evaluación no encontrada")

    db.delete(assessment)
    db.commit()

@router.get("/subjects/{subject_id}/assessments/validate-weights")
def validate_weights(
    subject_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    total = sum(float(a.weight_percent) for a in subject.assessments)
    return {
        "total_weight": round(total, 2),
        "is_valid": abs(total - 100) < 0.01,
        "remaining": round(100 - total, 2)
    }

# ─── GRADES ───

@router.post("/grades", response_model=GradeResponse, status_code=201)
def register_grade(
    data: GradeCreate,
    db: Session = Depends(get_db),
    _=Depends(require_roles(RoleEnum.ADMIN, RoleEnum.COORDINADOR, RoleEnum.PROFESOR))
):
    existing = db.query(Grade).filter(
        Grade.assessment_id == data.assessment_id,
        Grade.student_id == data.student_id
    ).first()

    if existing:
        # Actualizar si ya existe
        existing.score = data.score
        db.commit()
        db.refresh(existing)
        return existing

    grade = Grade(**data.model_dump())
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade

@router.get("/subjects/{subject_id}/grades")
def list_grades_by_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    enrollments = db.query(Enrollment).filter(Enrollment.subject_id == subject_id).all()
    assessments = subject.assessments

    resultado = []
    for enrollment in enrollments:
        student = enrollment.student
        row = {
            "student_id": student.id,
            "student_nombre": student.nombre,
            "student_codigo": student.codigo,
            "notas": {},
            "nota_final": None
        }

        total_peso = 0
        nota_ponderada = 0
        todas_ingresadas = True

        for assessment in assessments:
            grade = db.query(Grade).filter(
                Grade.assessment_id == assessment.id,
                Grade.student_id == student.id
            ).first()

            if grade:
                score = float(grade.score)
                peso = float(assessment.weight_percent) / 100
                row["notas"][assessment.name] = {
                    "score": score,
                    "weight": float(assessment.weight_percent)
                }
                nota_ponderada += score * peso
                total_peso += peso
            else:
                row["notas"][assessment.name] = {
                    "score": None,
                    "weight": float(assessment.weight_percent)
                }
                todas_ingresadas = False

        if todas_ingresadas and assessments:
            row["nota_final"] = round(nota_ponderada, 2)

        resultado.append(row)

    # Ranking: ordenar por nota final descendente
    resultado.sort(key=lambda x: x["nota_final"] if x["nota_final"] is not None else -1, reverse=True)

    return {
        "subject": subject.nombre,
        "assessments": [{"id": a.id, "name": a.name, "weight": float(a.weight_percent)} for a in assessments],
        "grades": resultado
    }

@router.get("/me/grades")
def my_grades(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(RoleEnum.ESTUDIANTE))
):
    # Buscar el estudiante vinculado por email
    from app.models.student import Student
    student = db.query(Student).filter(Student.codigo == current_user.email).first()

    # Si no hay match por email, buscar enrollments por nombre
    enrollments = db.query(Enrollment).all()
    student_ids = [e.student_id for e in enrollments]

    # Obtener todos los enrollments del estudiante
    my_enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == (student.id if student else -1)
    ).all()

    resultado = []
    for enrollment in my_enrollments:
        subject = enrollment.subject
        assessments = subject.assessments

        notas = []
        nota_ponderada = 0
        completo = True
        total_peso = sum(float(a.weight_percent) for a in assessments)

        for assessment in assessments:
            grade = db.query(Grade).filter(
                Grade.assessment_id == assessment.id,
                Grade.student_id == enrollment.student_id
            ).first()

            notas.append({
                "evaluacion": assessment.name,
                "peso": float(assessment.weight_percent),
                "score": float(grade.score) if grade else None
            })

            if grade:
                nota_ponderada += float(grade.score) * (float(assessment.weight_percent) / 100)
            else:
                completo = False

        resultado.append({
            "materia": subject.nombre,
            "codigo_materia": subject.codigo,
            "semestre": subject.semestre,
            "evaluaciones": notas,
            "nota_final": round(nota_ponderada, 2) if completo and abs(total_peso - 100) < 0.01 else None
        })

    return {"estudiante": current_user.full_name, "materias": resultado}


@router.get("/subjects/{subject_id}/final-grades")
def final_grades(
    subject_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    # Validar que los pesos sumen 100
    total_peso = sum(float(a.weight_percent) for a in subject.assessments)
    if abs(total_peso - 100) > 0.01:
        raise HTTPException(
            status_code=400,
            detail=f"Los pesos no suman 100%. Total actual: {total_peso:.1f}%"
        )

    enrollments = db.query(Enrollment).filter(Enrollment.subject_id == subject_id).all()
    resultado = []

    for enrollment in enrollments:
        student = enrollment.student
        nota_final = 0
        completo = True

        for assessment in subject.assessments:
            grade = db.query(Grade).filter(
                Grade.assessment_id == assessment.id,
                Grade.student_id == student.id
            ).first()

            if not grade:
                completo = False
                break

            nota_final += float(grade.score) * (float(assessment.weight_percent) / 100)

        resultado.append({
            "student_id": student.id,
            "student_nombre": student.nombre,
            "student_codigo": student.codigo,
            "nota_final": round(nota_final, 2) if completo else None,
            "completo": completo
        })

    resultado.sort(key=lambda x: x["nota_final"] if x["nota_final"] else -1, reverse=True)
    for i, r in enumerate(resultado):
        r["ranking"] = i + 1 if r["nota_final"] else None

    return {"subject": subject.nombre, "ranking": resultado}