import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.core.config import settings
from app.core.database import SessionLocal
from app.api.routes import items, auth, produccion, dashboard

import pymysql
from app.core.config import settings
from app.api.routes import items, auth
pymysql.install_as_MySQLdb()
app = FastAPI(title=settings.PROJECT_NAME)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler — ensures CORS headers are always sent even on 500
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)},
    )

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(items.router, prefix="/api")
app.include_router(produccion.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}


@app.on_event("startup")
def backfill_tabla_codigo_tabla():
    """Corrige registros web antiguos que no tienen tabla/codigo_tabla seteados."""
    db = SessionLocal()
    try:
        db.execute(text("""
            UPDATE tablero_produccion tp
            JOIN tipo_de_proceso tdp ON tdp.nombre = tp.operacion
            SET tp.tabla = 'tipo_de_proceso', tp.codigo_tabla = tdp.id
            WHERE (tp.tabla IS NULL OR tp.tabla = '')
              AND tp.operacion IS NOT NULL AND tp.operacion != ''
        """))
        db.commit()
    except Exception as e:
        print(f"[backfill] No se pudo actualizar tabla/codigo_tabla: {e}")
        db.rollback()
    finally:
        db.close()
 