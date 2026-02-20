from sqlalchemy import Column, Integer, ForeignKey
from app.core.database import Base


class AsignacionOperativa(Base):
    __tablename__ = "asignaciones_operativas"

    idAsignacion = Column(Integer, primary_key=True, autoincrement=True)
    idMovil = Column(Integer, ForeignKey("moviles.idMovil"), nullable=False)
    idChofer = Column(Integer, ForeignKey("personal.idPersonal"), nullable=False)
    idProceso = Column(Integer, ForeignKey("tipo_de_proceso.id"), nullable=False)
