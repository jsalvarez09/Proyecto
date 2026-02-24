def crear_materia_con_estudiante(client, db, token):
    from app.models.student import Student, ModalidadEnum
    from app.models.subject import Subject
    from app.models.enrollment import Enrollment
    from app.models.user import User

    user = db.query(User).first()

    student = Student(
        nombre="Est Test", codigo="EST001", edad=20,
        promedio=3.5, trabaja=False, recien_graduado=False,
        disciplina=3, madurez_emocional=3, modalidad=ModalidadEnum.presencial
    )
    db.add(student)

    subject = Subject(nombre="Materia Test", codigo="MAT001",
                      semestre="2026-1", created_by=user.id)
    db.add(subject)
    db.commit()

    enrollment = Enrollment(subject_id=subject.id, student_id=student.id)
    db.add(enrollment)
    db.commit()

    return subject, student

def test_suma_pesos_supera_100(client, admin_token, db):
    subject, _ = crear_materia_con_estudiante(client, db, admin_token)
    headers = {"Authorization": f"Bearer {admin_token}"}

    client.post(f"/api/v1/subjects/{subject.id}/assessments",
        headers=headers, json={"name": "Parcial 1", "weight_percent": 60})

    res = client.post(f"/api/v1/subjects/{subject.id}/assessments",
        headers=headers, json={"name": "Parcial 2", "weight_percent": 50})

    assert res.status_code == 400
    assert "supera 100%" in res.json()["detail"]

def test_no_duplicar_nota(client, admin_token, db):
    subject, student = crear_materia_con_estudiante(client, db, admin_token)
    headers = {"Authorization": f"Bearer {admin_token}"}

    res = client.post(f"/api/v1/subjects/{subject.id}/assessments",
        headers=headers, json={"name": "Parcial", "weight_percent": 100})
    assessment_id = res.json()["id"]

    # Primera nota
    client.post("/api/v1/grades", headers=headers,
        json={"assessment_id": assessment_id, "student_id": student.id, "score": 3.5})

    # Segunda nota mismo estudiante y evaluación → debe actualizar, no duplicar
    res2 = client.post("/api/v1/grades", headers=headers,
        json={"assessment_id": assessment_id, "student_id": student.id, "score": 4.0})

    assert res2.status_code == 201

    from app.models.grade import Grade
    count = db.query(Grade).filter(
        Grade.assessment_id == assessment_id,
        Grade.student_id == student.id
    ).count()
    assert count == 1

def test_nota_final_ponderada_correcta(client, admin_token, db):
    subject, student = crear_materia_con_estudiante(client, db, admin_token)
    headers = {"Authorization": f"Bearer {admin_token}"}

    a1 = client.post(f"/api/v1/subjects/{subject.id}/assessments",
        headers=headers, json={"name": "Parcial 1", "weight_percent": 60}).json()
    a2 = client.post(f"/api/v1/subjects/{subject.id}/assessments",
        headers=headers, json={"name": "Parcial 2", "weight_percent": 40}).json()

    client.post("/api/v1/grades", headers=headers,
        json={"assessment_id": a1["id"], "student_id": student.id, "score": 4.0})
    client.post("/api/v1/grades", headers=headers,
        json={"assessment_id": a2["id"], "student_id": student.id, "score": 3.0})

    res = client.get(f"/api/v1/subjects/{subject.id}/final-grades",
        headers=headers)

    assert res.status_code == 200
    ranking = res.json()["ranking"]
    # Nota esperada: 4.0 * 0.6 + 3.0 * 0.4 = 2.4 + 1.2 = 3.6
    assert ranking[0]["nota_final"] == 3.6

def test_final_grades_falla_si_pesos_no_suman_100(client, admin_token, db):
    subject, _ = crear_materia_con_estudiante(client, db, admin_token)
    headers = {"Authorization": f"Bearer {admin_token}"}

    client.post(f"/api/v1/subjects/{subject.id}/assessments",
        headers=headers, json={"name": "Parcial", "weight_percent": 70})

    res = client.get(f"/api/v1/subjects/{subject.id}/final-grades", headers=headers)
    assert res.status_code == 400
    assert "no suman 100%" in res.json()["detail"]