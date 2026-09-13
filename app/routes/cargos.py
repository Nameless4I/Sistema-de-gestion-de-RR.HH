from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.cargo import Cargo
from app.models.usuario import Usuario
from app.schemas.cargo import CargoCreate, CargoUpdate, CargoResponse
from app.auth.dependencies import get_usuario_actual, requiere_rol

router = APIRouter(prefix="/api/cargos", tags=["Cargos"])

@router.get("", response_model=list[CargoResponse])
def listar_cargos(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    return db.query(Cargo).all()

@router.get("/{cargo_id}", response_model=CargoResponse)
def obtener_cargo(
    cargo_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo no encontrado")
    return cargo

@router.post("", response_model=CargoResponse, status_code=status.HTTP_201_CREATED)
def crear_cargo(
    datos: CargoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_rol("ADMIN"))
):
    nuevo = Cargo(**datos.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{cargo_id}", response_model=CargoResponse)
def actualizar_cargo(
    cargo_id: int,
    datos: CargoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_rol("ADMIN"))
):
    cargo = db.query(Cargo).filter(Cargo.id == cargo_id).first()
    if not cargo:
        raise HTTPException(status_code=404, detail="Cargo no encontrado")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(cargo, campo, valor)

    db.commit()
    db.refresh(cargo)
    return cargo