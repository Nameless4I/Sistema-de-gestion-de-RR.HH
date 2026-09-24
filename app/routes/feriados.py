from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.feriado import Feriado
from app.schemas.feriado import FeriadoResponse
from app.auth.dependencies import get_usuario_actual
from app.models.usuario import Usuario

router = APIRouter(prefix="/api/feriados", tags=["Feriados"])

@router.get("", response_model=list[FeriadoResponse])
def listar_feriados(
    db: Session = Depends(get_db),
    usuario_actual: Usuario = Depends(get_usuario_actual)
):
    return db.query(Feriado).order_by(Feriado.fecha).all()