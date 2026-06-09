from sqlalchemy import Column, Integer, SmallInteger, String

from app.core.database import Base


class TipoMovil(Base):
    __tablename__ = "tipodemovil"

    id = Column(Integer, primary_key=True, autoincrement=True)
    detalle = Column(String(50), nullable=False)
    activo = Column(SmallInteger, nullable=False, default=1)
