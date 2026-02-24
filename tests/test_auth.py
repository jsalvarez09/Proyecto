def test_login_exitoso(client, db):
    from app.models.user import User, RoleEnum
    from app.core.security import hash_password
    user = User(
        email="u@test.com",
        password_hash=hash_password("pass123"),
        full_name="Test",
        role=RoleEnum.COORDINADOR
    )
    db.add(user)
    db.commit()

    res = client.post("/api/v1/auth/login", json={
        "email": "u@test.com", "password": "pass123"
    })
    assert res.status_code == 200
    assert "access_token" in res.json()

def test_login_credenciales_incorrectas(client):
    res = client.post("/api/v1/auth/login", json={
        "email": "noexiste@test.com", "password": "wrong"
    })
    assert res.status_code == 401

def test_endpoint_protegido_sin_token(client):
    res = client.get("/api/v1/students")
    assert res.status_code == 403

def test_endpoint_protegido_con_token(client, coordinador_token):
    res = client.get("/api/v1/students",
        headers={"Authorization": f"Bearer {coordinador_token}"}
    )
    assert res.status_code == 200

def test_consultor_no_puede_crear_estudiante(client, consultor_token):
    res = client.post("/api/v1/students",
        headers={"Authorization": f"Bearer {consultor_token}"},
        json={
            "nombre": "Test", "codigo": "001", "edad": 20,
            "promedio": 3.5, "disciplina": 3, "madurez_emocional": 3,
            "modalidad": "presencial"
        }
    )
    assert res.status_code == 403