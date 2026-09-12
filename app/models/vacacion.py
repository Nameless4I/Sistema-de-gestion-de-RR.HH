from sqlalchemy import Column, BigInteger, Date, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Vacacion(Base):
    __tablename__ = "vacaciones"

    id = Column(BigInteger, primary_key=True, index=True)
    empleado_id = Column(BigInteger, ForeignKey("empleados.id"), nullable=False)
    fecha_inicio = Column(Date, nullable=False)
    fecha_fin = Column(Date, nullable=False)
    dias_tomados = Column(Integer, nullable=False)
    tipo = Column(String(20), nullable=False)  
    estado = Column(String(20), default="PENDIENTE")
    aprobado_por = Column(BigInteger, ForeignKey("usuarios.id"), nullable=True)
    observaciones = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    empleado = relationship("Empleado", foreign_keys=[empleado_id])
    aprobador = relationship("Usuario", foreign_keys=[aprobado_por])
    