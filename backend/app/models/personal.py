from sqlalchemy import Column, Integer, String, Date, Float, SmallInteger
from app.core.database import Base


class Personal(Base):
    __tablename__ = "personal"

    idPersonal = Column(Integer, primary_key=True, autoincrement=True)
    Nombre = Column(String(80), nullable=False, default="")
    CUIT = Column(String(13), nullable=False, default="")
    FechaAlta = Column(Date, nullable=True)
    FechaBaja = Column(Date, nullable=True)
    fecha_nacimiento = Column(Date, nullable=True)
    fecha_ingreso = Column(Date, nullable=True)
    idPuesto = Column(Integer, nullable=False, default=1)
    EntradaM = Column(String(5), nullable=False, default="00:00")
    SalidaM = Column(String(5), nullable=False, default="00:00")
    EntradaT = Column(String(5), nullable=False, default="00:00")
    SalidaT = Column(String(5), nullable=False, default="00:00")
    CodigoArauco = Column(String(10), nullable=False, default="")
    CodigoRoble = Column(Integer, nullable=False, default=0)
    ult_liq = Column(String(6), nullable=False, default="")
    unidad_negocio = Column(Integer, nullable=False, default=1)
    expediente = Column(SmallInteger, nullable=False, default=0)
    telefono = Column(String(50), nullable=False, default="")
    domicilio = Column(String(50), nullable=False, default="")
    concepto_sueldo = Column(Integer, nullable=False, default=0)
    codigo_kobo = Column(String(50), nullable=False, default="")
    porcentaje = Column(Float, nullable=False)
    activo = Column(SmallInteger, nullable=False)
    dni = Column(String(8), nullable=True)
    password = Column(String(255), nullable=True)
    user_id = Column(Integer, nullable=True, unique=True)
