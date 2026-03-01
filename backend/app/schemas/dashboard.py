from pydantic import BaseModel
from datetime import date


# ─── KPI individual en la respuesta ───
class KpiItem(BaseModel):
    id: int
    nombre: str
    valor: float
    unidad: str
    icono: str
    es_principal: bool = False
    variacion_porcentual: float | None = None


# ─── Respuesta del endpoint /kpis ───
class FiltrosAplicados(BaseModel):
    tipo_proceso: str | None = None
    movil: str | None = None
    fecha_desde: str | None = None
    fecha_hasta: str | None = None


class KpisResponse(BaseModel):
    kpis: list[KpiItem]
    filtros_aplicados: FiltrosAplicados


# ─── Evolución temporal ───
class DatasetItem(BaseModel):
    nombre: str
    valores: list[float]


class EvolucionResponse(BaseModel):
    labels: list[str]
    datasets: list[DatasetItem]


# ─── Ranking de máquinas ───
class RankingMaquinaItem(BaseModel):
    patente: str
    detalle: str
    valor: float
    registros: int


# ─── Tipos de proceso disponibles ───
class TipoProcesoDisponible(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True


# ─── Móviles disponibles ───
class MovilDisponible(BaseModel):
    idMovil: int
    patente: str
    detalle: str

    class Config:
        from_attributes = True
