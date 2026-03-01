from pydantic import BaseModel
from datetime import date


# --- Operador ---
class OperadorResponse(BaseModel):
    idPersonal: int
    nombre: str
    dni: str | None = None
    encargado: int = 0
    tipo_de_proceso_id: int | None = None

    class Config:
        from_attributes = True


# --- Unidad de Negocio ---
class UnidadNegocioResponse(BaseModel):
    idUnidadNegocio: int
    nombre: str

    class Config:
        from_attributes = True


# --- Tipo de Proceso ---
class TipoProcesoResponse(BaseModel):
    id: int
    nombre: str
    campos: str

    class Config:
        from_attributes = True


# --- Movil ---
class MovilResponse(BaseModel):
    idMovil: int
    patente: str
    detalle: str
    idChofer: int

    class Config:
        from_attributes = True


# --- Asignación Operativa ---
class AsignacionOperativaResponse(BaseModel):
    idAsignacion: int
    idMovil: int
    idChofer: int
    idProceso: int
    patente: str = ""
    detalle: str = ""

    class Config:
        from_attributes = True


# --- Acta ---
class ActaResponse(BaseModel):
    id: int
    numero: str
    rodal_id: int

    class Config:
        from_attributes = True


# --- Predio ---
class PredioResponse(BaseModel):
    idPredio: int
    nombre: str

    class Config:
        from_attributes = True


# --- Rodal ---
class RodalResponse(BaseModel):
    idRodal: int
    rodal: str
    idPredio: int

    class Config:
        from_attributes = True


# --- Tablero Produccion ---
class TableroProduccionCreate(BaseModel):
    UN: str = ""
    operacion: str = ""
    fecha: date
    equipo: str = ""
    operador: str = ""
    cod_operador: int = 1
    cod_equipo: int = 1
    cod_un: int | None = None
    hr_inicio: float = 0
    hr_fin: float = 0
    combustible: int = 0
    aceite_cadena: int = 0
    acta: str = "0"
    rodal: str = "0"
    predio: str = "0"
    m3: int = 0
    carros: int = 0
    tn_despachadas: float = 0
    has: float = 0
    produccion: float = 0
    plantas: int = 0
    mtrs_recorridos: int = 0
    km_carreteo: float = 0
    km_perfilado: float = 0
    hr_disposicion: float = 0
    hrs_no_op: int = 0
    motivo_no_op: str = "0"
    observaciones: str = "0"
    unidad_produccion: str = "0"
    tabla: str = "tipo_de_proceso"
    codigo_tabla: int = 0


class TableroProduccionResponse(BaseModel):
    id: int
    UN: str
    operacion: str
    fecha: date | None
    equipo: str
    operador: str
    cod_operador: int
    cod_equipo: int
    hr_inicio: float
    hr_fin: float
    combustible: int
    m3: int
    carros: int
    tn_despachadas: float
    has: float
    produccion: float
    plantas: int
    mtrs_recorridos: int
    km_carreteo: float
    km_perfilado: float
    hr_disposicion: float
    hrs_no_op: int
    observaciones: str
    acta: str
    rodal: str
    predio: str

    class Config:
        from_attributes = True
