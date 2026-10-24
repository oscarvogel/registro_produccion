from sqlalchemy import Boolean, Column, Integer, String, SmallInteger
from app.core.database import Base


class TipoDeProceso(Base):
    __tablename__ = "tipo_de_proceso"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    campos = Column(String(255), nullable=False, default="")
    requiere_acta = Column(Boolean, nullable=False, default=False)
    requiere_predio = Column(Boolean, nullable=False, default=False)
    requiere_rodal = Column(Boolean, nullable=False, default=False)
    requiere_horometro = Column(Boolean, nullable=False, default=True)
    # Exigencia de evidencia fotografica (issue #194).
    #
    # NULL = sin configurar; la API lo expone como False (no exige evidencia).
    # 0 = configurado, no exige evidencia. 1 = configurado, exige evidencia.
    #
    # OJO: `requiere_horometro` es otro concepto: define si el parte pide
    # horometro inicial/final. Este flag define si hace falta FOTOGRAFIARLO.
    requiere_foto_horometro = Column(Boolean, nullable=True)
    requiere_foto_procesador = Column(Boolean, nullable=True)
    activo = Column(SmallInteger, nullable=False, default=1)


class UnidadNegocioTipoProceso(Base):
    __tablename__ = "unidadnegocio_tipo_proceso"

    un_id = Column(Integer, primary_key=True)
    tipo_proceso_id = Column(Integer, primary_key=True)
