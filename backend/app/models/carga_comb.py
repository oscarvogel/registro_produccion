from sqlalchemy import Column, Integer, String, Date, Numeric, SmallInteger, UniqueConstraint
from app.core.database import Base


class CargaComb(Base):
    __tablename__ = "cargacomb"
    __table_args__ = (
        UniqueConstraint(
            "personal",
            "form_uuid",
            name="uq_cargacomb_personal_form_uuid",
        ),
    )

    idCargaComb = Column(Integer, primary_key=True, autoincrement=True)
    idMovil = Column(Integer, nullable=False, default=0)
    idTipoComb = Column(Integer, nullable=False)
    Fecha = Column(Date, nullable=True)
    KM = Column(Integer, nullable=False, default=0)
    PreXLitro = Column(Numeric(12, 4), nullable=False, default=0)
    Litros = Column(Numeric(12, 4), nullable=False, default=0)
    idLugarCarga = Column(Integer, nullable=False, default=1)
    UnidadNegocio = Column(Integer, nullable=False, default=1)
    idPaniol = Column(Integer, nullable=False, default=1)
    personal = Column(Integer, nullable=False, default=1)
    idtabla = Column(String(12), nullable=False, default="0")
    remito = Column(String(12), nullable=False, default="0")
    tipo_mov = Column(String(1), nullable=False, default="")
    comprobante = Column(String(12), nullable=False, default="")
    modificado = Column(SmallInteger, nullable=False, default=0)
    pase = Column(SmallInteger, nullable=False, default=0)
    tabla = Column(String(50), nullable=False, default="0")
    _usuario = Column(String(30), nullable=False, default="")
    _fecha = Column(Date, nullable=True)
    _hora = Column(String(8), nullable=False, default="")
    remito2 = Column(String(12), nullable=True)
    remito3 = Column(String(12), nullable=True)
    observaciones = Column(String(200), nullable=True, default="")
    ajuste_stock = Column(SmallInteger, nullable=True, default=0)
    form_uuid = Column(String(36), nullable=True)
