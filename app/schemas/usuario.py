from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional
from enum import Enum

class RolEnum(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    JEFE = "JEFE"
    EMPLEADO = "EMPLEADO"
    CONSULTOR = "CONSULTOR"
    
class UsuarioCreate(BaseModel):
    email: EmailStr
    password: str
    empleado_id: int
    
    @field_validator("password")
    def password_minima(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v
    
class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class UsuarioResponse(BaseModel):
    id: int
    email: str
    rol: RolEnum
    activo: bool
    created_at: datetime
    
    
    
    class config:
        from_attributes = True
        
        
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    usuario: UsuarioResponse
    
    