from fastapi import FastAPI
from app.database import Base, engine
from app.routes import auth, departamentos, cargos, empleados
from app.models import usuario, empleado, departamento, cargo, asistencia, vacacion


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Gestion de RRHH")

app.include_router(auth.router)
app.include_router(departamentos.router)
app.include_router(cargos.router)
app.include_router(empleados.router)


@app.get("/")
def root():
    return {"mensaje": "API de Sistema de RRHH funcionando"}