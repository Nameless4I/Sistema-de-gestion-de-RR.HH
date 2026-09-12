from pydantic import BaseModel
from datetime import date, time, datetime
from decimal import Decimal
from typing import Optional
from enum import Enum


class TipoAsistenciaEnum(str, Enum):
    PRESENCIAL = "PRESENCIAL"
    REMOTO = "REMOTO"
    
class EstadoAsistenciaEnum(str, Enum):
    PRESENTE = "PRESENTE"
    AUSENTE = "AUSENTE"
    TARDANZA = "TARDANZA"
    JUSTIFICADO = "JUSTIFICADO"
    
class AsistenciaManualCreate(BaseModel):
    empleado_id: int
    fecha: date
    hora_entrada: Optional[time] = None
    hora_salida: Optional[time] = None
    tipo: TipoAsistenciaEnum
    observaciones: Optional[str] = None
    
class AsistenciaJustificar(BaseModel):
    estado: EstadoAsistenciaEnum
    observaciones: Optional[str] = None
    
class AsistenciaResponse(BaseModel):
    id: int
    empleado_id: int
    fecha: date
    hora_entrada: Optional[time]
    hora_salida: Optional[time]
    tipo: TipoAsistenciaEnum
    estado: EstadoAsistenciaEnum
    horas_trabajadas: Optional[Decimal]
    horas_extras: Optional[Decimal]
    observaciones: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True