from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from enum import Enum


class TipoDocumentoEnum(str, Enum):
    DNI = "DNI"
    CE = "CE"
    PASAPORTE = "PASAPORTE"
    
class TipoContratoEnum(str, Enum):
    INDEFINIDO = "INDEFINIDO"
    PLAZO_FIJO = "PLAZO_FIJO"
    CAS = "CAS"
    PRACTICAS = "PRACTICAS"
    
class EstadoEmpleadoEnum(str, Enum):
    ACTIVO = "ACTIVO"
    CESADO = "CESADO"
    SUSPENDIDO = "SUSPENDIDO"
    
class EmpleadoCreate(BaseModel):
    departamento_id: Optional[int] = None
    cargo_id: Optional[int] = None
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    tipo_documento: TipoDocumentoEnum
    numero_documento: str
    fecha_nacimiento: Optional[date] = None
    genero: Optional[str] = None
    telefono: Optional[str] = None
    email_personal: Optional[EmailStr] = None
    email_corporativo: Optional[EmailStr] = None
    direccion: Optional[str] = None
    fecha_contrato: date
    tipo_contrato: TipoContratoEnum
    salario: Decimal
    dias_vacaciones_disponibles: int = 0
    
    
class EmpleadoUpdate(BaseModel):
    departamento_id: Optional[int] = None
    cargo_id: Optional[int] = None
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    telefono: Optional[str] = None
    email_personal: Optional[EmailStr] = None
    direccion: Optional[str] = None
    salario: Optional[Decimal] = None
    dias_vacaciones_disponibles: Optional[int] = None
    
    
class EmpleadoContactoUpdate(BaseModel):
    telefono: Optional[str] = None
    email_personal: Optional[EmailStr] = None
    direccion: Optional[str] = None
    

class EmpleadoCese(BaseModel):
    fecha_cese: date
    motivo: str
    

class EmpleadoResponse(BaseModel):
    id: int
    departamento_id: Optional[int]
    cargo_id: Optional[int]
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str]
    tipo_documento: TipoDocumentoEnum
    numero_documento: str
    telefono: Optional[str]
    email_personal: Optional[EmailStr]
    email_corporativo: Optional[EmailStr]
    fecha_contrato: date
    fecha_cese: Optional[date]
    tipo_contrato: TipoContratoEnum
    salario: Optional[Decimal] = None
    dias_vacaciones_disponibles: int
    estado: EstadoEmpleadoEnum
    created_at: datetime
    
class EmpleadoResponse(BaseModel):
    id: int
    departamento_id: Optional[int]
    cargo_id: Optional[int]
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str]
    tipo_documento: TipoDocumentoEnum
    numero_documento: str
    telefono: Optional[str]
    email_personal: Optional[str]
    email_corporativo: Optional[str]
    fecha_contrato: date
    fecha_cese: Optional[date]
    tipo_contrato: TipoContratoEnum
    salario: Optional[Decimal] = None
    dias_vacaciones_disponibles: int
    estado: EstadoEmpleadoEnum
    tiene_usuario: Optional[bool] = False  # ← agregar esto
    email_usuario: Optional[str] = None    # ← y esto
    created_at: datetime
    
    class Config:
        from_attributes = True