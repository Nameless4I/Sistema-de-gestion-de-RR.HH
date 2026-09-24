from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, timedelta
from typing import Optional
from app.database import get_db
from app.models.vacacion import Vacacion
from app.models.empleado import Empleado
from app.models.usuario import Usuario
from app.models.feriado import Feriado
from app.schemas.vacacion import VacacionCreate, VacacionDecision, VacacionResponse
from app.auth.dependencies import get_usuario_actual, requiere_rol

router = APIRouter(prefix="/api/vacaciones", tags=["Vacaciones"])


def calcular_dias_con_feriados(fecha_inicio: date, fecha_fin: date, db: Session) -> tuple[int, list]:
    """
    Calcula los días de vacaciones a descontar:
    """
    dias_base = (fecha_fin - fecha_inicio).days + 1

    feriados_en_rango = db.query(Feriado).filter(
        Feriado.fecha >= fecha_inicio,
        Feriado.fecha <= fecha_fin
    ).all()

    feriados_contiguos = []
    dia_siguiente = fecha_fin + timedelta(days=1)

    while True:
        feriado_contiguo = db.query(Feriado).filter(
            Feriado.fecha == dia_siguiente
        ).first()
        if feriado_contiguo:
            feriados_contiguos.append(feriado_contiguo)
            dia_siguiente += timedelta(days=1)
        else:
            break

    total_dias = dias_base + len(feriados_contiguos)
    todos_feriados = feriados_en_rango + feriados_contiguos
    return total_dias, todos_feriados


def _verificar_scope_jefe(usuario: Usuario, empleado: Empleado, db: Session):
    """Verifica que un JEFE solo gestione empleados de su departamento."""
    if not usuario.empleado or usuario.empleado.departamento_id != empleado.departamento_id:
        raise HTTPException(status_code=403, detail="Este empleado no pertenece a tu departamento")


@router.post("", response_model=VacacionResponse, status_code=status.HTTP_201_CREATED)
def solicitar_vacacion(
    datos: VacacionCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    if not usuario_actual.empleado_id:
        raise HTTPException(status_code=400, detail="Tu usuario no está asociado a un empleado")

    empleado = db.query(Empleado).filter(Empleado.id == usuario_actual.empleado_id).first()

    # Calcular días con feriados contiguos
    dias_tomados, feriados_incluidos = calcular_dias_con_feriados(
        datos.fecha_inicio, datos.fecha_fin, db
    )

    # Verificar días disponibles
    if dias_tomados > empleado.dias_vacaciones_disponibles:
        detalle = f"No tienes suficientes días. Tienes {empleado.dias_vacaciones_disponibles} días disponibles, esta solicitud consume {dias_tomados} días"
        if feriados_incluidos:
            nombres = ', '.join([f.descripcion for f in feriados_incluidos])
            detalle += f" (incluye feriados: {nombres})"
        raise HTTPException(status_code=400, detail=detalle)

    # Verificar solapamiento
    solapamiento = db.query(Vacacion).filter(
        Vacacion.empleado_id == usuario_actual.empleado_id,
        Vacacion.estado.in_(["PENDIENTE", "APROBADO"]),
        Vacacion.fecha_inicio <= datos.fecha_fin,
        Vacacion.fecha_fin >= datos.fecha_inicio
    ).first()
    if solapamiento:
        raise HTTPException(status_code=400, detail="Ya tienes una solicitud que se solapa con esas fechas")

    nueva = Vacacion(
        empleado_id=usuario_actual.empleado_id,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        dias_tomados=dias_tomados,
        tipo=datos.tipo,
        estado="PENDIENTE",
        observaciones=datos.observaciones
    )
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


@router.get("", response_model=list[VacacionResponse])
def listar_vacaciones(
    empleado_id: Optional[int] = Query(None),
    estado: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    query = db.query(Vacacion)

    if usuario_actual.rol == "EMPLEADO":
        query = query.filter(Vacacion.empleado_id == usuario_actual.empleado_id)
    elif usuario_actual.rol == "JEFE":
        if not usuario_actual.empleado or not usuario_actual.empleado.departamento_id:
            raise HTTPException(status_code=403, detail="No tienes un departamento asignado")
        ids_equipo = [
            e.id for e in db.query(Empleado).filter(
                Empleado.departamento_id == usuario_actual.empleado.departamento_id
            ).all()
        ]
        query = query.filter(Vacacion.empleado_id.in_(ids_equipo))
    elif empleado_id:
        query = query.filter(Vacacion.empleado_id == empleado_id)

    if estado:
        query = query.filter(Vacacion.estado == estado)

    return query.all()


@router.get("/{vacacion_id}", response_model=VacacionResponse)
def obtener_vacacion(
    vacacion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    vacacion = db.query(Vacacion).filter(Vacacion.id == vacacion_id).first()
    if not vacacion:
        raise HTTPException(status_code=404, detail="Solicitud de vacación no encontrada")

    if usuario_actual.rol == "EMPLEADO" and vacacion.empleado_id != usuario_actual.empleado_id:
        raise HTTPException(status_code=403, detail="No puedes ver vacaciones de otro empleado")

    return vacacion


@router.patch("/{vacacion_id}/aprobar", response_model=VacacionResponse)
def aprobar_vacacion(
    vacacion_id: int,
    datos: VacacionDecision,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_rol("ADMIN", "RRHH", "JEFE"))
):
    vacacion = db.query(Vacacion).filter(Vacacion.id == vacacion_id).first()
    if not vacacion:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if vacacion.estado != "PENDIENTE":
        raise HTTPException(status_code=400, detail="Solo se pueden aprobar solicitudes PENDIENTE")

    empleado = db.query(Empleado).filter(Empleado.id == vacacion.empleado_id).first()

    if usuario_actual.rol == "JEFE":
        _verificar_scope_jefe(usuario_actual, empleado, db)

    empleado.dias_vacaciones_disponibles -= vacacion.dias_tomados

    vacacion.estado = "APROBADO"
    vacacion.aprobado_por = usuario_actual.id
    if datos.observaciones:
        vacacion.observaciones = datos.observaciones

    db.commit()
    db.refresh(vacacion)
    return vacacion


@router.patch("/{vacacion_id}/rechazar", response_model=VacacionResponse)
def rechazar_vacacion(
    vacacion_id: int,
    datos: VacacionDecision,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_rol("ADMIN", "RRHH", "JEFE"))
):
    vacacion = db.query(Vacacion).filter(Vacacion.id == vacacion_id).first()
    if not vacacion:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if vacacion.estado != "PENDIENTE":
        raise HTTPException(status_code=400, detail="Solo se pueden rechazar solicitudes PENDIENTE")

    empleado = db.query(Empleado).filter(Empleado.id == vacacion.empleado_id).first()

    if usuario_actual.rol == "JEFE":
        _verificar_scope_jefe(usuario_actual, empleado, db)

    vacacion.estado = "RECHAZADO"
    vacacion.aprobado_por = usuario_actual.id
    if datos.observaciones:
        vacacion.observaciones = datos.observaciones

    db.commit()
    db.refresh(vacacion)
    return vacacion


@router.patch("/{vacacion_id}/cancelar", response_model=VacacionResponse)
def cancelar_vacacion(
    vacacion_id: int,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    if usuario_actual.rol != "EMPLEADO":
        raise HTTPException(status_code=403, detail="Solo el propio empleado puede cancelar su solicitud")

    vacacion = db.query(Vacacion).filter(Vacacion.id == vacacion_id).first()
    if not vacacion:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")

    if vacacion.empleado_id != usuario_actual.empleado_id:
        raise HTTPException(status_code=403, detail="No puedes cancelar vacaciones de otro empleado")

    if vacacion.estado not in ["PENDIENTE", "APROBADO"]:
        raise HTTPException(status_code=400, detail="Solo se pueden cancelar solicitudes PENDIENTE o APROBADO")

    if vacacion.estado == "APROBADO" and vacacion.fecha_inicio <= date.today():
        raise HTTPException(status_code=400, detail="No puedes cancelar unas vacaciones que ya comenzaron")

    if vacacion.estado == "APROBADO":
        empleado = db.query(Empleado).filter(Empleado.id == vacacion.empleado_id).first()
        empleado.dias_vacaciones_disponibles += vacacion.dias_tomados

    vacacion.estado = "CANCELADO"
    db.commit()
    db.refresh(vacacion)
    return vacacion