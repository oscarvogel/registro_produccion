"""Read models de combustible para la app operativa.

El libro de stock ``cargacomb`` es la fuente de verdad del combustible: contiene
las cargas creadas desde un parte, las cargas independientes y las cargas
manuales o importadas. Estos helpers solo leen y devuelven DTOs; no modifican
datos ni deciden reglas de negocio transaccionales.
"""

from datetime import date

from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.models.carga_comb import CargaComb
from app.models.produccion import TableroProduccion

FUENTES_PARTE = ("tablero_produccion", "PRODUCCION", "produccion")


def _parte_id(valor):
    texto = str(valor or "").strip()
    if not texto or texto == "0":
        return None
    try:
        return int(texto)
    except (TypeError, ValueError):
        return None


def litros_por_parte(db: Session, parte_ids) -> dict[int, float]:
    """Litros del movimiento de stock vinculado a cada parte.

    El alta web guarda ``idtabla = str(parte.id)`` y el importador de Forestal
    guarda ``idtabla`` con ``zfill(12)``. Se consultan ambas formas. Si hubiera
    más de un movimiento para el mismo parte (dato inconsistente), se suman:
    el detalle y el total del equipo usan el mismo libro.
    """
    ids = {int(i) for i in parte_ids if int(i or 0) > 0}
    if not ids:
        return {}

    candidatos = set()
    for parte_id in ids:
        candidatos.add(str(parte_id))
        candidatos.add(str(parte_id).zfill(12))

    rows = (
        db.query(CargaComb)
        .filter(
            CargaComb.tipo_mov == "E",
            CargaComb.tabla.in_(FUENTES_PARTE),
            CargaComb.idtabla.in_(candidatos),
        )
        .all()
    )

    litros: dict[int, float] = {}
    for row in rows:
        parte_id = _parte_id(getattr(row, "idtabla", None))
        if parte_id is None:
            continue
        litros[parte_id] = litros.get(parte_id, 0.0) + float(
            getattr(row, "Litros", 0) or 0
        )
    return litros


def resumen_combustible_equipos(
    db: Session,
    equipo_ids,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
) -> dict:
    """Totales del libro de combustible y horas para un conjunto de equipos.

    - ``total_egresos``/``total_ingresos``: suma de ``cargacomb`` del período,
      sin importar el origen (parte, carga independiente o manual). Es el mismo
      alcance que "Control de combustible" de Forestal.
    - ``total_horas``: horas de todos los partes de esos equipos en el período,
      para que el consumo por hora del equipo no se calcule contra las horas de
      un solo operador.
    """
    ids = sorted({int(i) for i in equipo_ids if int(i or 0) > 0})
    if not ids:
        return {
            "equipos": [],
            "total_egresos": 0.0,
            "total_ingresos": 0.0,
            "total_horas": 0.0,
            "consumo_por_hora": None,
        }

    cargas = db.query(
        func.coalesce(
            func.sum(case((CargaComb.tipo_mov == "E", CargaComb.Litros), else_=0)),
            0,
        ),
        func.coalesce(
            func.sum(case((CargaComb.tipo_mov == "I", CargaComb.Litros), else_=0)),
            0,
        ),
    ).filter(CargaComb.idMovil.in_(ids))
    if fecha_desde is not None:
        cargas = cargas.filter(CargaComb.Fecha >= fecha_desde)
    if fecha_hasta is not None:
        cargas = cargas.filter(CargaComb.Fecha <= fecha_hasta)
    egresos, ingresos = cargas.one()

    horas_query = db.query(
        func.coalesce(
            func.sum(
                case(
                    (
                        TableroProduccion.hr_fin > TableroProduccion.hr_inicio,
                        TableroProduccion.hr_fin - TableroProduccion.hr_inicio,
                    ),
                    else_=0,
                )
            ),
            0,
        )
    ).filter(TableroProduccion.cod_equipo.in_(ids))
    if fecha_desde is not None:
        horas_query = horas_query.filter(TableroProduccion.fecha >= fecha_desde)
    if fecha_hasta is not None:
        horas_query = horas_query.filter(TableroProduccion.fecha <= fecha_hasta)
    horas = horas_query.scalar() or 0

    total_egresos = float(egresos or 0)
    total_horas = float(horas or 0)
    return {
        "equipos": ids,
        "total_egresos": total_egresos,
        "total_ingresos": float(ingresos or 0),
        "total_horas": total_horas,
        "consumo_por_hora": round(total_egresos / total_horas, 2) if total_horas > 0 else None,
    }
