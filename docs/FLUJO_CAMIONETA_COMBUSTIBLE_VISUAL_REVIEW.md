# Visual Review — Flujo camioneta: combustible y KM por parte de producción

- **Fecha:** 2026-10-14 (validación), documentado 2026-10-15
- **Rama:** `codex/tarea-flujo-camioneta-e2e` (base `main` @ `c02ecdd`)
- **Objetivo:** validar punta a punta que una camioneta puede cargar combustible
  y sus KM **usando el parte de producción existente**, sin cambios de código.

## Entorno de la prueba

El host demo documentado (`fasa_195` / `fg-ubuntu`) está offline desde hace
meses, y `backend/.env` apunta a una base que ya no responde. Para no tocar nada
productivo se armó un entorno local desechable:

- MariaDB 11.8 dentro de WSL Ubuntu, base nueva `registro_demo` (usuario
  `registro_demo`, acceso solo desde la LAN local).
- Esquema cargado desde `fg_structure.sql` (sin vistas/rutinas: referencian la
  base real `fg`) + `migrations.sql` + `db_migrations/*.sql`.
- Columnas que declaraban los modelos y faltaban en el dump, sincronizadas:
  `moviles.usa_planificacion`, `moviles.codigo_fg`,
  `moviles.modelo_normalizado`, `tablero_produccion.tipo_proceso_id`.
- Pivotes de las migraciones nuevas poblados a mano (`movil_unidad_negocio`)
  porque el seed demo no los cubre (ver Hallazgos).
- Datos ficticios con el seed oficial: `python -m app.seed.demo_data`
  (`APP_INSTANCE=indufor_demo`, `ALLOW_DEMO_SEED=true`).
- Backend: `uvicorn app.main:app` en `127.0.0.1:8000`.
- Frontend: `npm run dev -- --host 127.0.0.1 --port 5174`.
- Navegador: Microsoft Edge headless vía Playwright (regla de CONTEXT.md).

**Ningún dato productivo fue tocado.** Producción
(`produccion.indufor.com.ar`, base `fg`) sigue intacta; todas las escrituras
fueron sobre la base local desechable.

## Comandos ejecutados

```text
# entorno (WSL)
apt-get install mariadb-server; mysql registro_demo < fg_structure.sql (sin vistas)
mysql registro_demo < migrations.sql; mysql registro_demo < db_migrations/*.sql
# datos demo
python -m app.seed.demo_data                      # 200 partes, 50 cargas, 10 personal
# E2E visual
node e2e_camioneta.mjs                            # 15 capturas, exit 0
# verificación
python verify_all.py                              # 17/17 checks OK
# validaciones obligatorias
python -m pytest                                  # 243 passed
python -m compileall app                          # exit 0
npx vitest run                                    # 313 passed (52 archivos)
git diff --check                                  # exit 0
```

## Flujo probado

1. **Admin demo** (dni 99000001) crea el tipo de proceso **"Camioneta Demo"**
   con `campos` vacío, habilitado para la UN demo
   (Administración → Tipos de Proceso → Nuevo → pestaña Relaciones → UN).
2. **Operador Demo 01** (dni 99000011) abre Producción:
   UN precargada de la asignación → operador bloqueado a sí mismo → movil
   "Movil Demo 01" desde Asignaciones → proceso "Camioneta Demo" →
   horómetro 100/200 → producción sin campos (válido) →
   **Consumos: toggle "¿Se cargó combustible?" ON, 45 L, KM 125000, remito** →
   lugar de carga "Lugar Carga Demo 01" → revisión → **Guardar Registro**.
3. Confirmación visual "Registro guardado" (9/9 pasos validados) y el parte
   visible en **Mis Registros** ("CAMIONETA DEMO — 45 lts").

## Verificación en base (parte 900201 / carga 97790)

El parte y el egreso de stock nacieron en la **misma transacción**:

- `tablero_produccion` id **900201**: operación "Camioneta Demo",
  `tipo_proceso_id=900003`, equipo "Movil Demo 01 - DEM001",
  combustible 45 L, `form_uuid=8d79ac10-3e55-4991-af0e-9a8247a71dbd`.
- `cargacomb` id **97790**: `KM=125000`, `Litros=45`, `tipo_mov='E'`,
  `tabla='tablero_produccion'`, `idtabla='900201'` (ligada al parte),
  mismo `form_uuid`, remito canónico `000100009900`, lugar de carga 900001,
  personal = operador del parte.
- **Idempotencia (issue #124):** reintento con el mismo `form_uuid` devuelve el
  mismo parte (sin duplicar); misma clave natural con `form_uuid` nuevo →
  **HTTP 409** "Ya existe una carga de 45 L del movil 900001 con remito
  000100009900 en 2026-10-14 (id carga 97790). No se duplica el egreso de stock."

## Screenshots

`docs/screenshots/flujo_camioneta_combustible/` (ver README de la carpeta).

## Hallazgos

1. **El flujo ya existe y funciona sin código.** Con un tipo de proceso
   habilitado para la UN y la camioneta asignada al operador, el paso
   "Combustible" del parte crea el egreso de stock con KM y remito. La camioneta
   se elige como cualquier móvil.
2. **El seed demo no cubre los pivotes nuevos** (`movil_unidad_negocio`,
   `lugar_carga_unidad_negocio`): en una demo recién seedeada el operador no ve
   máquinas porque `/produccion/moviles` filtra por el pivote. Se pobló a mano
   para esta prueba. Sugiere issue de seed.
3. **`fg_structure.sql` está desactualizado** vs. los modelos (faltaban 4
   columnas) y sus vistas/rutinas referencian `fg` hardcodeado — coherente con
   lo documentado en el deploy de junio (se omitieron vistas).
4. **UX:** el campo "Remito 1" tiene `maxlength=12`; un remito hifenado de 13
   caracteres se trunca al escribirlo. El backend normaliza igual y guarda la
   forma canónica de 12 dígitos, pero conviene advertirlo en la UI o subir el
   `maxlength`.
5. **KM al cargar** queda en `cargacomb.KM`; `tablero_produccion.km_camioneta`
   sigue sin cablear en el flujo web (fuera del alcance acordado: solo se pedía
   el KM al cargar combustible).

## Veredicto

**Aprobado con observaciones.** El flujo punta a punta funciona con la
configuración documentada; las observaciones 2-5 son mejoras sugeridas, no
bloqueos.
