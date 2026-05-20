from datetime import date
from pydantic import BaseModel, Field


class DashboardTipoProcesoItem(BaseModel):
    id: int
    nombre: str
    registros: int
    produccion: float


class DashboardResumenItem(BaseModel):
    total_registros: int
    produccion_total: float
    tn_despachadas_total: float
    combustible_total: int
    operadores_activos: int
    equipos_activos: int
    registros_hoy: int


class DashboardUnidadNegocioItem(BaseModel):
    id: int
    nombre: str
    prefijo: str
    resumen: DashboardResumenItem
    tipos_proceso: list[DashboardTipoProcesoItem]


class AdminRecentRecordItem(BaseModel):
    id: int
    fecha: date | None
    unidad: str
    operacion: str
    operador: str
    equipo: str
    produccion: float
    combustible: int


class PersonalCreate(BaseModel):
    nombre: str = Field(min_length=1)
    dni: str | None = None
    cuit: str = ""
    id_puesto: int = 1
    unidad_negocio: int = 1
    unidad_ids: list[int] = Field(default_factory=list)
    tipo_de_proceso_id: int | None = None
    entrada_m: str = "00:00"
    salida_m: str = "00:00"
    entrada_t: str = "00:00"
    salida_t: str = "00:00"
    fecha_nacimiento: date | None = None
    fecha_ingreso: date | None = None
    telefono: str = ""
    domicilio: str = ""
    activo: int = 1
    encargado: int = 0
    is_admin: int = 0
    password: str | None = None


class PersonalUpdate(BaseModel):
    nombre: str | None = None
    dni: str | None = None
    cuit: str | None = None
    id_puesto: int | None = None
    unidad_negocio: int | None = None
    unidad_ids: list[int] | None = None
    tipo_de_proceso_id: int | None = None
    entrada_m: str | None = None
    salida_m: str | None = None
    entrada_t: str | None = None
    salida_t: str | None = None
    fecha_nacimiento: date | None = None
    fecha_ingreso: date | None = None
    telefono: str | None = None
    domicilio: str | None = None
    activo: int | None = None
    encargado: int | None = None
    is_admin: int | None = None
    password: str | None = None


class PersonalResponse(BaseModel):
    idPersonal: int
    nombre: str
    dni: str | None = None
    cuit: str
    id_puesto: int
    unidad_negocio: int
    unidad_ids: list[int] = Field(default_factory=list)
    tipo_de_proceso_id: int | None = None
    entrada_m: str
    salida_m: str
    entrada_t: str
    salida_t: str
    fecha_nacimiento: date | None = None
    fecha_ingreso: date | None = None
    telefono: str
    domicilio: str
    activo: int
    encargado: int
    is_admin: int


class MovilCreate(BaseModel):
    patente: str = Field(min_length=1)
    detalle: str = Field(min_length=1)
    tipo_proceso: str = "1"
    id_unidad_negocio: int = 1
    cant_neumaticos: int = 0
    capacidad_tanque: int = 0
    consumo_promedio: float = 0
    tipo_movil: int = 1
    anio_fabricacion: int = 0
    nro_chasis: str = ""
    nro_motor: str = ""
    venc_tecnica: date | None = None
    ruta: bool = False
    venc_ruta: date | None = None
    activo: int = 1
    observaciones: str | None = None


class MovilUpdate(BaseModel):
    patente: str | None = None
    detalle: str | None = None
    tipo_proceso: str | None = None
    id_unidad_negocio: int | None = None
    cant_neumaticos: int | None = None
    capacidad_tanque: int | None = None
    consumo_promedio: float | None = None
    tipo_movil: int | None = None
    anio_fabricacion: int | None = None
    nro_chasis: str | None = None
    nro_motor: str | None = None
    venc_tecnica: date | None = None
    ruta: bool | None = None
    venc_ruta: date | None = None
    activo: int | None = None
    observaciones: str | None = None


class MovilResponse(BaseModel):
    idMovil: int
    patente: str
    detalle: str
    tipo_proceso: str
    id_unidad_negocio: int
    cant_neumaticos: int
    capacidad_tanque: int
    consumo_promedio: float
    tipo_movil: int
    anio_fabricacion: int
    nro_chasis: str
    nro_motor: str
    venc_tecnica: date | None = None
    ruta: bool
    venc_ruta: date | None = None
    activo: int
    observaciones: str | None = None


class UnidadNegocioCreate(BaseModel):
    nombre: str = Field(min_length=1)
    prefijo: str = ""
    codigo_kobo: str = ""
    activo: int = 1


class UnidadNegocioUpdate(BaseModel):
    nombre: str | None = None
    prefijo: str | None = None
    codigo_kobo: str | None = None
    activo: int | None = None


class UnidadNegocioResponse(BaseModel):
    idUnidadNegocio: int
    nombre: str
    prefijo: str
    codigo_kobo: str
    activo: int


class TipoProcesoCreate(BaseModel):
    nombre: str = Field(min_length=1)
    campos: str = ""
    unidad_ids: list[int] = Field(default_factory=list)
    activo: int = 1


class TipoProcesoUpdate(BaseModel):
    nombre: str | None = None
    campos: str | None = None
    unidad_ids: list[int] | None = None
    activo: int | None = None


class TipoProcesoResponse(BaseModel):
    id: int
    nombre: str
    campos: str
    unidad_ids: list[int] = Field(default_factory=list)
    activo: int


class LugarCargaCreate(BaseModel):
    detalle: str = Field(min_length=1)
    unidad_negocio: int = 1
    activo: int = 1


class LugarCargaUpdate(BaseModel):
    detalle: str | None = None
    unidad_negocio: int | None = None
    activo: int | None = None


class LugarCargaResponse(BaseModel):
    idLugarCarga: int
    detalle: str
    unidad_negocio: int
    activo: int


class PredioCreate(BaseModel):
    idPredio: int | None = None
    nombre: str = Field(min_length=1)
    empresa: str = Field(min_length=1)
    codigo_kobo: str | None = None


class PredioUpdate(BaseModel):
    nombre: str | None = None
    empresa: str | None = None
    codigo_kobo: str | None = None


class PredioResponse(BaseModel):
    idPredio: int
    nombre: str
    empresa: str
    codigo_kobo: str | None = None


class RodalCreate(BaseModel):
    rodal: str = Field(min_length=1)
    idPredio: int
    vam: float = 0
    tarifa: float = 0
    extraccion: float = 0
    carga: float = 0


class RodalUpdate(BaseModel):
    rodal: str | None = None
    idPredio: int | None = None
    vam: float | None = None
    tarifa: float | None = None
    extraccion: float | None = None
    carga: float | None = None


class RodalResponse(BaseModel):
    idRodal: int
    rodal: str
    idPredio: int
    vam: float
    tarifa: float
    extraccion: float
    carga: float


class AsignacionOperativaCreate(BaseModel):
    idMovil: int
    idChofer: int
    idProceso: int


class AsignacionOperativaUpdate(BaseModel):
    idMovil: int | None = None
    idChofer: int | None = None
    idProceso: int | None = None


class AsignacionOperativaResponse(BaseModel):
    idAsignacion: int
    idMovil: int
    idChofer: int
    idProceso: int


class ConfiguracionUsuarioResponse(BaseModel):
    idPersonal: int
    nombre: str
    dni: str | None = None
    activo: int
    encargado: int
    is_admin: int


class ConfiguracionAccesoUpdate(BaseModel):
    is_admin: int


class DeleteResponse(BaseModel):
    ok: bool = True
