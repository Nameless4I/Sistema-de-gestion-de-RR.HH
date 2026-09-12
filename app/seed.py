from app.database import SessionLocal
from app.models.usuario import Usuario
from app.models import empleado, departamento, cargo, asistencia, vacacion
from app.auth.security import hash_password

def crear_admin_inicial():
    db = SessionLocal()
    try:
        existe = db.query(Usuario).filter(Usuario.email == "admin@empresa.com").first()
        if existe:
            print("El usuario admin ya existe.")
            return

        admin = Usuario(
            email="admin@empresa.com",
            password_hash=hash_password("admin"),
            empleado_id=None,
            rol="ADMIN",
            activo=True
        )
        db.add(admin)
        db.commit()
        print("Usuario ADMIN creado: admin@empresa.com / admin")
    finally:
        db.close()

if __name__ == "__main__":
    crear_admin_inicial()