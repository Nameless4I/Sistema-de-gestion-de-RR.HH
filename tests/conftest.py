import os
os.environ["TESTING"] = "true"
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.auth.security import hash_password
from app.models.usuario import Usuario
from app.models.empleado import Empleado
from app.models.departamento import Departamento
from app.models.cargo import Cargo
from app.models.feriado import Feriado
from datetime import date

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:Pochita030668@localhost:5432/rrhh_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
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
    """Crea tablas antes de cada test y limpia con CASCADE después."""
    Base.metadata.create_all(bind=engine)

    # Fix: empleado_id debe ser nullable
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE usuarios ALTER COLUMN empleado_id DROP NOT NULL"))
            conn.commit()
        except Exception:
            conn.rollback()
        try:
            conn.execute(text("ALTER TABLE empleados ALTER COLUMN fecha_nacimiento DROP NOT NULL"))
            conn.commit()
        except Exception:
            conn.rollback()
    yield

    # Limpieza con CASCADE para evitar el error de dependencia circular
    with engine.connect() as conn:
        conn.execute(text("SET session_replication_role = replica"))  # desactiva FK checks
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.execute(text("SET session_replication_role = DEFAULT"))  # reactiva FK checks
        conn.commit()


@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_user(db):
    usuario = Usuario(
        email="admin@test.com",
        password_hash=hash_password("Admin12345"),
        rol="ADMIN",
        activo=True,
        empleado_id=None
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@pytest.fixture
def admin_token(client, admin_user):
    response = client.post("/api/auth/login", json={
        "email": "admin@test.com",
        "password": "Admin12345"
    })
    return response.json()["access_token"]


@pytest.fixture
def departamento(db):
    dept = Departamento(nombre="Tecnología", activo=True)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


@pytest.fixture
def cargo(db):
    c = Cargo(nombre="Desarrollador", nivel="SENIOR", salario_base=4500)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@pytest.fixture
def empleado(db, departamento, cargo):
    emp = Empleado(
        nombre="Juan",
        apellido_paterno="Pérez",
        tipo_documento="DNI",
        numero_documento="12345678",
        fecha_contrato=date(2026, 1, 1),
        tipo_contrato="INDEFINIDO",
        salario=4500,
        dias_vacaciones_disponibles=30,
        estado="ACTIVO",
        departamento_id=departamento.id,
        cargo_id=cargo.id
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


@pytest.fixture
def empleado_user(db, empleado):
    usuario = Usuario(
        email="empleado@test.com",
        password_hash=hash_password("Empleado12345"),
        rol="EMPLEADO",
        activo=True,
        empleado_id=empleado.id
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@pytest.fixture
def empleado_token(client, empleado_user):
    response = client.post("/api/auth/login", json={
        "email": "empleado@test.com",
        "password": "Empleado12345"
    })
    return response.json()["access_token"]


@pytest.fixture
def feriado_independencia(db):
    f = Feriado(fecha=date(2026, 7, 28), descripcion="Día de la Independencia")
    db.add(f)
    db.commit()
    db.refresh(f)
    return f