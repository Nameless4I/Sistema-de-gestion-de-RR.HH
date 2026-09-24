from sqlalchemy import Column, BigInteger, Date, String, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base

class Feriado(Base):
    __tablename__ = "feriados"

    id = Column(BigInteger, primary_key=True, index=True)
    fecha = Column(Date, nullable=False, unique=True, index=True)
    descripcion = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())