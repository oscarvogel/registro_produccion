from sqlalchemy import Column, Integer, SmallInteger, String

from app.core.database import Base


class Cliente(Base):
    """Cliente del catalogo legacy (tabla `cliente`).

    `predios.empresa` es clave foranea contra `cliente.cuit`, asi que el
    valor que se carga como empresa de un predio tiene que existir aca.
    Esta app no tiene ABM de clientes: el alta se hace en el sistema legacy.
    """

    __tablename__ = "cliente"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cuit = Column(String(30), nullable=False, unique=True)
    razon_social = Column(String(50), nullable=False, default="")
    domicilio = Column(String(50), nullable=False, default="")
    operaciones = Column(SmallInteger, nullable=False, default=0)
    localidad = Column(String(50), nullable=False, default="")
    telefono = Column(String(50), nullable=False, default="")
    codigo_postal = Column(String(10), nullable=False, default="")
    email = Column(String(150), nullable=False, default="")
    cat_iva = Column(String(10), nullable=False, default="")
    provincia = Column(Integer, nullable=False, default=0)
