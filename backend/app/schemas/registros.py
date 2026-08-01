"""Schemas para el listado y detalle de registros individuales.

Usados por el endpoint ``/api/dashboard/registros`` (issue #104) y reusados
desde ``/api/produccion/mis-registros`` para mantener una sola representacion
de un registro entre el dashboard y la vista del operador.
"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


# ─── Listado ────────────────────────────────────────────────────────────────


class RegistroListItem(BaseModel):
    """DTO de un registro individual para el listado paginado.

    Contiene los campos clave que se muestran en la fila/tarjeta de la lista.
    El detalle completo (RegistroDetail) se obtiene via GET /registros/{id}.
    """
    id: int
    fecha: Optional[date] = None
    operacion: str = ""
    equipo: str = ""
    operador: str = ""
    cod_operador: int = 0
    cod_equipo: int = 0
    cod_un: Optional[int] = None
    tipo_proceso_id: Optional[int] = None
    hr_inicio: float = 0
    hr_fin: float = 0
    hrs_no_op: int = 0
    motivo_no_op: str = ""
    combustible: int = 0
    aceite_cadena: int = 0
    tn_despachadas: float = 0
    m3: int = 0
    has: float = 0
    carros: int = 0
    plantas: int = 0
    km_carreteo: float = 0
    km_perfilado: float = 0
    mtrs_recorridos: int = 0
    remito: str = ""
    remito2: str = ""
    remito3: str = ""
    remito_bitren: str = ""

    class Config:
        from_attributes = True


class RegistrosPagedResponse(BaseModel):
    items: list[RegistroListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# ─── Detalle ────────────────────────────────────────────────────────────────


class RegistroDetail(RegistroListItem):
    """DTO completo de un registro individual (issue #104).

    Reune los campos que pueden llegar a ser utiles al operario/encargado que
    consulta el detalle de una carga: ubicacion, metricas, consumos, remitos,
    lubricantes, identificadores de produccion, etc. NO expone datos sensibles
    (passwords, tokens, etc.).
    """
    UN: str = ""
    acta: str = ""
    rodal: str = ""
    predio: str = ""
    parcela: str = ""
    lugar_carga: int = 0
    produccion: float = 0
    unitario: float = 0
    unidad_produccion: str = ""
    tarifa: float = 0
    fijo: float = 0
    hr_disposicion: float = 0
    km_camioneta: int = 0
    servicio_tercero: int = 0
    detalle_servicio: str = ""
    observaciones: str = ""
    aceite_hidraulico: int = 0
    aceite_motor: int = 0
    aceite_embrague: int = 0
    aceite_transmision: int = 0
    nro_parte: int = 0
    stock_abc: int = 0
    dist_tosquera: int = 0
    viaje_tosca: int = 0
    cambio_cuchilla: int = 0
    espada: int = 0
    puntera: int = 0
    cadena: int = 0
    pinon: int = 0
    cantidad_cadenas: int = 0
    giro_pinon: int = 0
    pies_16: float = 0
    pies_14: float = 0
    pies_12: float = 0
    pies_10: float = 0
    pulpable: float = 0
    remito_proveedor: str = ""
    remito_fgpy: str = ""
    nombre_chofer: str = ""
    cliente_camion: str = ""
    origen_camion: str = ""
    destino_camion: str = ""
    origen: str = ""
    origen_destino_id: int = 0
    fecha_hora: Optional[datetime] = None
    usuario: str = ""
    tabla: str = ""
    codigo_tabla: int = 0
    tarifa_empresa: float = 0
    proveedor_id: Optional[int] = None
    bruto_destino: float = 0
    tara_destino: float = 0
    neto_origen: float = 0
    neto_destino: float = 0
    hora_inicio_viaje: str = ""
    hora_fin_viaje: str = ""
    modificado: int = 0
