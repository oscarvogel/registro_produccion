# Issue #141 Caminos Multi-Proceso Integration Plan
> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Probar y garantizar que un parte de Caminos con DISPOSICION y REMOLQUE se envíe como procesos separados, persista en dos filas relacionadas y genere un único movimiento de combustible.

**Architecture:** Mantener la ruta específica `POST /api/produccion/caminos` como orquestador de la persistencia multi-proceso. La normalización de texto se realiza en el schema antes de las validaciones de longitud y también en la construcción de payloads persistidos para no reintroducir padding proveniente de catálogos. El frontend conserva `procesos` como array y normaliza los textos al construir el payload.

**Tech Stack:** FastAPI, Pydantic v2, SQLAlchemy, SQLite en tests, Vue 3, Pinia, Vitest, Vite.

---

## Task 1: Add real backend persistence coverage

**Files:** `backend/tests/test_parte_caminos_integration.py`

- [ ] Add an isolated SQLite fixture with `UnidadNegocio`, `TipoDeProceso`, `TableroProduccion`, and `CargaComb` tables only.
- [ ] Invoke `create_parte_caminos` directly with a validated two-process payload and stub only permission/locking dependencies; do not use production data or services.
- [ ] Assert exactly two `tablero_produccion` rows, one shared `form_uuid`, shared header fields, different `tipo_proceso_id`, individual `operacion`, and process-specific metrics.
- [ ] Assert exactly one `CargaComb` for the form and that it points to the first persisted production row.
- [ ] Run the focused backend tests and confirm they fail before the implementation is completed.

## Task 2: Add frontend payload coverage

**Files:** `frontend/src/views/CaminosFormView.test.js`

- [ ] Mount the real view with padded catalog values and two selected processes.
- [ ] Fill operator, business unit, equipment, predio, acta, rodal, and observations with lateral whitespace, then invoke the real save path.
- [ ] Assert the store receives trimmed values and `procesos` remains an array with one object per process, never a concatenated operation string.
- [ ] Run the focused Vitest test and confirm it fails before the implementation is completed.

## Task 3: Normalize before validation and persistence

**Files:** `frontend/src/views/CaminosFormView.vue`, `backend/app/schemas/parte_caminos.py`, `backend/app/api/routes/parte_caminos.py`

- [ ] Normalize frontend header/catalog text with `trim()` while preserving the existing numeric conversions and process array shape.
- [ ] Normalize backend header and process text before Pydantic length/business validation.
- [ ] Normalize unit/type catalog names at the route persistence boundary so padded database catalog values cannot leak into `UN` or `operacion`.
- [ ] Keep the existing per-process row creation and single fuel movement behavior unchanged except for normalized values.

## Task 4: Verify all suites

- [ ] Run the focused backend and frontend tests until green.
- [ ] Run the complete backend test suite.
- [ ] Run the complete frontend test suite.
- [ ] Run the frontend production build and inspect the diff for unrelated changes.

## Task 5: Publish and refresh the test environment

- [ ] Commit the implementation and tests on the PR branch without merging to `main`.
- [ ] Push the branch only after checking the working tree and commit contents.
- [ ] Pull the exact new commit into `/tmp/registro_produccion_test_126/app` on `fasa_195`.
- [ ] Reuse the existing MySQL container and restart only backend/frontend test services if required.
- [ ] Report commit(s), files, suites, and concrete two-row/one-fuel evidence.
