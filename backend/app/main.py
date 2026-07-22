import logging
import re
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.core.database import engine
from app.api.routes import items, auth, produccion, dashboard, admin, combustible

import pymysql

pymysql.install_as_MySQLdb()
app = FastAPI(title=settings.PROJECT_NAME)
logger = logging.getLogger(__name__)
DATABASE_ERROR_DETAIL = "No se pudieron cargar los datos necesarios. Actualiza e intenta nuevamente."
SERVER_ERROR_DETAIL = "No se pudo completar la operacion. Intenta nuevamente en unos minutos."
SAFE_DATABASE_ERROR_DETAIL = DATABASE_ERROR_DETAIL
SAFE_SERVER_ERROR_DETAIL = SERVER_ERROR_DETAIL

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=settings.ALLOWED_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler — ensures CORS headers are always sent even on 500
def _is_allowed_origin(origin: str) -> bool:
    return origin in settings.ALLOWED_ORIGINS or bool(re.match(settings.ALLOWED_ORIGIN_REGEX, origin))


def _cors_headers_for_request(request: Request) -> dict[str, str]:
    origin = request.headers.get("origin", "")
    headers = {}
    if _is_allowed_origin(origin):
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return headers


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.exception("Unhandled database error while processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=503,
        content={"detail": DATABASE_ERROR_DETAIL},
        headers=_cors_headers_for_request(request),
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled application error while processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": SERVER_ERROR_DETAIL},
        headers=_cors_headers_for_request(request),
    )

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(items.router, prefix="/api")
app.include_router(produccion.router, prefix="/api")
app.include_router(combustible.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


def check_database_health() -> bool:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    return True


def get_current_database_name() -> str | None:
    with engine.connect() as connection:
        return connection.execute(text("SELECT DATABASE()")).scalar()


@app.get("/health")
async def health():
    database_ok = False
    database_name_check = None
    try:
        database_ok = check_database_health()
    except Exception:
        database_ok = False

    expected_db_name = (settings.EXPECTED_DB_NAME or "").strip()
    if database_ok and expected_db_name:
        try:
            actual_db_name = get_current_database_name()
            database_name_check = {
                "expected": expected_db_name,
                "actual": actual_db_name,
                "matches": actual_db_name == expected_db_name,
            }
        except Exception:
            database_name_check = {
                "expected": expected_db_name,
                "actual": None,
                "matches": False,
            }

    healthy = bool(database_ok) and (
        database_name_check is None or bool(database_name_check["matches"])
    )
    payload = {
        "status": "ok" if healthy else "error",
        "service": settings.APP_NAME,
        "instance": settings.APP_INSTANCE,
        "database": "ok" if healthy else "error",
        "version": settings.APP_VERSION,
        "time": datetime.now(timezone.utc).isoformat(),
    }
    if database_name_check is not None:
        payload["database"] = "ok" if database_ok else "error"
        payload["database_name"] = database_name_check
    return JSONResponse(status_code=200 if healthy else 503, content=payload)
 
