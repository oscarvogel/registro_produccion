from sqlalchemy import Column, Integer, String, Date, Float, SmallInteger, Text, Numeric
from app.core.database import Base


class Movil(Base):
    __tablename__ = "moviles"

    idMovil = Column(Integer, primary_key=True, autoincrement=True)
    Patente = Column(String(14), nullable=False, default="")
    Detalle = Column(String(200), nullable=False, default="")
    idChofer = Column(Integer, nullable=False, default=1)
    ult_hr_km = Column(Integer, nullable=False, default=0)
    UltFecha = Column(Date, nullable=True)
    idUnidadNegocio = Column(Integer, nullable=False, default=1)
    tipo_proceso = Column(String(1), nullable=False, default="1")
    Baja = Column(SmallInteger, nullable=False, default=0)
    activo = Column(SmallInteger, nullable=False, default=1)
    FechaBaja = Column(Date, nullable=True)
    fecha_alta = Column(Date, nullable=True)
    capacidad_tanque = Column(Integer, nullable=False, default=0)
    tipo_movil = Column(Integer, nullable=False, default=1)
    observaciones = Column(Text, nullable=True)
