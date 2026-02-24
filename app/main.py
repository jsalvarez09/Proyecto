from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.models import *
from app.routes import auth, users, students, teachers, subjects
from app.routes import auth, users, students, teachers, subjects, recommendations
from app.routes import auth, users, students, teachers, subjects, recommendations, assessments



Base.metadata.create_all(bind=engine)

app = FastAPI(title="Motor de Recomendación Docente", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(students.router, prefix="/api/v1")
app.include_router(teachers.router, prefix="/api/v1")
app.include_router(subjects.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(assessments.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Motor de Recomendación Docente API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}