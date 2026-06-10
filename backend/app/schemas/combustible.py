from datetime import date
from pydantic import BaseModel, Field


class CombustibleMovilResponse(BaseModel):
    idMovil: int
    patente: str
    detalle: str
    id_unidad_negocio: int


class CargaCombustibleCreate(BaseModel):
    fecha: date
    id_movil: int
    litros: float = Field(gt=0)
    km: int = Field(ge=0)
    observaciones: str | None = None


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
    observaciones: str | None = None
