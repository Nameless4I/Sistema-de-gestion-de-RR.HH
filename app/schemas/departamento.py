from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DepartamentoCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    jefe_id: Optional[int] = None 

class DepartamentoUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    jefe_id: Optional[int] = None

class DepartamentoResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    jefe_id: Optional[int] = None
    activo: bool
    created_at: datetime

    class Config:
        from_attributes = True