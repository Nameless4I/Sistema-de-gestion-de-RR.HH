from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional
from app.database import get_db
from app.models.asistencia import Asistencia
from app.models.vacacion import Vacacion
from app.models.empleado import Empleado
from app.models.usuario import Usuario
from app.schemas.asistencia import (
    AsistenciaManualCreate, AsistenciaJustificar, AsistenciaResponse
)
from app.auth.dependencies import get_usuario_actual, requiere_rol

router = APIRouter(prefix="/api/asistencias", tags=["Asistencias"])

HORA_LIMITE_TARDANZA = time(8, 15)
JORNADA_HORAS = Decimal("8.0")


def _calcular_horas(hora_entrada: time, hora_salida: time) -> tuple[Decimal, Decimal]:
    """Devuelve (horas_trabajadas, horas_extras)."""
    entrada_dt = datetime.combine(date.today(), hora_entrada)
    salida_dt = datetime.combine(date.today(), hora_salida)
    delta = salida_dt - entrada_dt
    horas = Decimal(delta.total_seconds()) / Decimal(3600)
    horas = round(horas, 2)
    extras = max(Decimal("0"), horas - JORNADA_HORAS)
    return horas, round(extras, 2)


@router.post("/marcar-entrada", response_model=AsistenciaResponse, status_code=status.HTTP_201_CREATED)
def marcar_entrada(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    if not usuario_actual.empleado_id:
        raise HTTPException(status_code=400, detail="Tu usuario no está asociado a un empleado")

    hoy = date.today()

    # Regla: no puede marcar si tiene vacación aprobada que cubre hoy
    vacacion_activa = db.query(Vacacion).filter(
        Vacacion.empleado_id == usuario_actual.empleado_id,
        Vacacion.estado == "APROBADO",
        Vacacion.fecha_inicio <= hoy,
        Vacacion.fecha_fin >= hoy
    ).first()
    if vacacion_activa:
        raise HTTPException(status_code=403, detail="Estás de vacaciones aprobadas en esta fecha")

    # No puede marcar entrada dos veces el mismo día
    existente = db.query(Asistencia).filter(
        Asistencia.empleado_id == usuario_actual.empleado_id,
        Asistencia.fecha == hoy
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya registraste tu entrada hoy")

    ahora = datetime.now().time()
    estado = "TARDANZA" if ahora > HORA_LIMITE_TARDANZA else "PRESENTE"

    nueva = Asistencia(
        empleado_id=usuario_actual.empleado_id,
        fecha=hoy,
        hora_entrada=ahora,
        tipo="PRESENCIAL",
        estado=estado
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@router.patch("/marcar-salida", response_model=AsistenciaResponse)
def marcar_salida(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    if not usuario_actual.empleado_id:
        raise HTTPException(status_code=400, detail="Tu usuario no está asociado a un empleado")

    hoy = date.today()
    asistencia = db.query(Asistencia).filter(
        Asistencia.empleado_id == usuario_actual.empleado_id,
        Asistencia.fecha == hoy
    ).first()

    if not asistencia:
        raise HTTPException(status_code=400, detail="No registraste tu entrada hoy")
    if asistencia.hora_salida:
        raise HTTPException(status_code=400, detail="Ya registraste tu salida hoy")

    ahora = datetime.now().time()
    asistencia.hora_salida = ahora
    asistencia.horas_trabajadas, asistencia.horas_extras = _calcular_horas(
        asistencia.hora_entrada, ahora
    )

    db.commit()
    db.refresh(asistencia)
    return asistencia


@router.get("", response_model=list[AsistenciaResponse])
def listar_asistencias(
    empleado_id: Optional[int] = Query(None),
    fecha_inicio: Optional[date] = Query(None),
    fecha_fin: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    query = db.query(Asistencia)

    if usuario_actual.rol == "EMPLEADO":
        query = query.filter(Asistencia.empleado_id == usuario_actual.empleado_id)
    elif usuario_actual.rol == "JEFE":
        if not usuario_actual.empleado or not usuario_actual.empleado.departamento_id:
            raise HTTPException(status_code=403, detail="No tienes un departamento asignado")
        ids_equipo = [
            e.id for e in db.query(Empleado).filter(
                Empleado.departamento_id == usuario_actual.empleado.departamento_id
            ).all()
        ]
        query = query.filter(Asistencia.empleado_id.in_(ids_equipo))
    elif empleado_id:
        query = query.filter(Asistencia.empleado_id == empleado_id)

    if fecha_inicio:
        query = query.filter(Asistencia.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(Asistencia.fecha <= fecha_fin)

    return query.all()


@router.get("/{asistencia_id}", response_model=AsistenciaResponse)
def obtener_asistencia(
    asistencia_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    asistencia = db.query(Asistencia).filter(Asistencia.id == asistencia_id).first()
    if not asistencia:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")

    if usuario_actual.rol == "EMPLEADO" and asistencia.empleado_id != usuario_actual.empleado_id:
        raise HTTPException(status_code=403, detail="No puedes ver asistencias de otro empleado")

    return asistencia


@router.patch("/{asistencia_id}/justificar", response_model=AsistenciaResponse)
def justificar_asistencia(
    asistencia_id: int,
    datos: AsistenciaJustificar,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_rol("ADMIN", "RRHH"))
):
    asistencia = db.query(Asistencia).filter(Asistencia.id == asistencia_id).first()
    if not asistencia:
        raise HTTPException(status_code=404, detail="Asistencia no encontrada")

    asistencia.estado = datos.estado
    if datos.observaciones:
        asistencia.observaciones = datos.observaciones

    db.commit()
    db.refresh(asistencia)
    return asistencia


@router.post("/manual", response_model=AsistenciaResponse, status_code=status.HTTP_201_CREATED)
def crear_asistencia_manual(
    datos: AsistenciaManualCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_rol("ADMIN", "RRHH"))
):
    empleado = db.query(Empleado).filter(Empleado.id == datos.empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=400, detail="El empleado indicado no existe")

    existente = db.query(Asistencia).filter(
        Asistencia.empleado_id == datos.empleado_id,
        Asistencia.fecha == datos.fecha
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe una asistencia para ese empleado en esa fecha")

    horas_trabajadas = None
    horas_extras = None
    if datos.hora_entrada and datos.hora_salida:
        horas_trabajadas, horas_extras = _calcular_horas(datos.hora_entrada, datos.hora_salida)

    estado = "PRESENTE"
    if datos.hora_entrada and datos.hora_entrada > HORA_LIMITE_TARDANZA:
        estado = "TARDANZA"

    nueva = Asistencia(
        **datos.model_dump(),
        estado=estado,
        horas_trabajadas=horas_trabajadas,
        horas_extras=horas_extras
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva