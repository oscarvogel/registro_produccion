from sqlalchemy import Column, Integer, String, Numeric
from app.core.database import Base


class Acta(Base):
    __tablename__ = "actas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rodal_id = Column(Integer, nullable=False, default=0)
    numero = Column(String(30), nullable=False, default="0")
    vam = Column(Numeric(12, 4), nullable=False)
    tarifa = Column(Numeric(12, 4), nullable=False)
    extraccion = Column(Numeric(12, 4), nullable=False)
    carga = Column(Numeric(12, 4), nullable=False)
    periodo = Column(String(6), nullable=True)


class Predio(Base):
    __tablename__ = "predios"

    idPredio = Column(Integer, primary_key=True)
    Nombre = Column(String(100), nullable=False, default="")
    empresa = Column(String(30), nullable=False)
    codigo_kobo = Column(String(50), nullable=True)


class Rodal(Base):
    __tablename__ = "rodales"

    idRodal = Column(Integer, primary_key=True, autoincrement=True)
    Rodal = Column(String(50), nullable=False, default="")
    idPredio = Column(Integer, nullable=False)
    VAM = Column(Numeric(12, 4), nullable=False, default=0)
    Tarifa = Column(Numeric(12, 4), nullable=False, default=0)
    Extraccion = Column(Numeric(12, 4), nullable=False, default=0)
    Carga = Column(Numeric(12, 4), nullable=False, default=0)
