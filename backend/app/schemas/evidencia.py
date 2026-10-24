"""Schemas compartidos de la evidencia fotografica (issue #194).

Los flags de exigencia de evidencia viven en `tipo_de_proceso` y se exponen
en DOS schemas distintos: el de admin (`/api/admin/tipos-proceso`) y el de
produccion (`/api/produccion/tipo-proceso`, que alimenta el wizard). Ya se
han desincronizado una vez (el flag `requiere_horometro` faltaba en uno de
los dos), asi que los campos viven en un mixin comun.
"""
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class RequisitosEvidenciaMixin(BaseModel):
    """Flags de exigencia de evidencia fotografica por tipo de proceso.

    En la base el valor NULL significa "sin configurar". La API lo expone
    siempre como bool: NULL se traduce a False (no exige evidencia), que es
    el comportamiento seguro para un proceso recien creado.
    """

    requiere_foto_horometro: bool = False
    requiere_foto_procesador: bool = False

    @field_validator("requiere_foto_horometro", "requiere_foto_procesador", mode="before")
    @classmethod
    def _sin_configurar_a_false(cls, value):
        # Con from_attributes el valor viene crudo del atributo del ORM y
        # puede ser None; sin este validator Pydantic rechazaria el None.
        if value is None:
            return False
        return value


class EvidenciaResponse(BaseModel):
    """Una foto de evidencia, tal como la ve el frontend.

    `url` es la ruta para bajar los bytes: la foto vive en el volumen del
    servidor, no en la base (decision D2).
    """

    id: int
    registro_id: int | None = None
    form_uuid: str = ""
    tipo: str = ""
    incluye_horometro: bool = False
    # 0 pendiente, 1 verificada, 2 rechazada, 3 reemplazada.
    estado: int = 0
    mime: str = ""
    tamano: int = 0
    hash_sha256: str = ""
    cargado_por: str = ""
    verificado_por: str = ""
    verificado_at: datetime | None = None
    comentario: str = ""
    created_at: datetime | None = None
    url: str = ""


class EvidenciaVerificacion(BaseModel):
    """Cuerpo del PATCH de verificacion (R5).

    El estado tiene que ser 1 (verificada) o 2 (rechazada): volver a
    "pendiente" desde el backend dejaria el registro sin cobertura y nadie
    avisado.
    """

    estado: int
    comentario: str = Field(default="", max_length=255)
