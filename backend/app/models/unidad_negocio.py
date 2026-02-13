from sqlalchemy import Column, Integer, String, SmallInteger
from app.core.database import Base


class UnidadNegocio(Base):
    __tablename__ = "unidadnegocio"

    idUnidadNegocio = Column(Integer, primary_key=True, autoincrement=True)
    Nombre = Column(String(50), nullable=False, default="")
    Prefijo = Column(String(3), nullable=False, default="")
    codigo_kobo = Column(String(30), nullable=False, default="")
    activo = Column(SmallInteger, nullable=False, default=1)
