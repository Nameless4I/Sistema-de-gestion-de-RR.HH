from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.departamento import Departamento
from app.models.usuario import Usuario
from app.schemas.departamento import DepartamentoCreate, DepartamentoUpdate, DepartamentoResponse
from app.auth.dependencies import get_usuario_actual, requiere_rol

router = APIRouter(prefix="/api/departamentos", tags=["Departamentos"])

@router.get("", response_model=list[DepartamentoResponse])
def listar_departamentos(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    return db.query(Departamento).all()

@router.get("/{departamento_id}", response_model=DepartamentoResponse)
def obtener_departamento(
    departamento_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return departamento

@router.post("", response_model=DepartamentoResponse, status_code=status.HTTP_201_CREATED)
def crear_departamento(
    datos: DepartamentoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_rol("ADMIN"))
):
    if db.query(Departamento).filter(Departamento.nombre == datos.nombre).first():
        raise HTTPException(status_code=400, detail="Ya existe un departamento con ese nombre")

    nuevo = Departamento(**datos.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@router.put("/{departamento_id}", response_model=DepartamentoResponse)
def actualizar_departamento(
    departamento_id: int,
    datos: DepartamentoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_rol("ADMIN"))
):
    departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(departamento, campo, valor)

    db.commit()
    db.refresh(departamento)
    return departamento

@router.delete("/{departamento_id}", response_model=DepartamentoResponse)
def desactivar_departamento(
    departamento_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_rol("ADMIN"))
):
    departamento = db.query(Departamento).filter(Departamento.id == departamento_id).first()
    if not departamento:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")

    departamento.activo = False
    db.commit()
    db.refresh(departamento)
    return departamento