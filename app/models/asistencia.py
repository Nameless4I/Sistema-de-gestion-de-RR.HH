from sqlalchemy import Column, BigInteger, Date, Time, String, DECIMAL, Text, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Asistencia(Base):
    __tablename__ = "asistencias"

    id = Column(BigInteger, primary_key=True, index=True)
    empleado_id = Column(BigInteger, ForeignKey("empleados.id"), nullable=False)
    fecha = Column(Date, nullable=False)
    hora_entrada = Column(Time, nullable=True)
    hora_salida = Column(Time, nullable=True)
    tipo = Column(String(20), nullable=False)  
    estado = Column(String(20), nullable=False)
    horas_trabajadas = Column(DECIMAL(5, 2), nullable=True)
    observaciones = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    empleado = relationship("Empleado")
    