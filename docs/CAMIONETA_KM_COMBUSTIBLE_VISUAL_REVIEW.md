# Visual Review — Flujo camioneta: combustible y KM sin horómetro

- **Fecha:** 2026-10-16
- **Rama:** `codex/tarea-flujo-camioneta-e2e`
- **Objetivo:** que una camioneta registre **combustible y KM** desde el parte de
  producción **sin cargar horómetro**. Antes el paso "Control de Tiempo" era
  obligatorio para cualquier tipo de proceso.

## Cambio funcional

Se agregó el flag `requiere_horometro` al tipo de proceso:

- **Backend:** columna `tipo_de_proceso.requiere_horometro` (TINYINT(1) DEFAULT 1),
  migración `db_migrations/20261016_tipo_proceso_requiere_horometro.sql` (se aplica
  con `python -m app.migrate` en el deploy; ver `DEPLOY.md`), schema
  `TipoProcesoCreate/Update/Response` y ruteo en `admin_legacy`.
  Los procesos existentes conservan el horómetro (default 1).
- **Frontend:**
  - `services/tipoProcesoRules.js`: `processRequiresHorometro` y
    `productionSteps` (omite el paso "Tiempo" cuando el proceso no usa horómetro).
  - `views/ProduccionLegacyFormView.vue`: wizard dinámico por clave de paso; sin
    horómetro envía `hr_inicio/hr_fin/hrs_no_op = 0` y no consulta la última
    lectura; la revisión no muestra la fila "Horómetros".
  - `views/admin/AdminCrudView.vue`: columna "Horómetro" y checkbox
    "Requiere Horómetro" en la pestaña Requisitos.

El backend ya aceptaba horómetro en 0 para procesos distintos de "HORAS MAQUINAS",
así que no hizo falta cambiar la validación del parte.

## Entorno de la captura

Capturas con la API **mockeada** y Vite, siguiendo el patrón de
`frontend/scripts/docsCapture.mjs`. No se usó base de datos ni datos productivos:

```text
node scripts/camionetaCapture.mjs   # 13 capturas, exit 0
```

- Navegador: Chromium headless (Playwright), viewport 1440x900.
- Tipo de proceso mockeado: `CAMIONETA DEMO`, `campos` vacío,
  `requiere_horometro: false`, habilitado para la UN demo.

## Flujo probado

1. **Admin** ve Tipos de Proceso con la columna Horómetro y crea/edita un tipo
   desmarcando "Requiere Horómetro".
2. **Operador** abre Producción: el wizard muestra **8 pasos** (sin "Tiempo"):
   Contexto → Operador → Equipo → Proceso → Producción → Consumos → Ubicación →
   Revisión.
3. En **Consumos** activa "¿Se cargó combustible?", ingresa 45 L, KM 125000 y
   remito; guarda y confirma "Registro guardado".
4. El parte aparece en **Mis Registros** como "CAMIONETA DEMO — 45 lts".

## Validaciones ejecutadas

```text
python -m pytest backend/tests                                  # 247 passed
python -m compileall backend/app                                # exit 0
npx vitest run                                                  # 320 passed (53 archivos)
npm run build                                                   # exit 0
git diff --check                                                # exit 0
```

## Screenshots

`docs/screenshots/camioneta_km_combustible/` (ver README de la carpeta).

## Hallazgos

1. El paso "Tiempo" desaparece del wizard (8 pasos) y la revisión no muestra
   horómetros para procesos `requiere_horometro = false`.
2. La configuración es por tipo de proceso, sin depender del nombre: cualquier
   proceso (no solo "camioneta") puede marcarse sin horómetro.
3. Las capturas son de un ambiente mockeado; falta la verificación en base real
   (parte + `cargacomb`). Queda como pendiente para el entorno descartable.

## Veredicto

**Aprobado con observaciones.** El flujo sin horómetro funciona de punta a punta
en la UI y la configuración es explícita por tipo de proceso; la verificación en
base real queda pendiente.
