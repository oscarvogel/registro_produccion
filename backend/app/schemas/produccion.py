from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import date

from app.core.remito import normalize_remito


# Numeric fields that the frontend can send as an empty string or null when
# the operator clears a "number" input. We coerce those to 0 instead of
# rejecting the whole payload with a raw `int_parsing` error.
_NUMERIC_FIELDS: tuple[str, ...] = (
    "cod_operador",
    "cod_equipo",
    "hr_inicio",
    "hr_fin",
    "combustible",
    "km_combustible",
    "aceite_cadena",
    "aceite_hidraulico",
    "aceite_motor",
    "aceite_transmision",
    "aceite_embrague",
    "m3",
    "carros",
    "tn_despachadas",
    "has",
    "produccion",
    "plantas",
    "mtrs_recorridos",
    "km_carreteo",
    "km_perfilado",
    "hr_disposicion",
    "hrs_no_op",
    "espada",
    "puntera",
    "cadena",
    "pinon",
    "cantidad_cadenas",
    "pies_16",
    "pies_14",
    "pies_12",
    "pies_10",
    "pulpable",
    "lugar_carga",
    "codigo_tabla",
    "id_tipo_comb",
)


def _coerce_empty_numeric(data: Any) -> Any:
    """Treat empty strings / null in numeric fields as `0` before Pydantic
    validation runs. Without this, `v-model.number` on a cleared number input
    produces `""` and the request fails with a raw `int_parsing` error.
    """
    if not isinstance(data, dict):
        return data
    for field in _NUMERIC_FIELDS:
        if field not in data:
            continue
        value = data[field]
        if value is None or (isinstance(value, str) and value.strip() == ""):
            data[field] = 0
    return data


# --- Operador ---
class OperadorResponse(BaseModel):
    idPersonal: int
    nombre: str
    dni: str | None = None
    encargado: int = 0
    tipo_de_proceso_id: int | None = None
    unidad_ids: list[int] = Field(default_factory=list)

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
    requiere_acta: bool = False
    requiere_predio: bool = False
    requiere_rodal: bool = False

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


class UltimaHoraFinResponse(BaseModel):
    hr_fin: float | None = None


# --- Lugar de Carga ---
class LugarCargaResponse(BaseModel):
    idLugarCarga: int
    detalle: str

    class Config:
        from_attributes = True


# --- Tablero Produccion ---
class TableroProduccionCreate(BaseModel):
    form_uuid: str = Field(default="", max_length=36)
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
    km_combustible: int = Field(default=0, ge=0)
    aceite_cadena: int = 0
    aceite_hidraulico: int = 0
    aceite_motor: int = 0
    aceite_transmision: int = 0
    aceite_embrague: int = 0
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
    espada: int = 0
    puntera: int = 0
    cadena: int = 0
    pinon: int = 0
    cantidad_cadenas: int = 0
    pies_16: float = 0
    pies_14: float = 0
    pies_12: float = 0
    pies_10: float = 0
    pulpable: float = 0
    lugar_carga: int = 0
    tabla: str = "tipo_de_proceso"
    codigo_tabla: int = 0
    id_tipo_comb: int = Field(default=1, ge=1)
    remito: str = Field(default="", max_length=12)
    remito2: str = Field(default="", max_length=12)
    remito3: str = Field(default="", max_length=12)

    @field_validator("remito", "remito2", "remito3")
    @classmethod
    def validate_remito(cls, value: str) -> str:
        # Issue #124: normalizar el remito al formato canonico (12 digitos
        # para valores puramente numericos) para evitar que el mismo
        # comprobante aparezca dos veces en Control de combustible.
        if value is None or value == "":
            return ""
        try:
            return normalize_remito(value)
        except ValueError:
            raise

    @model_validator(mode="before")
    @classmethod
    def _normalize_blank_numeric_fields(cls, data: Any) -> Any:
        return _coerce_empty_numeric(data)

    @model_validator(mode="after")
    def apply_horas_maquinas_production(self):
        """Issue #146: HORAS MAQUINAS usa el horómetro como fuente de verdad.

        El operador no carga producción manual: se calcula como hr_fin - hr_inicio
        y se persiste en horas. El cálculo vive en backend para que también aplique
        a reintentos offline u otros clientes de la API.
        """
        if self.operacion.strip().upper() != "HORAS MAQUINAS":
            return self

        if self.hr_inicio <= 0 or self.hr_fin <= 0:
            raise ValueError("HORAS MAQUINAS requiere hora de inicio y hora de fin mayores a cero")
        if self.hr_fin <= self.hr_inicio:
            raise ValueError("En HORAS MAQUINAS la hora final debe ser mayor a la hora inicial")

        self.produccion = round(self.hr_fin - self.hr_inicio, 2)
        self.unidad_produccion = "HS"
        return self

    @model_validator(mode="after")
    def validate_combustible_movement(self):
        if self.combustible <= 0:
            return self

        if not self.form_uuid.strip():
            raise ValueError("El combustible requiere una identidad estable del formulario")
        if self.km_combustible <= 0:
            raise ValueError("El combustible requiere un kilometraje u horometro mayor a cero")
        if self.lugar_carga <= 0:
            raise ValueError("El combustible requiere un lugar de carga")
        if not self.remito.strip():
            raise ValueError("El combustible requiere al menos el Remito 1")
        return self


# --- Mis Registros (vista operador) ---
class MiRegistroItem(BaseModel):
    id: int
    fecha: date | None
    operacion: str
    equipo: str
    combustible: int
    tn_despachadas: float
    m3: int
    has: float
    carros: int
    plantas: int
    km_carreteo: float
    km_perfilado: float
    mtrs_recorridos: int
    hr_inicio: float
    hr_fin: float

    class Config:
        from_attributes = True


class MisRegistrosResponse(BaseModel):
    registros: list[MiRegistroItem]
    total: int
    total_horas: float
    total_combustible: int
    # totales de producción por campo
    total_tn: float
    total_m3: int
    total_has: float
    total_carros: int
    total_plantas: int
    total_km_carreteo: float
    total_km_perfilado: float
    # ratios por hora (None si total_horas == 0)
    combustible_por_hora: float | None
    tn_por_hora: float | None
    m3_por_hora: float | None
    has_por_hora: float | None
    carros_por_hora: float | None
    plantas_por_hora: float | None
    km_carreteo_por_hora: float | None
    km_perfilado_por_hora: float | None


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
    aceite_cadena: int
    aceite_hidraulico: int
    aceite_motor: int
    aceite_transmision: int
    aceite_embrague: int
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
    espada: int = 0
    puntera: int = 0
    cadena: int = 0
    pinon: int = 0
    cantidad_cadenas: int = 0
    pies_16: float = 0
    pies_14: float = 0
    pies_12: float = 0
    pies_10: float = 0
    pulpable: float = 0
    lugar_carga: int = 0

    class Config:
        from_attributes = True
