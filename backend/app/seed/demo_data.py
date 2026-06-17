from __future__ import annotations

import argparse
import os
import random
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Iterable
from sqlalchemy import text

from app.core.config import settings

DEMO_MARKER = "DEMO_SEED"
DEMO_ID_BASE = 900000
SAFE_INSTANCE_TOKENS = ("demo", "test", "staging")


class DemoSeedSafetyError(RuntimeError):
    """Raised when the demo seed safety checks fail."""


@dataclass(frozen=True)
class DemoDataset:
    unidades_negocio: list[dict]
    tipos_proceso: list[dict]
    tipos_movil: list[dict]
    personal: list[dict]
    moviles: list[dict]
    lugares_carga: list[dict]
    predios: list[dict]
    rodales: list[dict]
    asignaciones: list[dict]
    moviles_operadores: list[dict]
    produccion: list[dict]
    cargas_combustible: list[dict]


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _is_true(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y", "si"}


def _instance_is_safe(instance: str) -> bool:
    normalized = instance.lower()
    return any(token in normalized for token in SAFE_INSTANCE_TOKENS)


def validate_seed_environment(*, force_instance: bool = False) -> None:
    app_env = _env("APP_ENV", "development").lower()
    app_instance = _env("APP_INSTANCE", "")
    allow_seed = _env("ALLOW_DEMO_SEED", "false")

    if app_env == "production":
        raise DemoSeedSafetyError("Refusing to run demo seed with APP_ENV=production")
    if not _is_true(allow_seed):
        raise DemoSeedSafetyError("Refusing to run demo seed unless ALLOW_DEMO_SEED=true")
    if not force_instance and not _instance_is_safe(app_instance):
        raise DemoSeedSafetyError(
            "Refusing to run demo seed unless APP_INSTANCE contains demo, test, or staging"
        )


def _demo_dni(offset: int) -> str:
    return f"9900{offset:04d}"[-8:]


def build_demo_dataset(*, record_count: int, today: date | None = None) -> DemoDataset:
    today = today or date.today()
    rng = random.Random(20260617)

    unidades_negocio = [
        {
            "idUnidadNegocio": DEMO_ID_BASE + 1,
            "Nombre": "Unidad Negocio Demo Forestal",
            "Prefijo": "DEM",
            "codigo_kobo": "demo_un_forestal",
            "activo": 1,
        }
    ]
    tipos_proceso = [
        {"id": DEMO_ID_BASE + 1, "nombre": "Proceso Demo Cosecha", "campos": "", "activo": 1},
        {"id": DEMO_ID_BASE + 2, "nombre": "Proceso Demo Transporte", "campos": "", "activo": 1},
    ]
    tipos_movil = [
        {"id": DEMO_ID_BASE + 1, "detalle": "Tipo Movil Demo Harvester", "activo": 1},
        {"id": DEMO_ID_BASE + 2, "detalle": "Tipo Movil Demo Forwarder", "activo": 1},
        {"id": DEMO_ID_BASE + 3, "detalle": "Tipo Movil Demo Camion", "activo": 1},
    ]

    personal = [
        _personal_row(DEMO_ID_BASE + 1, "Admin Demo", _demo_dni(1), 1, 1, tipos_proceso[0]["id"]),
        _personal_row(DEMO_ID_BASE + 2, "Encargado Demo", _demo_dni(2), 1, 0, tipos_proceso[0]["id"]),
    ]
    personal.extend(
        _personal_row(
            DEMO_ID_BASE + 10 + index,
            f"Operador Demo {index:02d}",
            _demo_dni(10 + index),
            0,
            0,
            tipos_proceso[index % len(tipos_proceso)]["id"],
        )
        for index in range(1, 9)
    )

    moviles = [
        _movil_row(DEMO_ID_BASE + index, f"Movil Demo {index:02d}", tipos_movil[index % len(tipos_movil)]["id"])
        for index in range(1, 7)
    ]
    lugares_carga = [
        {
            "idLugarCarga": DEMO_ID_BASE + index,
            "Detalle": f"Lugar Carga Demo {index:02d}",
            "activo": 1,
            "unidad_negocio": unidades_negocio[0]["idUnidadNegocio"],
        }
        for index in range(1, 5)
    ]
    predios = [
        {
            "idPredio": DEMO_ID_BASE + 1,
            "Nombre": "Predio Demo Norte",
            "empresa": "Empresa Demo",
            "codigo_kobo": "predio_demo_norte",
        },
        {
            "idPredio": DEMO_ID_BASE + 2,
            "Nombre": "Predio Demo Sur",
            "empresa": "Empresa Demo",
            "codigo_kobo": "predio_demo_sur",
        },
    ]
    rodales = [
        {
            "idRodal": DEMO_ID_BASE + index,
            "Rodal": f"Rodal Demo {'AB'[index % 2]}-{index:02d}",
            "idPredio": predios[index % len(predios)]["idPredio"],
            "VAM": Decimal("10.0000"),
            "Tarifa": Decimal("1.0000"),
            "Extraccion": Decimal("1.0000"),
            "Carga": Decimal("1.0000"),
        }
        for index in range(1, 9)
    ]

    operadores = [row for row in personal if row["Nombre"].startswith("Operador Demo")]
    asignaciones = [
        {
            "idMovil": movil["idMovil"],
            "idChofer": operadores[index % len(operadores)]["idPersonal"],
            "idProceso": tipos_proceso[index % len(tipos_proceso)]["id"],
        }
        for index, movil in enumerate(moviles)
    ]
    moviles_operadores = [
        {
            "operador_id": asignacion["idChofer"],
            "movil_id": str(asignacion["idMovil"]),
            "desde": today - timedelta(days=60),
            "hasta": None,
        }
        for asignacion in asignaciones
    ]

    produccion = []
    cargas_combustible = []
    for index in range(record_count):
        operador = operadores[index % len(operadores)]
        movil = moviles[index % len(moviles)]
        lugar = lugares_carga[index % len(lugares_carga)]
        rodal = rodales[index % len(rodales)]
        predio = predios[index % len(predios)]
        fecha = today - timedelta(days=rng.randint(0, 59))
        produccion.append(
            {
                "id": DEMO_ID_BASE + index + 1,
                "UN": unidades_negocio[0]["Nombre"],
                "operacion": tipos_proceso[index % len(tipos_proceso)]["nombre"],
                "fecha": fecha,
                "equipo": movil["Detalle"],
                "operador": operador["Nombre"],
                "hr_inicio": Decimal(index % 6),
                "hr_fin": Decimal((index % 6) + 4),
                "combustible": 20 + (index % 40),
                "acta": f"DEMO-{index + 1:04d}"[:10],
                "rodal": rodal["Rodal"][:10],
                "m3": 10 + (index % 25),
                "produccion": Decimal(10 + (index % 25)),
                "unidad_produccion": "m3",
                "observaciones": f"{DEMO_MARKER} registro ficticio",
                "predio": predio["Nombre"],
                "cod_operador": operador["idPersonal"],
                "cod_equipo": movil["idMovil"],
                "_uuid": f"demo-{index + 1:032d}"[:36],
                "form_uuid": f"demo-form-{index + 1:027d}"[:36],
                "lugar_carga": lugar["idLugarCarga"],
                "usuario": "seed_demo",
                "fecha_hora": datetime.combine(fecha, time(hour=8 + (index % 8))),
                "cod_un": unidades_negocio[0]["idUnidadNegocio"],
                "tabla": DEMO_MARKER,
                "codigo_tabla": index + 1,
            }
        )
        if index < max(1, record_count // 4):
            cargas_combustible.append(
                {
                    "idMovil": movil["idMovil"],
                    "idTipoComb": 1,
                    "Fecha": fecha,
                    "KM": 1000 + index * 8,
                    "PreXLitro": Decimal("1.0000"),
                    "Litros": Decimal(20 + (index % 15)),
                    "idLugarCarga": lugar["idLugarCarga"],
                    "UnidadNegocio": unidades_negocio[0]["idUnidadNegocio"],
                    "personal": operador["idPersonal"],
                    "idtabla": f"D{index + 1:06d}"[:12],
                    "remito": f"D{index + 1:06d}"[:12],
                    "tabla": DEMO_MARKER,
                    "_usuario": "seed_demo",
                    "_fecha": fecha,
                    "_hora": "08:00",
                    "observaciones": f"{DEMO_MARKER} combustible ficticio",
                }
            )

    return DemoDataset(
        unidades_negocio=unidades_negocio,
        tipos_proceso=tipos_proceso,
        tipos_movil=tipos_movil,
        personal=personal,
        moviles=moviles,
        lugares_carga=lugares_carga,
        predios=predios,
        rodales=rodales,
        asignaciones=asignaciones,
        moviles_operadores=moviles_operadores,
        produccion=produccion,
        cargas_combustible=cargas_combustible,
    )


def _personal_row(id_personal: int, nombre: str, dni: str, encargado: int, is_admin: int, tipo_proceso_id: int) -> dict:
    return {
        "idPersonal": id_personal,
        "Nombre": nombre,
        "CUIT": "",
        "FechaAlta": date.today(),
        "idPuesto": 1,
        "EntradaM": "07:00",
        "SalidaM": "12:00",
        "EntradaT": "13:00",
        "SalidaT": "17:00",
        "CodigoArauco": "",
        "CodigoRoble": 0,
        "ult_liq": "",
        "unidad_negocio": DEMO_ID_BASE + 1,
        "expediente": 0,
        "telefono": "",
        "domicilio": "Domicilio Demo",
        "concepto_sueldo": 0,
        "codigo_kobo": f"demo_{dni}",
        "porcentaje": 100,
        "activo": 1,
        "encargado": encargado,
        "is_admin": is_admin,
        "tipo_de_proceso_id": tipo_proceso_id,
        "dni": dni,
        "password": "demo1234",
    }


def _movil_row(id_movil: int, detalle: str, tipo_movil: int) -> dict:
    return {
        "idMovil": id_movil,
        "Patente": f"DEM{id_movil - DEMO_ID_BASE:03d}",
        "Detalle": detalle,
        "idChofer": DEMO_ID_BASE + 11,
        "ult_hr_km": 0,
        "idUnidadNegocio": DEMO_ID_BASE + 1,
        "tipo_proceso": "1",
        "CantNeumaticos": 4,
        "CantRepuesto": 1,
        "Baja": 0,
        "activo": 1,
        "MotivoBaja": "",
        "Remolque": "",
        "Porcentaje": Decimal("0.00"),
        "Ruta": False,
        "nvocodigo": f"demo-{id_movil}",
        "nro_chasis": f"chasis-demo-{id_movil}",
        "nro_motor": f"motor-demo-{id_movil}",
        "anio_fabricacion": 2020,
        "centro_costo": 0,
        "codigo_kobo": f"movil_demo_{id_movil}",
        "codigo_bertotto": 0,
        "capacidad_tanque": 100,
        "consumo_promedio": 10,
        "forma_actualizacion": "",
        "tipo_movil": tipo_movil,
        "estadistica": 1,
        "codigo_gestya": "",
        "movil_asociado": 0,
        "observaciones": f"{DEMO_MARKER} movil ficticio",
    }


def _delete_existing_demo_data(db) -> dict[str, int]:
    from app.models.asignacion_operativa import AsignacionOperativa
    from app.models.carga_comb import CargaComb
    from app.models.lugar_carga import LugarCarga
    from app.models.movil import Movil
    from app.models.movil_operador import MovilOperador
    from app.models.personal import Personal
    from app.models.produccion import TableroProduccion
    from app.models.tipo_movil import TipoMovil
    from app.models.tipo_proceso import TipoDeProceso
    from app.models.ubicacion import Predio, Rodal
    from app.models.unidad_negocio import UnidadNegocio

    demo_personal_ids = [row[0] for row in db.query(Personal.idPersonal).filter(Personal.Nombre.like("%Demo%")).all()]
    demo_movil_ids = [row[0] for row in db.query(Movil.idMovil).filter(Movil.Detalle.like("%Demo%")).all()]

    deleted = {}
    deleted["asignaciones"] = db.query(AsignacionOperativa).filter(
        AsignacionOperativa.idMovil.in_(demo_movil_ids) | AsignacionOperativa.idChofer.in_(demo_personal_ids)
    ).delete(synchronize_session=False)
    deleted["moviles_operadores"] = db.query(MovilOperador).filter(
        MovilOperador.operador_id.in_(demo_personal_ids) | MovilOperador.movil_id.in_([str(id_) for id_ in demo_movil_ids])
    ).delete(synchronize_session=False)
    deleted["cargas_combustible"] = db.query(CargaComb).filter(CargaComb.observaciones.like(f"%{DEMO_MARKER}%")).delete(
        synchronize_session=False
    )
    deleted["produccion"] = db.query(TableroProduccion).filter(
        (TableroProduccion.observaciones.like(f"%{DEMO_MARKER}%")) | (TableroProduccion.operador.like("%Demo%"))
    ).delete(synchronize_session=False)
    deleted["rodales"] = db.query(Rodal).filter(Rodal.Rodal.like("%Demo%")).delete(synchronize_session=False)
    deleted["predios"] = db.query(Predio).filter(Predio.Nombre.like("%Demo%")).delete(synchronize_session=False)
    deleted["lugares_carga"] = db.query(LugarCarga).filter(LugarCarga.Detalle.like("%Demo%")).delete(
        synchronize_session=False
    )
    deleted["moviles"] = db.query(Movil).filter(Movil.Detalle.like("%Demo%")).delete(synchronize_session=False)
    deleted["personal"] = db.query(Personal).filter(Personal.Nombre.like("%Demo%")).delete(synchronize_session=False)
    deleted["tipos_movil"] = db.query(TipoMovil).filter(TipoMovil.detalle.like("%Demo%")).delete(
        synchronize_session=False
    )
    deleted["tipos_proceso"] = db.query(TipoDeProceso).filter(TipoDeProceso.nombre.like("%Demo%")).delete(
        synchronize_session=False
    )
    deleted["unidades_negocio"] = db.query(UnidadNegocio).filter(UnidadNegocio.Nombre.like("%Demo%")).delete(
        synchronize_session=False
    )
    return deleted


def _bulk_insert(db, model, rows: Iterable[dict]) -> int:
    rows = list(rows)
    if rows:
        db.bulk_insert_mappings(model, rows)
    return len(rows)


def run_seed(*, record_count: int, clear_only: bool = False) -> dict[str, int]:
    from app.core.database import SessionLocal
    from app.models.asignacion_operativa import AsignacionOperativa
    from app.models.carga_comb import CargaComb
    from app.models.lugar_carga import LugarCarga
    from app.models.movil import Movil
    from app.models.movil_operador import MovilOperador
    from app.models.personal import Personal
    from app.models.produccion import TableroProduccion
    from app.models.tipo_movil import TipoMovil
    from app.models.tipo_proceso import TipoDeProceso
    from app.models.ubicacion import Predio, Rodal
    from app.models.unidad_negocio import UnidadNegocio

    dataset = build_demo_dataset(record_count=record_count)
    db = SessionLocal()
    try:
        foreign_key_checks_disabled = _set_mysql_foreign_key_checks(db, enabled=False)
        deleted = _delete_existing_demo_data(db)
        created: dict[str, int] = {}
        if not clear_only:
            created["unidades_negocio"] = _bulk_insert(db, UnidadNegocio, dataset.unidades_negocio)
            created["tipos_proceso"] = _bulk_insert(db, TipoDeProceso, dataset.tipos_proceso)
            created["tipos_movil"] = _bulk_insert(db, TipoMovil, dataset.tipos_movil)
            created["personal"] = _bulk_insert(db, Personal, dataset.personal)
            created["moviles"] = _bulk_insert(db, Movil, dataset.moviles)
            created["lugares_carga"] = _bulk_insert(db, LugarCarga, dataset.lugares_carga)
            created["predios"] = _bulk_insert(db, Predio, dataset.predios)
            created["rodales"] = _bulk_insert(db, Rodal, dataset.rodales)
            created["asignaciones"] = _bulk_insert(db, AsignacionOperativa, dataset.asignaciones)
            created["moviles_operadores"] = _bulk_insert(db, MovilOperador, dataset.moviles_operadores)
            created["produccion"] = _bulk_insert(db, TableroProduccion, dataset.produccion)
            created["cargas_combustible"] = _bulk_insert(db, CargaComb, dataset.cargas_combustible)
        if foreign_key_checks_disabled:
            _set_mysql_foreign_key_checks(db, enabled=True)
        db.commit()
        return {f"deleted_{key}": value for key, value in deleted.items()} | {
            f"created_{key}": value for key, value in created.items()
        }
    except Exception:
        if "foreign_key_checks_disabled" in locals() and foreign_key_checks_disabled:
            try:
                _set_mysql_foreign_key_checks(db, enabled=True)
            except Exception:
                pass
        db.rollback()
        raise
    finally:
        db.close()


def _set_mysql_foreign_key_checks(db, *, enabled: bool) -> bool:
    if "mysql" not in settings.DATABASE_URL.lower():
        return False
    db.execute(text(f"SET FOREIGN_KEY_CHECKS={1 if enabled else 0}"))
    return True


def _record_count_from_env() -> int:
    raw = _env("DEMO_SEED_RECORDS", "200")
    try:
        return max(1, int(raw))
    except ValueError as exc:
        raise DemoSeedSafetyError("DEMO_SEED_RECORDS must be an integer") from exc


def _print_summary(summary: dict[str, int], *, dry_run: bool) -> None:
    mode = "dry-run" if dry_run else "applied"
    print(f"Demo seed {mode} for instance '{_env('APP_INSTANCE', 'unknown')}'")
    for key in sorted(summary):
        print(f"- {key}: {summary[key]}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed fake demo data for a non-production registro_produccion instance.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print planned counts without touching the DB.")
    parser.add_argument("--clear-only", action="store_true", help="Delete only demo-tagged data before exiting.")
    parser.add_argument("--force-instance", action="store_true", help="Allow APP_INSTANCE without demo/test/staging token.")
    args = parser.parse_args(argv)

    validate_seed_environment(force_instance=args.force_instance)
    record_count = _record_count_from_env()
    if args.dry_run:
        dataset = build_demo_dataset(record_count=record_count)
        summary = {
            "planned_unidades_negocio": len(dataset.unidades_negocio),
            "planned_tipos_proceso": len(dataset.tipos_proceso),
            "planned_tipos_movil": len(dataset.tipos_movil),
            "planned_personal": len(dataset.personal),
            "planned_moviles": len(dataset.moviles),
            "planned_lugares_carga": len(dataset.lugares_carga),
            "planned_predios": len(dataset.predios),
            "planned_rodales": len(dataset.rodales),
            "planned_asignaciones": len(dataset.asignaciones),
            "planned_produccion": len(dataset.produccion),
            "planned_cargas_combustible": len(dataset.cargas_combustible),
        }
        _print_summary(summary, dry_run=True)
        return 0

    summary = run_seed(record_count=record_count, clear_only=args.clear_only)
    _print_summary(summary, dry_run=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
