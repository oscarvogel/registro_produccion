from sqlalchemy import Boolean, Column, Integer, String, SmallInteger
from app.core.database import Base


class TipoDeProceso(Base):
    __tablename__ = "tipo_de_proceso"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    campos = Column(String(255), nullable=False, default="")
    requiere_acta = Column(Boolean, nullable=False, default=False)
    requiere_predio = Column(Boolean, nullable=False, default=False)
    requiere_rodal = Column(Boolean, nullable=False, default=False)
    activo = Column(SmallInteger, nullable=False, default=1)


class UnidadNegocioTipoProceso(Base):
    __tablename__ = "unidadnegocio_tipo_proceso"

    un_id = Column(Integer, primary_key=True)
    tipo_proceso_id = Column(Integer, primary_key=True)
