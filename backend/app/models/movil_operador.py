from sqlalchemy import Column, Integer, String, Date
from app.core.database import Base


class MovilOperador(Base):
    __tablename__ = "moviles_operadores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    operador_id = Column(Integer, nullable=False, default=0)
    movil_id = Column(String(50), nullable=False, default="0")
    desde = Column(Date, nullable=False)
    hasta = Column(Date, nullable=True)
