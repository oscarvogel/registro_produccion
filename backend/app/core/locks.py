"""Lock nombrado de MySQL para serializar operaciones sensibles.

Dos operaciones del backend necesitan que no se pisen entre si:

- el alta de un parte (`tablero_produccion` asigna los ids con `MAX(id)+1`),
- la carga de evidencia (una foto viva por `(form_uuid, tipo)`).

MySQL tiene locks con nombre (`GET_LOCK`), que viven en la **conexion** y no
en la transaccion: por eso el lock usa una conexion dedicada, que se mantiene
abierta hasta que se libero.
"""
from __future__ import annotations

from contextlib import contextmanager

from fastapi import HTTPException
from sqlalchemy import text


def adquirir_lock(db, lock_name: str) -> bool:
    """Toma el lock nombrado. True si se logro."""
    result = db.execute(
        text("SELECT GET_LOCK(:lock_name, 10)"),
        {"lock_name": lock_name},
    ).scalar()
    return result == 1


def liberar_lock(db, lock_name: str) -> None:
    """Libera el lock nombrado."""
    db.execute(
        text("SELECT RELEASE_LOCK(:lock_name)"),
        {"lock_name": lock_name},
    )


@contextmanager
def form_submission_lock(db, lock_name: str):
    """Reserva el lock durante el bloque, con una conexion dedicada."""
    # Named locks belong to a MySQL connection, not a transaction. Keep this
    # dedicated connection checked out until RELEASE_LOCK has completed.
    connection = db.get_bind().connect()
    try:
        if not adquirir_lock(connection, lock_name):
            raise HTTPException(
                status_code=503,
                detail="No se pudo reservar el envio. Se reintentara automaticamente.",
            )
        yield
    finally:
        try:
            liberar_lock(connection, lock_name)
        finally:
            connection.close()
