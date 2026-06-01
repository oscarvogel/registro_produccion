from fastapi import APIRouter

from app.api.routes.admin_access import router as access_router
from app.api.routes.admin_assignments import router as assignments_router
from app.api.routes.admin_catalogs import router as catalogs_router
from app.api.routes.admin_dashboard import router as dashboard_router
from app.api.routes.admin_personnel import router as personnel_router

router = APIRouter()
router.include_router(dashboard_router)
router.include_router(access_router)
router.include_router(personnel_router)
router.include_router(catalogs_router)
router.include_router(assignments_router)
