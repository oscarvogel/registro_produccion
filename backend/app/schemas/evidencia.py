"""Schemas compartidos de la evidencia fotografica (issue #194).

Los flags de exigencia de evidencia viven en `tipo_de_proceso` y se exponen
en DOS schemas distintos: el de admin (`/api/admin/tipos-proceso`) y el de
produccion (`/api/produccion/tipo-proceso`, que alimenta el wizard). Ya se
han desincronizado una vez (el flag `requiere_horometro` faltaba en uno de
los dos), asi que los campos viven en un mixin comun.
"""
from pydantic import BaseModel, field_validator


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
