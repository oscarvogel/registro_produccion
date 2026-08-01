from sqlalchemy import Column, Integer, String
from app.core.database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    # MySQL exige longitud explicita en VARCHAR. La longitud 200 sigue el
    # patron de otras tablas (ej: moviles.Detalle varchar(200)) y es
    # suficiente para nombres de items de catalogo.
    name = Column(String(200), index=True)
    description = Column(String(500), nullable=True)
