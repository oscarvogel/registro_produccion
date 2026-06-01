from fastapi import APIRouter

from app.api.routes import admin_legacy
from app.schemas.admin import (
    AdminDashboardOverviewResponse,
    AdminRecentRecordItem,
    DashboardUnidadNegocioItem,
)

router = APIRouter(prefix="/admin", tags=["admin-dashboard"])

router.add_api_route(
    "/dashboard/overview",
    admin_legacy.get_admin_dashboard_overview,
    methods=["GET"],
    response_model=AdminDashboardOverviewResponse,
)
router.add_api_route(
    "/dashboard",
    admin_legacy.get_admin_dashboard,
    methods=["GET"],
    response_model=list[DashboardUnidadNegocioItem],
)
router.add_api_route(
    "/dashboard/recent-records",
    admin_legacy.get_admin_recent_records,
    methods=["GET"],
    response_model=list[AdminRecentRecordItem],
)
