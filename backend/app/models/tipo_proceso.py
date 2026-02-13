from sqlalchemy import Column, Integer, String, SmallInteger
from app.core.database import Base


class TipoDeProceso(Base):
    __tablename__ = "tipo_de_proceso"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    campos = Column(String(255), nullable=False, default="")
    activo = Column(SmallInteger, nullable=False, default=1)


class UnidadNegocioTipoProceso(Base):
    __tablename__ = "unidadnegocio_tipo_proceso"

    un_id = Column(Integer, primary_key=True)
    tipo_proceso_id = Column(Integer, primary_key=True)
