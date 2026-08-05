from datetime import date
from pydantic import BaseModel, Field, field_validator

from app.core.remito import normalize_remito


class CombustibleMovilResponse(BaseModel):
    idMovil: int
    patente: str
    detalle: str
    id_unidad_negocio: int


class CargaCombustibleCreate(BaseModel):
    form_uuid: str = Field(min_length=1, max_length=36)
    fecha: date
    id_movil: int
    litros: float = Field(gt=0)
    km: int = Field(gt=0)
    id_lugar_carga: int = Field(ge=1)
    id_tipo_comb: int = Field(default=1, ge=1)
    remito: str = Field(min_length=1, max_length=12)
    remito2: str = Field(default="", max_length=12)
    remito3: str = Field(default="", max_length=12)
    observaciones: str | None = None

    @field_validator("form_uuid")
    @classmethod
    def validate_form_uuid(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("El valor no puede estar vacío")
        return normalized

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


class CargaCombustibleResponse(BaseModel):
    id_carga: int
    fecha: date | None
    id_movil: int
    movil: str
    patente: str
    id_operador: int
    operador: str
    unidad_negocio: int
    litros: float
    km: int
    id_lugar_carga: int
    id_tipo_comb: int
    remito: str
    remito2: str
    remito3: str
    form_uuid: str
    observaciones: str | None = None
