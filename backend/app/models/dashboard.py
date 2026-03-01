from sqlalchemy import Column, Integer, String, SmallInteger, Enum as SAEnum
from app.core.database import Base


class KpiDefinicion(Base):
    __tablename__ = "kpi_definicion"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    campo_origen = Column(String(80), nullable=False)
    agregacion = Column(SAEnum("SUM", "AVG", "COUNT", "MAX", "CUSTOM", name="agregacion_enum"), nullable=False, default="SUM")
    unidad = Column(String(20), nullable=False, default="")
    icono = Column(String(50), nullable=False, default="")
    descripcion = Column(String(255), nullable=False, default="")
    activo = Column(SmallInteger, nullable=False, default=1)


class TipoProcesoKpi(Base):
    __tablename__ = "tipo_proceso_kpi"

    tipo_proceso_id = Column(Integer, primary_key=True)
    kpi_id = Column(Integer, primary_key=True)
    orden = Column(SmallInteger, nullable=False, default=0)
    es_principal = Column(SmallInteger, nullable=False, default=0)
