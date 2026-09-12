from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.usuario import Usuario
from app.models.empleado import Empleado    
from app.schemas.usuario import UsuarioCreate, UsuarioLogin, UsuarioResponse, TokenResponse
from app.auth.security import hash_password, verify_password, crear_access_token
from app.auth.dependencies import get_usuario_actual, requiere_rol

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def register(
    datos: UsuarioCreate,
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(requiere_rol("ADMIN", "RRHH"))
):
    
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    
    empleado = db.query(Empleado).filter(Empleado.id == datos.empleado_id).first()
    if not empleado:
        raise HTTPException(status_code=400, detail="El empleado indicado no existe")
    
    
    if db.query(Usuario).filter(Usuario.empleado_id == datos.empleado_id).first():
        raise HTTPException(status_code=400, detail="Este empleado ya tiene una cuenta de usuario") 
    
    
    nuevo_usuario = Usuario(
        email=datos.email,
        password_hash=hash_password(datos.password),
        empleado_id=datos.empleado_id,
        rol="EMPLEADO",
        activo=True
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@router.post("/login", response_model=TokenResponse)
def login(datos: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == datos.email).first()
    
    if not usuario or not verify_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    if not usuario.activo:
        raise HTTPException(status=403, detail="Usuario inactivo")
    
    access_token = crear_access_token(data={"sub": str(usuario.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": usuario
    }
    
@router.get("/me", response_model=UsuarioResponse)
def me(usuario_actual: Usuario = Depends(get_usuario_actual)):
    return usuario_actual