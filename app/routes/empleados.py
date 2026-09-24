from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.empleado import Empleado
from app.models.usuario import Usuario
from app.schemas.empleado import (
    EmpleadoCreate, EmpleadoUpdate, EmpleadoContactoUpdate, EmpleadoCese, EmpleadoResponse
)

from app.auth.dependencies import get_usuario_actual, requiere_rol

router = APIRouter(prefix="/api/empleados", tags=["Empleados"])


def _ocultar_campos_consultor(empleado: Empleado, usuario: Usuario) -> Empleado:
    """Si el usuario es CONSULTOR, oculta salario y numero_documento."""
    if usuario.rol == "CONSULTOR":
        empleado.salario = None
        empleado.numero_documento = "***OCULTO***"
    return empleado


@router.get("", response_model=list[EmpleadoResponse])
def listar_empleados(
    departamento_id: Optional[int] = Query(None),
    estado: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    query = db.query(Empleado)

    # JEFE solo ve su propio departamento
    if usuario_actual.rol == "JEFE":
        if not usuario_actual.empleado or not usuario_actual.empleado.departamento_id:
            raise HTTPException(status_code=403, detail="No tienes un departamento asignado")
        query = query.filter(Empleado.departamento_id == usuario_actual.empleado.departamento_id)
    elif departamento_id:
        query = query.filter(Empleado.departamento_id == departamento_id)

    if estado:
        query = query.filter(Empleado.estado == estado)

    resultados = query.all()
    resultados = [_enriquecer_empleado(e, db, usuario_actual) for e in resultados]

    if usuario_actual.rol == "CONSULTOR":
        resultados = [_ocultar_campos_consultor(e, usuario_actual) for e in resultados]

    return resultados


@router.get("/{empleado_id}", response_model=EmpleadoResponse)
def obtener_empleado(
    empleado_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    # EMPLEADO solo puede ver su propio registro
    if usuario_actual.rol == "EMPLEADO" and usuario_actual.empleado_id != empleado_id:
        raise HTTPException(status_code=403, detail="No puedes ver el registro de otro empleado")

    # JEFE solo ve empleados de su departamento
    if usuario_actual.rol == "JEFE":
        if not usuario_actual.empleado or usuario_actual.empleado.departamento_id != empleado.departamento_id:
            raise HTTPException(status_code=403, detail="Este empleado no pertenece a tu departamento")

    if usuario_actual.rol == "CONSULTOR":
        empleado = _enriquecer_empleado(empleado, db, usuario_actual)

    return empleado


@router.post("", response_model=EmpleadoResponse, status_code=status.HTTP_201_CREATED)
def crear_empleado(
    datos: EmpleadoCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_rol("ADMIN", "RRHH"))
):
    if db.query(Empleado).filter(Empleado.numero_documento == datos.numero_documento).first():
        raise HTTPException(status_code=400, detail="Ya existe un empleado con ese número de documento")

    if datos.email_corporativo and db.query(Empleado).filter(
        Empleado.email_corporativo == datos.email_corporativo
    ).first():
        raise HTTPException(status_code=400, detail="Ya existe un empleado con ese email corporativo")

    nuevo = Empleado(**datos.model_dump(), estado="ACTIVO")
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.put("/{empleado_id}", response_model=EmpleadoResponse)
def actualizar_empleado(
    empleado_id: int,
    datos: EmpleadoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_rol("ADMIN", "RRHH"))
):
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(empleado, campo, valor)

    db.commit()
    db.refresh(empleado)
    return empleado


@router.patch("/{empleado_id}/contacto", response_model=EmpleadoResponse)
def actualizar_contacto(
    empleado_id: int,
    datos: EmpleadoContactoUpdate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    if usuario_actual.rol != "EMPLEADO" or usuario_actual.empleado_id != empleado_id:
        raise HTTPException(status_code=403, detail="Solo puedes editar tus propios datos de contacto")

    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(empleado, campo, valor)

    db.commit()
    db.refresh(empleado)
    return empleado


@router.patch("/{empleado_id}/cese", response_model=EmpleadoResponse)
def cesar_empleado(
    empleado_id: int,
    datos: EmpleadoCese,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_rol("ADMIN", "RRHH"))
):
    empleado = db.query(Empleado).filter(Empleado.id == empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    if empleado.estado == "CESADO":
        raise HTTPException(status_code=400, detail="El empleado ya está cesado")

    empleado.estado = "CESADO"
    empleado.fecha_cese = datos.fecha_cese
    empleado.email_corporativo = None

    usuario_asociado = db.query(Usuario).filter(Usuario.empleado_id == empleado_id).first()
    if usuario_asociado:
        usuario_asociado.activo = False
        usuario_asociado.email = f"_cesado_{usuario_asociado.id}_{usuario_asociado.email}"
        
    

    db.commit()
    db.refresh(empleado)
    return empleado

def _enriquecer_empleado(empleado: Empleado, db: Session, usuario_actual: Usuario):
    """Agrega info de usuario al empleado si el rol lo permite."""
    if usuario_actual.rol in ["ADMIN", "RRHH"]:
        usuario = db.query(Usuario).filter(
            Usuario.empleado_id == empleado.id
        ).first()
        empleado.tiene_usuario = usuario is not None
        empleado.email_usuario = usuario.email if usuario else None
    else:
        empleado.tiene_usuario = None
        empleado.email_usuario = None
    return empleado