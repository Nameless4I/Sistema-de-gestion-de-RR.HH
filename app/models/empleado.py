from sqlalchemy import Column, BigInteger, String, Date, DECIMAL, Integer, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(BigInteger, primary_key=True, index=True)
    departamento_id = Column(BigInteger, ForeignKey("departamentos.id"), nullable=True)
    cargo_id = Column(BigInteger, ForeignKey("cargos.id"), nullable=True)
    nombre = Column(String(100), nullable=False)
    apellido_paterno = Column(String(50), nullable=False)
    apellido_materno = Column(String(50), nullable=True)
    tipo_documento = Column(String(20), nullable=False)
    numero_documento = Column(String(20), unique=True, index=True, nullable=False)
    fecha_nacimiento = Column(Date, nullable=False)
    genero = Column(String(10), nullable=True)
    telefono = Column(String(20), nullable=True)
    email_personal = Column(String(100), nullable=True)
    email_corporativo = Column(String(100), unique=True, nullable=True)
    direccion = Column(String, nullable=True)
    fecha_contrato = Column(Date, nullable=False)
    fecha_cese = Column(Date, nullable=True)
    tipo_contrato = Column(String(20), nullable=False)
    salario = Column(DECIMAL(12, 2), nullable=False)
    dias_vacaciones_disponibles = Column(Integer, default=0)
    estado = Column(String(20), default="activo")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    usuario = relationship("Usuario", back_populates="empleado", uselist=False, foreign_keys="[Usuario.empleado_id]")
    departamento = relationship("Departamento", back_populates="empleados", foreign_keys=[departamento_id])
    cargo = relationship("Cargo", back_populates="empleados")