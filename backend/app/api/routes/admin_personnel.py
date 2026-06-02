from fastapi import APIRouter, status

from app.api.routes import admin_legacy
from app.schemas.admin import DeleteResponse, PersonalResponse

router = APIRouter(prefix="/admin", tags=["admin-personnel"])

router.add_api_route("/personal", admin_legacy.list_personal, methods=["GET"], response_model=list[PersonalResponse])
router.add_api_route(
    "/personal",
    admin_legacy.create_personal,
    methods=["POST"],
    response_model=PersonalResponse,
    status_code=status.HTTP_201_CREATED,
)
router.add_api_route(
    "/personal/{idPersonal}",
    admin_legacy.update_personal,
    methods=["PUT"],
    response_model=PersonalResponse,
)
router.add_api_route(
    "/personal/{idPersonal}",
    admin_legacy.delete_personal,
    methods=["DELETE"],
    response_model=DeleteResponse,
)
