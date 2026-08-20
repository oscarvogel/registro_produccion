import logging
import re
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.core.config import settings
from app.core.database import engine
from app.api.routes import items, auth, produccion, parte_caminos, dashboard, admin, combustible, motivos_no_operativos

import pymysql

pymysql.install_as_MySQLdb()
app = FastAPI(title=settings.PROJECT_NAME)
logger = logging.getLogger(__name__)
SAFE_DATABASE_ERROR_DETAIL = "No se pudieron cargar los datos necesarios. Actualiza e intenta nuevamente."
SAFE_SERVER_ERROR_DETAIL = "No se pudo completar la operacion. Intenta nuevamente en unos minutos."
SAFE_VALIDATION_ERROR_DETAIL = "Los datos enviados no son validos. Revisa los campos del formulario e intenta nuevamente."

_VALUE_ERROR_PREFIX = "Value error, "
_VALIDATION_FIELD_LABELS = {
    "form_uuid": "identificador del formulario",
    "equipo": "equipo",
    "operador": "operador",
    "UN": "unidad de negocio",
    "motivo_no_op": "motivo no operativo",
    "observaciones": "observaciones",
    "predio": "predio",
    "acta": "acta",
    "rodal": "rodal",
    "remito": "remito 1",
    "remito2": "remito 2",
    "remito3": "remito 3",
}


def _validation_field_label(err: dict) -> str | None:
    location = err.get("loc") or ()
    for part in reversed(location):
        if isinstance(part, str) and part not in {"body", "query", "path"}:
            return _VALIDATION_FIELD_LABELS.get(part)
    return None


def _humanize_validation_error(exc: RequestValidationError) -> str:
    errors = exc.errors() or []
    for err in errors:
        if err.get("type") == "value_error":
            msg = str(err.get("msg") or "").strip()
            if msg.startswith(_VALUE_ERROR_PREFIX):
                msg = msg[len(_VALUE_ERROR_PREFIX):]
            if msg:
                return msg

    type_messages = {
        "int_parsing": "uno de los campos numericos no es un numero valido",
        "float_parsing": "uno de los campos numericos no es un numero valido",
        "missing": "faltan datos obligatorios del formulario",
        "string_too_long": "uno de los textos excede el tamano maximo permitido",
        "string_type": "uno de los campos esperaba texto",
        "greater_than_equal": "uno de los campos numericos es menor al minimo permitido",
        "greater_than": "uno de los campos numericos debe ser mayor a cero",
        "json_invalid": "el cuerpo de la solicitud no tiene un formato valido",
    }
    for err in errors:
        error_type = err.get("type", "")
        if error_type == "string_too_long":
            field_label = _validation_field_label(err)
            if field_label:
                return f"El campo {field_label} excede el tamano maximo permitido"
        translated = type_messages.get(error_type)
        if translated:
            return translated
    return SAFE_VALIDATION_ERROR_DETAIL


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_origin_regex=settings.ALLOWED_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    return JSONResponse(status_code=503, content={"detail": SAFE_DATABASE_ERROR_DETAIL}, headers=_cors_headers_for_request(request))


@app.exception_handler(RequestValidationError)
async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning("Validation error while processing %s %s: %s", request.method, request.url.path, exc.errors())
    return JSONResponse(status_code=422, content={"detail": _humanize_validation_error(exc)}, headers=_cors_headers_for_request(request))


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled application error while processing %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": SAFE_SERVER_ERROR_DETAIL}, headers=_cors_headers_for_request(request))


app.include_router(auth.router, prefix="/api")
app.include_router(items.router, prefix="/api")
app.include_router(produccion.router, prefix="/api")
app.include_router(parte_caminos.router, prefix="/api")
app.include_router(combustible.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(motivos_no_operativos.router, prefix="/api")


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
            database_name_check = {"expected": expected_db_name, "actual": actual_db_name, "matches": actual_db_name == expected_db_name}
        except Exception:
            database_name_check = {"expected": expected_db_name, "actual": None, "matches": False}

    healthy = bool(database_ok) and (database_name_check is None or bool(database_name_check["matches"]))
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
