from datetime import date

from pydantic import BaseModel, Field


class CaminosRegistroAgrupado(BaseModel):
    id: int
    child_ids: list[int] = Field(default_factory=list)
    form_uuid: str = ""
    procesos_count: int = 1
    fecha: date | None = None
    operacion: str = ""
    equipo: str = ""
    combustible: int = 0
    tn_despachadas: float = 0
    m3: int = 0
    has: float = 0
    carros: int = 0
    plantas: int = 0
    km_carreteo: float = 0
    km_perfilado: float = 0
    hr_disposicion: float = 0
    hr_remolque: float = 0
    mtrs_recorridos: int = 0
    hr_inicio: float = 0
    hr_fin: float = 0


class CaminosMisRegistrosResponse(BaseModel):
    registros: list[CaminosRegistroAgrupado] = Field(default_factory=list)
    child_ids: list[int] = Field(default_factory=list)
