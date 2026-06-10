from fastapi import APIRouter, status

from app.api.routes import admin_legacy
from app.schemas.admin import (
    DeleteResponse,
    LugarCargaResponse,
    MovilResponse,
    PredioResponse,
    RodalResponse,
    TipoProcesoResponse,
    TipoMovilResponse,
    UnidadNegocioResponse,
)

router = APIRouter(prefix="/admin", tags=["admin-catalogs"])

router.add_api_route("/moviles", admin_legacy.list_moviles, methods=["GET"], response_model=list[MovilResponse])
router.add_api_route("/moviles", admin_legacy.create_movil, methods=["POST"], response_model=MovilResponse, status_code=status.HTTP_201_CREATED)
router.add_api_route("/moviles/{idMovil}", admin_legacy.update_movil, methods=["PUT"], response_model=MovilResponse)
router.add_api_route("/moviles/{idMovil}", admin_legacy.delete_movil, methods=["DELETE"], response_model=DeleteResponse)

router.add_api_route("/unidades-negocio", admin_legacy.list_unidades_negocio, methods=["GET"], response_model=list[UnidadNegocioResponse])
router.add_api_route("/unidades-negocio", admin_legacy.create_unidad_negocio, methods=["POST"], response_model=UnidadNegocioResponse, status_code=status.HTTP_201_CREATED)
router.add_api_route("/unidades-negocio/{idUnidadNegocio}", admin_legacy.update_unidad_negocio, methods=["PUT"], response_model=UnidadNegocioResponse)
router.add_api_route("/unidades-negocio/{idUnidadNegocio}", admin_legacy.delete_unidad_negocio, methods=["DELETE"], response_model=DeleteResponse)

router.add_api_route("/tipos-proceso", admin_legacy.list_tipos_proceso, methods=["GET"], response_model=list[TipoProcesoResponse])
router.add_api_route("/tipos-proceso", admin_legacy.create_tipo_proceso, methods=["POST"], response_model=TipoProcesoResponse, status_code=status.HTTP_201_CREATED)
router.add_api_route("/tipos-proceso/{tipo_proceso_id}", admin_legacy.update_tipo_proceso, methods=["PUT"], response_model=TipoProcesoResponse)
router.add_api_route("/tipos-proceso/{tipo_proceso_id}", admin_legacy.delete_tipo_proceso, methods=["DELETE"], response_model=DeleteResponse)

router.add_api_route("/tipos-movil", admin_legacy.list_tipos_movil, methods=["GET"], response_model=list[TipoMovilResponse])

router.add_api_route("/lugares-carga", admin_legacy.list_lugares_carga, methods=["GET"], response_model=list[LugarCargaResponse])
router.add_api_route("/lugares-carga", admin_legacy.create_lugar_carga, methods=["POST"], response_model=LugarCargaResponse, status_code=status.HTTP_201_CREATED)
router.add_api_route("/lugares-carga/{idLugarCarga}", admin_legacy.update_lugar_carga, methods=["PUT"], response_model=LugarCargaResponse)
router.add_api_route("/lugares-carga/{idLugarCarga}", admin_legacy.delete_lugar_carga, methods=["DELETE"], response_model=DeleteResponse)

router.add_api_route("/predios", admin_legacy.list_predios, methods=["GET"], response_model=list[PredioResponse])
router.add_api_route("/predios", admin_legacy.create_predio, methods=["POST"], response_model=PredioResponse, status_code=status.HTTP_201_CREATED)
router.add_api_route("/predios/{idPredio}", admin_legacy.update_predio, methods=["PUT"], response_model=PredioResponse)
router.add_api_route("/predios/{idPredio}", admin_legacy.delete_predio, methods=["DELETE"], response_model=DeleteResponse)

router.add_api_route("/rodales", admin_legacy.list_rodales, methods=["GET"], response_model=list[RodalResponse])
router.add_api_route("/rodales", admin_legacy.create_rodal, methods=["POST"], response_model=RodalResponse, status_code=status.HTTP_201_CREATED)
router.add_api_route("/rodales/{idRodal}", admin_legacy.update_rodal, methods=["PUT"], response_model=RodalResponse)
router.add_api_route("/rodales/{idRodal}", admin_legacy.delete_rodal, methods=["DELETE"], response_model=DeleteResponse)
