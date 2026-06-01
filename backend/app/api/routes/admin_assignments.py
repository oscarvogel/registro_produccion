from fastapi import APIRouter, status

from app.api.routes import admin_legacy
from app.schemas.admin import AsignacionOperativaResponse, DeleteResponse

router = APIRouter(prefix="/admin", tags=["admin-assignments"])

router.add_api_route(
    "/asignaciones",
    admin_legacy.list_asignaciones,
    methods=["GET"],
    response_model=list[AsignacionOperativaResponse],
)
router.add_api_route(
    "/asignaciones",
    admin_legacy.create_asignacion,
    methods=["POST"],
    response_model=AsignacionOperativaResponse,
    status_code=status.HTTP_201_CREATED,
)
router.add_api_route(
    "/asignaciones/{idAsignacion}",
    admin_legacy.update_asignacion,
    methods=["PUT"],
    response_model=AsignacionOperativaResponse,
)
router.add_api_route(
    "/asignaciones/{idAsignacion}",
    admin_legacy.delete_asignacion,
    methods=["DELETE"],
    response_model=DeleteResponse,
)
