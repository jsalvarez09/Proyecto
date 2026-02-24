from app.database import SessionLocal
from app.models.user import User, RoleEnum
from app.core.security import hash_password

db = SessionLocal()

admin = User(
    email="admin@motor.com",
    password_hash=hash_password("admin123"),
    full_name="Administrador",
    role=RoleEnum.ADMIN
)

db.add(admin)
db.commit()
print("Admin creado: admin@motor.com / admin123")
db.close()