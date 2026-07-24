from sqlalchemy import Column, Integer

from app.core.database import Base


class MovilUnidadNegocio(Base):
    __tablename__ = "movil_unidad_negocio"

    idMovil = Column(Integer, primary_key=True)
    idUnidadNegocio = Column(Integer, primary_key=True)
