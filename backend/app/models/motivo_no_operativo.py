from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, UniqueConstraint

from app.core.database import Base


class MotivoNoOperativo(Base):
    __tablename__ = "motivos_no_operativos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(40), nullable=False, unique=True)
    nombre = Column(String(80), nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class MotivoNoOperativoUnidadNegocio(Base):
    __tablename__ = "motivos_no_operativos_unidad_negocio"
    __table_args__ = (
        UniqueConstraint("idMotivo", "unidad_negocio", name="uq_motivo_no_operativo_un"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    idMotivo = Column(Integer, nullable=False)
    unidad_negocio = Column(Integer, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)
