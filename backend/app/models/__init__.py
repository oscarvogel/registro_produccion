"""Modelos del backend.

Importar todos los modelos aca es necesario para que `Base.metadata` los
registre y `Base.metadata.create_all(engine)` levante las tablas en una
DB limpia. Sin estos imports, ``create_all`` no crea ninguna tabla
porque SQLAlchemy solo conoce los modelos que se importaron en el proceso.
"""
from app.core.database import Base  # noqa: F401  (reexportado para conveniencia)

# Tablas principales. El orden no importa: SQLAlchemy resuelve las FK en
# el momento del create_all.
from app.models.asignacion_operativa import AsignacionOperativa  # noqa: F401
from app.models.carga_comb import CargaComb  # noqa: F401
from app.models.dashboard import KpiDefinicion, TipoProcesoKpi  # noqa: F401
from app.models.item import Item  # noqa: F401
from app.models.lugar_carga import LugarCarga  # noqa: F401
from app.models.lugar_carga_unidad_negocio import LugarCargaUnidadNegocio  # noqa: F401
from app.models.movil import Movil  # noqa: F401
from app.models.movil_operador import MovilOperador  # noqa: F401
from app.models.movil_unidad_negocio import MovilUnidadNegocio  # noqa: F401
from app.models.personal import Personal  # noqa: F401
from app.models.personal_unidad_negocio import PersonalUnidadNegocio  # noqa: F401
from app.models.produccion import TableroProduccion  # noqa: F401
from app.models.tipo_movil import TipoMovil  # noqa: F401
from app.models.tipo_proceso import TipoDeProceso, UnidadNegocioTipoProceso  # noqa: F401
from app.models.ubicacion import Acta, Predio, Rodal  # noqa: F401
from app.models.unidad_negocio import UnidadNegocio  # noqa: F401
