from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum

class NivelEnum(str, Enum):
    JUNIOR = "JUNIOR"
    SEMISENIOR = "SEMISENIOR"
    SENIOR = "SENIOR"
    LEAD = "LEAD"
    GERENTE = "GERENTE"
    
class CargoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    nivel: NivelEnum
    salario_base: Optional[Decimal] = None
    
    
    
class CargoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    nivel: Optional[NivelEnum] = None
    salario_base: Optional[Decimal] = None
    
class CargoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    nivel: NivelEnum
    salario_base: Decimal
    activo: bool
    created_at: datetime
    
    class Config:
        from_attributes = True