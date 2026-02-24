import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models.user import User, RoleEnum
from app.core.security import hash_password

# BD en memoria para tests
SQLALCHEMY_TEST_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_TEST_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db():
    db = TestingSessionLocal()
    yield db
    db.close()

@pytest.fixture
def admin_token(client, db):
    admin = User(
        email="admin@test.com",
        password_hash=hash_password("admin123"),
        full_name="Admin Test",
        role=RoleEnum.ADMIN
    )
    db.add(admin)
    db.commit()

    res = client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    })
    return res.json()["access_token"]

@pytest.fixture
def coordinador_token(client, db):
    user = User(
        email="coord@test.com",
        password_hash=hash_password("coord123"),
        full_name="Coordinador Test",
        role=RoleEnum.COORDINADOR
    )
    db.add(user)
    db.commit()

    res = client.post("/api/v1/auth/login", json={
        "email": "coord@test.com",
        "password": "coord123"
    })
    return res.json()["access_token"]

@pytest.fixture
def consultor_token(client, db):
    user = User(
        email="consultor@test.com",
        password_hash=hash_password("cons123"),
        full_name="Consultor Test",
        role=RoleEnum.CONSULTOR
    )
    db.add(user)
    db.commit()

    res = client.post("/api/v1/auth/login", json={
        "email": "consultor@test.com",
        "password": "cons123"
    })
    return res.json()["access_token"]