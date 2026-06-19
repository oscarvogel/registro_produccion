import re
import traceback
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.core.config import settings
from app.core.database import engine
from app.api.routes import items, auth, produccion, dashboard, admin, combustible

import pymysql

pymysql.install_as_MySQLdb()
app = FastAPI(title=settings.PROJECT_NAME)

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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    origin = request.headers.get("origin", "")
    headers = {}
    if _is_allowed_origin(origin):
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
        headers=headers,
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
 
