from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import Base, engine
from app.routes import auth, departamentos, cargos, empleados, asistencias, vacaciones
from app.models import usuario, empleado, departamento, cargo, asistencia, vacacion

Base.metadata.create_all(bind=engine)

# Corregir columna empleado_id si tiene NOT NULL (fix para Render)
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE usuarios ALTER COLUMN empleado_id DROP NOT NULL"))
        conn.commit()
except Exception:
    pass  # Si ya está corregida, ignorar el error

app = FastAPI(title="Sistema de Gestión de RRHH")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://sistema-rrhh-frontend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(departamentos.router)
app.include_router(cargos.router)
app.include_router(empleados.router)
app.include_router(asistencias.router)
app.include_router(vacaciones.router)

# Crear admin inicial automáticamente
from app.seed import crear_admin_inicial
crear_admin_inicial()

@app.get("/")
def root():
    return {"mensaje": "API de Sistema de RRHH funcionando"}