from datetime import date
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.remito import normalize_remito


class ProcesoCaminosCreate(BaseModel):
    tipo_proceso_id: int = Field(gt=0)
    predio: str = Field(default="0", max_length=50)
    acta: str = Field(default="0", max_length=10)
    rodal: str = Field(default="0", max_length=10)
    hr_disposicion: float = Field(default=0, ge=0)
    km_perfilado: float = Field(default=0, ge=0)
    hr_remolque: float = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_metricas(self):
        if self.hr_disposicion <= 0 and self.km_perfilado <= 0 and self.hr_remolque <= 0:
            raise ValueError("Cada proceso de Caminos debe tener al menos una metrica mayor a cero")
        return self


class ParteCaminosCreate(BaseModel):
    form_uuid: str = Field(min_length=1, max_length=36)
    fecha: date
    cod_equipo: int = Field(gt=0)
    equipo: str = Field(default="", max_length=100)
    cod_operador: int = Field(gt=0)
    operador: str = Field(default="", max_length=50)
    cod_un: int = Field(gt=0)
    UN: str = Field(default="Caminos", max_length=50)
    hr_inicio: float = Field(ge=0)
    hr_fin: float = Field(gt=0)

    combustible: int = Field(default=0, ge=0)
    km_combustible: int = Field(default=0, ge=0)
    lugar_carga: int = Field(default=0, ge=0)
    id_tipo_comb: int = Field(default=1, ge=1)
    remito: str = Field(default="", max_length=12)
    remito2: str = Field(default="", max_length=12)
    remito3: str = Field(default="", max_length=12)

    aceite_cadena: int = Field(default=0, ge=0)
    aceite_hidraulico: int = Field(default=0, ge=0)
    aceite_motor: int = Field(default=0, ge=0)
    aceite_transmision: int = Field(default=0, ge=0)
    aceite_embrague: int = Field(default=0, ge=0)

    hrs_no_op: int = Field(default=0, ge=0)
    motivo_no_op: str = Field(default="0", max_length=150)
    observaciones: str = Field(default="0", max_length=150)
    procesos: list[ProcesoCaminosCreate] = Field(min_length=1)

    @field_validator("remito", "remito2", "remito3")
    @classmethod
    def validate_remito(cls, value: str) -> str:
        if value is None or value == "":
            return ""
        return normalize_remito(value)

    @model_validator(mode="before")
    @classmethod
    def normalize_blanks(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        numeric_fields = (
            "cod_equipo",
            "cod_operador",
            "cod_un",
            "hr_inicio",
            "hr_fin",
            "combustible",
            "km_combustible",
            "lugar_carga",
            "id_tipo_comb",
            "aceite_cadena",
            "aceite_hidraulico",
            "aceite_motor",
            "aceite_transmision",
            "aceite_embrague",
            "hrs_no_op",
        )
        for field in numeric_fields:
            if field in data and (data[field] is None or str(data[field]).strip() == ""):
                data[field] = 0
        return data

    @model_validator(mode="after")
    def validate_cabecera(self):
        if self.hr_fin <= self.hr_inicio:
            raise ValueError("La hora final debe ser mayor que la hora inicial")
        if self.hrs_no_op > 0 and (not self.motivo_no_op.strip() or self.motivo_no_op.strip() == "0"):
            raise ValueError("Las horas no operativas requieren un motivo")
        if self.combustible > 0:
            if self.km_combustible <= 0:
                raise ValueError("El combustible requiere un kilometraje u horometro mayor a cero")
            if self.lugar_carga <= 0:
                raise ValueError("El combustible requiere un lugar de carga")
            if not self.remito.strip():
                raise ValueError("El combustible requiere al menos el Remito 1")
        return self


class ParteCaminosResponse(BaseModel):
    form_uuid: str
    registros_creados: int
    ids: list[int]
    total_km_perfilado: float
    total_hr_disposicion: float
    total_hr_remolque: float
