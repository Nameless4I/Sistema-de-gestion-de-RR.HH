from sqlalchemy import Column, BigInteger, String, Boolean,  TIMESTAMP, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Departamento(Base):
    __tablename__ = "departamentos"

    id = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, nullable=False)
    descripcion = Column(Text, nullable=True)
    jefe_id = Column(BigInteger, ForeignKey("empleados.id"), nullable=True)
    activo = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    empleados = relationship("Empleado", back_populates="departamento", foreign_keys="[Empleado.departamento_id]")
    jefe = relationship("Empleado", foreign_keys=[jefe_id])