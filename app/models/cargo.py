from sqlalchemy import Column, BigInteger, String, DECIMAL, Text, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Cargo(Base):
    __tablename__ = "cargos"

    id = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    nivel = Column(String(20), nullable=True)
    salario_base = Column(DECIMAL(12, 2), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    empleados = relationship("Empleado", back_populates="cargo")