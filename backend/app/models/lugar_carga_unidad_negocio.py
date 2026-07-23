from sqlalchemy import Boolean, Column, Integer, SmallInteger

from app.core.database import Base


class LugarCargaUnidadNegocio(Base):
    __tablename__ = "lugar_carga_unidad_negocio"

    id = Column(Integer, primary_key=True, autoincrement=True)
    idLugarCarga = Column(Integer, nullable=False)
    unidad_negocio = Column(Integer, nullable=False)
    prioridad = Column(Integer, nullable=False, default=100)
    es_default = Column(SmallInteger, nullable=False, default=0)
    activo = Column(Boolean, nullable=False, default=True)
