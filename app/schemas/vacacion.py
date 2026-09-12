from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Optional
from enum import Enum


class TipoVacacionEnum(str, Enum):
    ANUAL = "ANUAL"
    ANTICIPADO = "ANTICIPADO"
    COMPENSADO = "COMPENSADO"
    
    
class EstadoVacacionEnum(str, Enum):
    PENDIENTE = "PENDIENTE"
    APROBADO = "APROBADO"
    RECHAZADO = "RECHAZADO"
    GOZADO = "GOZADO"
    CANCELADO = "CANCELADO"
    
class VacacionCreate(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    tipo: TipoVacacionEnum
    observaciones: Optional[str] = None
    
    @field_validator("fecha_fin")
    def fecha_fin_valida(cls, v, info):
        if "fecha_inicio" in info.data and v < info.data["fecha_inicio"]:
            raise ValueError("fecha_fin no puede ser anterior a fecha_inicio")
        return v
    
class VacacionDecision(BaseModel):
    observaciones: Optional[str] = None
    
    
class VacacionResponse(BaseModel):
    id: int
    empleado_id: int
    fecha_inicio: date
    fecha_fin: date
    dias_tomados: int
    tipo: TipoVacacionEnum
    estado: EstadoVacacionEnum
    aprobado_por: Optional[int]
    observaciones: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True