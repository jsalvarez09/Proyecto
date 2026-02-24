from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, RoleEnum
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.recommendation import Recommendation
from app.core.dependencies import get_current_user, require_roles
from app.services.recommendation_service import recomendar_profesor
import json

router = APIRouter(prefix="/subjects", tags=["Recomendaciones"])

@router.get("/{subject_id}/group-profile")
def get_group_profile(
    subject_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    students = [e.student for e in subject.enrollments]
    if not students:
        raise HTTPException(status_code=400, detail="La materia no tiene estudiantes inscritos")

    from app.services.recommendation_service import calcular_perfil, definir_pesos
    perfil = calcular_perfil(students)
    pesos = definir_pesos(perfil)

    return {"perfil": perfil, "pesos": pesos}

@router.post("/{subject_id}/recommend", status_code=status.HTTP_201_CREATED)
def generate_recommendation(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleEnum.ADMIN, RoleEnum.COORDINADOR))
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    students = [e.student for e in subject.enrollments]
    if not students:
        raise HTTPException(status_code=400, detail="La materia no tiene estudiantes inscritos")

    teachers = db.query(Teacher).filter(Teacher.is_active == True).all()
    if not teachers:
        raise HTTPException(status_code=400, detail="No hay profesores activos disponibles")

    resultado = recomendar_profesor(students, teachers)

    recommendation = Recommendation(
        subject_id=subject_id,
        recommended_teacher_id=resultado["recomendado"]["teacher_id"],
        group_profile=resultado["perfil_grupo"],
        weights_used=resultado["pesos_usados"],
        scores=resultado["scores"],
        top3=resultado["top3"],
        justification=resultado["justificacion"],
        generated_by=current_user.id
    )
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)

    return {
        "id": recommendation.id,
        "recomendado": resultado["recomendado"],
        "top3": resultado["top3"],
        "perfil_grupo": resultado["perfil_grupo"],
        "pesos_usados": resultado["pesos_usados"],
        "justificacion": resultado["justificacion"]
    }

@router.get("/{subject_id}/recommendations")
def list_recommendations(
    subject_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Materia no encontrada")

    recs = db.query(Recommendation).filter(
        Recommendation.subject_id == subject_id
    ).order_by(Recommendation.generated_at.desc()).all()

    return [
        {
            "id": r.id,
            "teacher_id": r.recommended_teacher_id,
            "justificacion": r.justification,
            "perfil_grupo": r.group_profile,
            "top3": r.top3,
            "generated_at": r.generated_at,
            "generated_by": r.generated_by
        }
        for r in recs
    ]

@router.get("/recommendation/{recommendation_id}")
def get_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    _=Depends(get_current_user)
):
    r = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Recomendación no encontrada")

    return {
        "id": r.id,
        "subject_id": r.subject_id,
        "teacher_id": r.recommended_teacher_id,
        "perfil_grupo": r.group_profile,
        "pesos_usados": r.weights_used,
        "scores": r.scores,
        "top3": r.top3,
        "justificacion": r.justification,
        "generated_at": r.generated_at,
        "generated_by": r.generated_by
    }