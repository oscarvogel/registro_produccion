from sqlalchemy import Column, Integer

from app.core.database import Base


class PersonalUnidadNegocio(Base):
    __tablename__ = "personal_unidad_negocio"

    idPersonal = Column(Integer, primary_key=True)
    idUnidadNegocio = Column(Integer, primary_key=True)
