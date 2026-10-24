from datetime import datetime

from sqlalchemy import Column, DateTime, Index, Integer, SmallInteger, String

from app.core.database import Base


class ProduccionEvidencia(Base):
    """Evidencia fotografica de un registro de produccion.

    Una fila es una foto. `tipo` es el rol principal de la foto
    ('procesador' u 'horometro') y `incluye_horometro` cubre el caso en que
    el operador declara que el horometro se ve en la misma pantalla del
    procesador: esa sola foto cubre los dos roles.

    La foto se sube antes de que exista la fila de produccion (modo offline),
    asi que el vinculo estable es `form_uuid`; `registro_id` se completa
    cuando se crea el registro.
    """

    __tablename__ = "produccion_evidencia"
    __table_args__ = (
        # Indice NORMAL, no unico: con D-F puede haber mas de una fila por
        # (form_uuid, tipo) -- la foto rechazada queda como historial y la
        # nueva la reemplaza. La unicidad "una sola evidencia viva por tipo"
        # la garantiza la aplicacion (ver app/api/routes/evidencia.py).
        Index("idx_evidencia_form_tipo", "form_uuid", "tipo"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Vinculo con tablero_produccion. NULL mientras la foto viaja sola.
    registro_id = Column(Integer, nullable=True, index=True)
    # Identidad estable del formulario: deduplica reintentos de subida.
    form_uuid = Column(String(36), nullable=False)
    # 'procesador' | 'horometro'
    tipo = Column(String(20), nullable=False)
    # La foto del procesador tambien muestra el horometro (decision D7).
    incluye_horometro = Column(SmallInteger, nullable=False, default=0)
    # Ruta RELATIVA dentro del volumen de archivos de evidencia.
    archivo = Column(String(255), nullable=False)
    mime = Column(String(100), nullable=False, default="")
    tamano = Column(Integer, nullable=False, default=0)
    hash_sha256 = Column(String(64), nullable=False, default="")
    # 0 pendiente, 1 verificada, 2 rechazada, 3 reemplazada.
    estado = Column(SmallInteger, nullable=False, default=0)
    # Nombre de quien la cargo (auditoria legible).
    cargado_por = Column(String(80), nullable=False, default="")
    # idPersonal de quien la cargo: el nombre no es univoco y los permisos
    # se deciden por id, no por texto.
    cargado_por_id = Column(Integer, nullable=True, index=True)
    verificado_por = Column(String(80), nullable=False, default="")
    verificado_at = Column(DateTime, nullable=True)
    comentario = Column(String(255), nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
