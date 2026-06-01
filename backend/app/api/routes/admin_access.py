from fastapi import APIRouter

from app.api.routes import admin_legacy
from app.schemas.admin import ConfiguracionUsuarioResponse

router = APIRouter(prefix="/admin", tags=["admin-access"])

router.add_api_route(
    "/configuracion/usuarios",
    admin_legacy.list_usuarios_configuracion,
    methods=["GET"],
    response_model=list[ConfiguracionUsuarioResponse],
)
router.add_api_route(
    "/configuracion/usuarios/{idPersonal}/acceso",
    admin_legacy.update_usuario_acceso,
    methods=["PATCH"],
    response_model=ConfiguracionUsuarioResponse,
)
