"""Read models de combustible para la app operativa.

El libro de stock ``cargacomb`` es la fuente de verdad del combustible: contiene
las cargas creadas desde un parte, las cargas independientes y las cargas
manuales o importadas. Estos helpers solo leen y devuelven DTOs; no modifican
datos ni deciden reglas de negocio transaccionales.
"""

from datetime import date

from sqlalchemy.orm import Session

from app.models.carga_comb import CargaComb
from app.models.movil import Movil

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


def _resumen_equipo(
    db: Session,
    id_movil: int,
    fecha_desde: date | None,
    fecha_hasta: date | None,
) -> dict:
    """Libro de combustible y horómetro real de un equipo en el período.

    El horómetro se calcula igual que "Control de combustible" de Forestal:
    se parte de la última carga anterior al período y se suma ``KM`` de cada
    movimiento (sin sumar el salto de los ``pase``). Así el consumo por hora
    usa el avance real del equipo y no la suma de horas de los partes, que se
    duplica cuando hay más de un operador.
    """
    query = db.query(CargaComb).filter(CargaComb.idMovil == id_movil)
    if fecha_desde is not None:
        query = query.filter(CargaComb.Fecha >= fecha_desde)
    if fecha_hasta is not None:
        query = query.filter(CargaComb.Fecha <= fecha_hasta)
    cargas = query.order_by(
        CargaComb.Fecha,
        CargaComb.KM,
        CargaComb.idCargaComb,
    ).all()

    total_egresos = sum(
        float(carga.Litros or 0) for carga in cargas if carga.tipo_mov == "E"
    )
    total_ingresos = sum(
        float(carga.Litros or 0) for carga in cargas if carga.tipo_mov == "I"
    )

    km_inicio = None
    if fecha_desde is not None:
        anterior = (
            db.query(CargaComb)
            .filter(
                CargaComb.idMovil == id_movil,
                CargaComb.Fecha < fecha_desde,
            )
            .order_by(
                CargaComb.Fecha.desc(),
                CargaComb.KM.desc(),
                CargaComb.idCargaComb.desc(),
            )
            .first()
        )
        if anterior is not None:
            km_inicio = float(anterior.KM or 0)

    km_fin = None
    km_anterior = km_inicio
    km_recorrido = 0.0
    for carga in cargas:
        km = float(carga.KM or 0)
        if km_anterior is None:
            km_anterior = km
        if carga.pase:
            km_recorrido = 0.0
        else:
            km_recorrido += km - km_anterior
        km_anterior = km
        km_fin = km

    if km_inicio is None and cargas:
        km_inicio = float(cargas[0].KM or 0)

    total_horas = km_recorrido if km_recorrido > 0 else 0.0
    return {
        "id_movil": int(id_movil),
        "nombre": "",
        "total_egresos": round(total_egresos, 2),
        "total_ingresos": round(total_ingresos, 2),
        "km_inicio": km_inicio,
        "km_fin": km_fin,
        "total_horas": round(total_horas, 2),
        "consumo_por_hora": (
            round(total_egresos / total_horas, 2) if total_horas > 0 else None
        ),
    }


def resumen_combustible_equipos(
    db: Session,
    equipo_ids,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
) -> dict:
    """Totales del libro de combustible por equipo, con consumo individual.

    Cada equipo se calcula por separado: sumar equipos distintos mezcla
    consumos de máquinas que no tienen nada que ver. El total agregado se
    mantiene para compatibilidad, pero la UI usa ``por_equipo``.
    """
    ids = sorted({int(i) for i in equipo_ids if int(i or 0) > 0})
    if not ids:
        return {
            "equipos": [],
            "por_equipo": [],
            "total_egresos": 0.0,
            "total_ingresos": 0.0,
            "total_horas": 0.0,
            "consumo_por_hora": None,
        }

    nombres = {
        int(row.idMovil): row.Detalle or ""
        for row in db.query(Movil.idMovil, Movil.Detalle)
        .filter(Movil.idMovil.in_(ids))
        .all()
    }

    por_equipo = []
    for id_movil in ids:
        item = _resumen_equipo(db, id_movil, fecha_desde, fecha_hasta)
        item["nombre"] = nombres.get(id_movil, "")
        por_equipo.append(item)

    total_egresos = round(sum(item["total_egresos"] for item in por_equipo), 2)
    total_ingresos = round(sum(item["total_ingresos"] for item in por_equipo), 2)
    total_horas = round(sum(item["total_horas"] for item in por_equipo), 2)
    return {
        "equipos": ids,
        "por_equipo": por_equipo,
        "total_egresos": total_egresos,
        "total_ingresos": total_ingresos,
        "total_horas": total_horas,
        "consumo_por_hora": (
            round(total_egresos / total_horas, 2) if total_horas > 0 else None
        ),
    }
