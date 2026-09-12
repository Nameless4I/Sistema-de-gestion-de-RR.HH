from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth
from app.models import usuario, empleado, departamento, cargo, asistencia, vacacion

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Gestion de RRHH")

app.include_router(auth.router)


@app.get("/")
def root():
    return {"mensaje": "API de Sistema de RRHH funcionando"}