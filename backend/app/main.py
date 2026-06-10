import re
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
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
 
