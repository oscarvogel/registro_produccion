from datetime import date
from pydantic import BaseModel, Field, field_validator


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

    @field_validator("form_uuid", "remito")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("El valor no puede estar vacío")
        return normalized


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
