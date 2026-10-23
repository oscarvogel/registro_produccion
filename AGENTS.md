# AGENTS.md — Loop de trabajo para proyectos de Óscar

Este repositorio debe trabajarse con un loop operativo repetible, no con prompts aislados.

El objetivo es que cada tarea avance de forma ordenada:

**Issue → rama → implementación acotada → validaciones → PR draft → revisión → merge → cleanup → siguiente issue**

---

## 1. Principios generales

* Trabajar siempre desde `main` o la rama base oficial actualizada.
* Crear una rama por issue o tarea.
* Mantener cambios chicos, revisables y testeables.
* No mezclar issues distintos en un mismo PR.
* No implementar fuera de alcance.
* No hacer refactors grandes si no fueron pedidos.
* No modificar datos productivos reales.
* No tocar archivos locales/no trackeados fuera de alcance.
* Si hay dudas fuertes de alcance, frenar y reportar.
* Si hay conflicto real, error de validación o bloqueo de merge, frenar y reportar.
* Todo PR debe abrirse primero como draft.
* No mergear si las validaciones obligatorias no pasan.

---

## 2. Antes de empezar una tarea

1. Verificar estado local:

   ```bash
   git status -sb
   ```

2. Confirmar rama actual.

3. Actualizar rama base:

   ```bash
   git fetch --prune origin
   git pull --ff-only origin main
   ```

4. Confirmar que la rama base está alineada con `origin/main`.

5. Revisar el issue/tarea asignada.

6. Revisar dependencias:

   * Si depende de otro PR no mergeado, no avanzar.
   * Si depende de datos o decisiones faltantes, reportar.
   * Si el bloqueo es real, no inventar solución.

7. Crear rama nueva con formato:

   ```bash
   codex/issue-NN-descripcion-corta
   ```

   O, si no hay issue:

   ```bash
   codex/tarea-descripcion-corta
   ```

---

## 3. Tipos de tareas

### 3.1 Documentación

Si la tarea es documental:

* No modificar código funcional.
* No modificar UI.
* No agregar dependencias.
* Validar formato y consistencia.
* Mantener el PR chico.

Validaciones mínimas:

```bash
git diff --check
```

Si el repo tiene tests rápidos, ejecutarlos también.

---

### 3.2 Modelo / datos / servicios

Si la tarea toca modelos, servicios o reglas funcionales:

* No implementar UI salvo que el issue lo pida.
* No duplicar reglas en pantalla.
* Agregar o actualizar tests.
* Mantener reglas de negocio en servicios/modelos.
* No mezclar impresión, reportes o integraciones futuras si no corresponde.

Validaciones mínimas sugeridas para Python:

```bash
git diff --check
git diff --cached --check
python -m pytest
python -m compileall app
```

Si el repo usa `py -3.12`, preferir:

```bash
py -3.12 -m pytest
py -3.12 -m compileall app
```

---

### 3.3 UI / UX

Si la tarea agrega o modifica pantalla:

* Reutilizar servicios existentes.
* No duplicar reglas de negocio en UI.
* Mantener estilo visual aprobado del proyecto.
* Agregar tests de instanciación/navegación si existen.
* Validar visualmente con Computer Use cuando sea posible.
* Guardar screenshots reales.
* No aprobar visualmente una pantalla sin evidencia.

Validaciones mínimas:

```bash
git diff --check
git diff --cached --check
python -m pytest
python -m compileall app
```

Si existe smoke:

```bash
python -m app.main --smoke
```

Si existe modo demo/UI:

```bash
python -m app.main --demo-ui
```

La evidencia visual debe guardarse en una carpeta tipo:

```text
docs/screenshots/<nombre_tarea>/
```

Agregar un `README.md` explicando las capturas.

Si corresponde, agregar reporte:

```text
docs/<NOMBRE_TAREA>_VISUAL_REVIEW.md
```

El reporte visual debe incluir:

* Fecha.
* Rama/commit validado.
* Comandos ejecutados.
* Resultado de tests.
* Flujo probado.
* Screenshots.
* Hallazgos.
* Veredicto:

  * aprobado visualmente
  * aprobado con observaciones
  * no aprobado

---

### 3.4 Impresión / documentos / reportes

Si la tarea genera documentos, PDFs, remitos, órdenes, reportes o impresiones:

* No modificar UI salvo que sea necesario.
* No modificar reglas de negocio no relacionadas.
* Agregar tests de generación si el proyecto lo permite.
* Validar formato de salida con evidencia.
* Mantener plantillas separadas de lógica cuando sea posible.

---

### 3.5 Integraciones externas

Si la tarea toca APIs, correos, AFIP/ARCA, WhatsApp, n8n, servicios externos o bases externas:

* No usar credenciales reales en código.
* No commitear `.env`.
* Documentar variables necesarias.
* Agregar modo mock/stub si corresponde.
* Separar integración real de tests unitarios.
* No ejecutar acciones productivas sin instrucción explícita.

---

## 4. Implementación

Durante la implementación:

1. Revisar estructura del repo.
2. Buscar patrones existentes antes de crear algo nuevo.
3. Implementar lo mínimo necesario.
4. Agregar tests.
5. Ejecutar validaciones.
6. Corregir errores reales.
7. Mantener commits chicos y claros.

Evitar:

* Cambiar nombres públicos sin necesidad.
* Reordenar archivos masivamente.
* Mezclar formateos con lógica.
* Meter mejoras “ya que estamos”.
* Resolver issues futuros dentro del PR actual.

---

## 5. Validaciones obligatorias

Antes de abrir o actualizar PR, ejecutar las validaciones definidas por el proyecto.

Base sugerida:

```bash
git diff --check
git diff --cached --check
python -m pytest
python -m compileall app
```

Para apps con smoke:

```bash
python -m app.main --smoke
```

Para apps con UI:

```bash
python -m app.main --demo-ui
```

Si algún comando no existe en el proyecto, documentar cuál fue omitido y por qué.

---

## 6. PR

Todo PR debe abrirse primero como draft.

La descripción debe incluir:

* Issue relacionado con `Closes #NN` si aplica.
* Objetivo.
* Cambios realizados.
* Archivos principales modificados.
* Tests agregados o actualizados.
* Validaciones ejecutadas.
* Evidencia visual si aplica.
* Fuera de alcance.
* Riesgos o pendientes.

Formato sugerido:

```markdown
## Objetivo

Closes #NN

## Cambios

- ...

## Tests / Validaciones

- [x] git diff --check
- [x] python -m pytest
- [x] python -m compileall app
- [x] smoke, si aplica
- [x] Computer Use, si aplica

## Evidencia visual

- ...

## Fuera de alcance

- ...

## Riesgos / pendientes

- ...
```

---

## 7. Revisión final del PR

Antes de pasar a ready:

1. Actualizar rama con `main` si corresponde.
2. Revisar diff completo contra la rama base.
3. Confirmar que el alcance coincide con el issue.
4. Repetir validaciones obligatorias.
5. Si es UI, repetir validación visual con Computer Use.
6. Corregir errores reales con commits chicos.
7. Si todo está OK, pasar PR a ready.

---

## 8. Merge

Sólo mergear si:

* El PR está limpio.
* Las validaciones pasan.
* No hay conflictos.
* El issue está correctamente referenciado.
* No hay cambios fuera de alcance.
* En UI, hay evidencia visual real.

Después de mergear:

1. Verificar que el issue se cerró automáticamente.

2. Si no se cerró, cerrarlo manualmente indicando el PR.

3. Actualizar `main` local.

4. Borrar rama local/remota si corresponde.

5. Ejecutar:

   ```bash
   git status -sb
   ```

6. Reportar estado final.

---

## 9. Reporte final esperado

Al terminar cada tarea, reportar:

* Issue trabajado.
* PR creado o mergeado.
* Estado del PR.
* Merge commit si aplica.
* Estado del issue.
* Archivos modificados.
* Validaciones ejecutadas.
* Evidencia visual si aplica.
* Estado local final.
* Siguiente issue recomendado.

---

## 10. Comando corto para ejecutar el loop

Cuando el usuario diga:

```text
Ejecutá el loop para el issue #NN.
```

Se debe aplicar este flujo completo:

1. Revisar issue.
2. Validar dependencias.
3. Crear rama.
4. Implementar alcance acotado.
5. Ejecutar validaciones.
6. Abrir PR draft.
7. Revisar.
8. Si corresponde, pasar ready.
9. Si corresponde, mergear.
10. Limpiar ramas.
11. Reportar resultado final.

---

## 11. Sección específica del proyecto

### Nombre del proyecto

`registro_produccion` — Registro de producción forestal (Caminos).

App fullstack para que el operador y el encargado carguen partes de producción de
caminos, y para consultar el tablero de producción y el dashboard. Corre contra la
base MySQL `fg` y se publica en dos instancias que comparten esa base:

| Instancia        | URL                                      | Servicio en el compose       |
|------------------|------------------------------------------|------------------------------|
| `produccion_fg`  | `https://produccion.servinlgsm.com.ar/`  | `produccion_fg`              |
| `indufor`        | `https://produccion.indufor.com.ar/`     | `indufor`                    |

Las dos frontends (`frontend_servinlgsm`, `frontend_indufor`) y los dos backends
salen del mismo `docker-compose.yml`: **un deploy actualiza las dos instancias**.

### Stack

* **Backend**: Python 3.12, FastAPI 0.109, SQLAlchemy 2.x, Pydantic 2
  (`pydantic-settings`), PyMySQL, JWT con `python-jose`, hash con `passlib`/`bcrypt`,
  `gunicorn` en producción. Layout: `backend/app/{api,core,models,schemas,seed}`.
* **Frontend**: Vue 3 + Vite 5, Vue Router 4, Pinia 2, Tailwind CSS 4, GSAP 3,
  `lucide-vue-next`, `sweetalert2`, `axios`, `vite-plugin-pwa` + `dexie` (offline).
* **Base de datos**: MySQL/MariaDB, base `fg` (esquema legacy de producción:
  `unidadnegocio`, `tipo_de_proceso`, `tablero_produccion`).
* **Infraestructura**: Docker + Docker Compose, desplegado por **Coolify 4.4.7**
  (traefik v3.6 como proxy) en el host `fasa_189` (192.168.0.189,
  `fasa-PowerEdge-T40`, público 186.5.245.12).
* **Migraciones**: no hay Alembic. Son archivos SQL en `db_migrations/` que aplica
  `backend/app/migrate.py` al arrancar el contenedor (`RUN_MIGRATIONS=1` en el
  compose). El `Pre-deployment Command` de Coolify **no** sirve con build pack
  `dockercompose`.
* **CI**: GitHub Actions (`.github/workflows/ci.yml`).
* **Tests**: `pytest` (backend), `vitest` + `@vue/test-utils` (frontend),
  Playwright para la evidencia visual.

### Comandos reales del proyecto

Tests:

```bash
# Backend (desde backend/, ver pytest.ini: testpaths=tests, pythonpath=.)
cd backend
python -m pytest

# Frontend (vitest run)
cd frontend
npm test
```

Compile/check:

```bash
cd backend
python -m compileall app

cd frontend
npm run check     # == vite build
```

Smoke:

```bash
# No hay un comando `--smoke` en el repo: el smoke válido es contra la instancia.
# 1) la API responde y la base está conectada
curl -sS https://produccion.servinlgsm.com.ar/api/health
# esperado: HTTP 200, "status":"ok", "database":"ok", "database_name":{"matches":true}

# 2) la SPA carga (Playwright): login renderizado y 0 errores de consola
```

UI/demo:

```bash
# Dev server (Vite) en http://127.0.0.1:5173
cd frontend
npm run dev

# Capturas de los manuales en modo mock (390x844, datos DEMO_*)
npm run docs:capture

# Evidencia visual de una tarea: Vite + Playwright con mocks de /api/**
# (ver "Flujo visual" más abajo)
```

Build/deploy, si aplica:

```bash
# Build local de las imágenes
docker compose build

# Deploy real: Coolify, desde la PC de desarrollo (sin SSH).
# Ver DEPLOY.md para la topología, el rollback y el diagnóstico.
curl -X POST https://coolify.vogelconsultoria.com.ar/api/v1/deploy \
  -H "Authorization: Bearer $COOLIFY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"uuid":"4hcjxromkdmdylfjbw0fgvs4","force":true}'
```

### Reglas específicas del proyecto

* **Mergear a `main` NO despliega.** El CI sólo corre tests y el repo **no tiene
  webhooks**: publicar es un paso aparte y manual (panel o API de Coolify).
  Al cerrar una tarea hay que decir explícitamente si el cambio está desplegado.
* **La base real es `fg` en `186.5.245.12:23306`** (`central_admin`, CA central en
  `C:\Programacion\forestal\certs\mysql-central-ca.pem`). El certificado no valida
  para la IP: hay que conectar con `check_hostname=False` y `verify_mode=CERT_REQUIRED`.
  El `.env` del repo apunta a `192.168.0.189` y **da Access denied** desde la PC de
  desarrollo. Contra `fg` sólo `SELECT`: nunca escribir datos productivos.
* **Los catálogos se eligen con combo de búsqueda (autocomplete).** El texto escrito
  tiene que coincidir con una opción de la lista; si no coincide, no se guarda y se
  frena el envío.
* **Viewport objetivo: 1638x969 y 1366x768.** Toda vista nueva tiene que verse bien
  en los dos. Si el contenido es más alto que la ventana, va en un contenedor con
  scroll: sin eso los layouts se comprimen y los widgets se superponen.
* **Regla de negocio del turno (Caminos):** `turno = horas no operativas + horas
  trabajadas + horas a disposición`, y `horas trabajadas = horas de remolque + horas
  de perfilado`. Las horas de perfilado **se trabajan pero no se anotan como horas**
  (van en km) y **no se pueden medir en horas**. Disposición y remolque **no se suman
  entre sí**: 6 h + 6 h es un turno de 12 h, no de 18 h.
* **`backend/tests/test_deploy_scripts_contract.py` fija contenido** de `DEPLOY.md`,
  `scripts/deploy_produccion_fg_main_fasa195.sh`, `scripts/deploy_main_fasa195.sh` y
  `scripts/build_deploy_package.ps1`. Si se toca `DEPLOY.md`, hay que actualizar ese
  test en el mismo PR.
* **En Windows la suite termina con `PermissionError` al limpiar `pytest-current`**
  (pytest hace `stat` de un symlink que no puede leer). Los tests pasan igual, pero el
  exit code queda en 1 y parece un fallo. Para una corrida limpia:
  `python -m pytest --basetemp <dir>`.
* **En dev el service worker de la PWA está activo** (`frontend/vite.config.js`,
  `devOptions.enabled: true`) y el `runtimeCaching` `NetworkFirst` intercepta
  `/api/produccion/...`. Esos requests **no pasan** por `page.route` de Playwright:
  llegan al proxy de Vite y devuelven 500. Para verificar la UI con catálogos falsos
  hay que crear el contexto con `serviceWorkers: 'block'`.
* **El login tiene dos formularios** con breakpoint `lg` (1024px): `#desktop-dni` y
  `#mobile-dni`. Elegir por ancho de viewport, no por `:visible` (durante la
  animación de GSAP el campo todavía no es visible).

### Archivos/carpetas fuera de alcance local

* `backend/venv/`, `backend/.env`, `backend/.pytest_cache/`, `backend/**/__pycache__/`
  — entorno local y credenciales; nunca se commitean.
* `frontend/node_modules/`, `frontend/dist/` — dependencias y build.
* `output/`, `.playwright-cli/` — artefactos de corridas locales, sin versionar.
* `docs/audits/`, `design-qa.md` — evidencia local de auditorías visuales (ya
  ignorados por git a propósito).
* `C:\Programacion\forestal\` — proyecto desktop Forestal, **otro repo**: no mezclar
  cambios ni versiones entre los dos.
* Las ramas con WIP propio del usuario: no tocar, no rebasar, no descartar.

### Flujo visual, si aplica

* Comando para abrir UI:

  ```bash
  cd frontend
  npm run dev
  ```

  Para evidencia de una tarea, levantarlo y navegar con Playwright interceptando
  `**/api/**` (con `serviceWorkers: 'block'`), y capturar en **1638x969**,
  **1366x768** y **390x844**.

* Carpeta de screenshots:

  ```text
  docs/screenshots/<nombre_tarea>/
  ```

  Cada carpeta lleva un `README.md` que explica las capturas.

* Reporte de revisión visual:

  ```text
  docs/<NOMBRE_TAREA>_VISUAL_REVIEW.md
  ```

  Con fecha, rama/commit validado, comandos ejecutados, resultado de tests, flujo
  probado, screenshots, hallazgos y veredicto (aprobado / aprobado con observaciones
  / no aprobado).

### Orden actual de issues

1. **#188** — completar esta sección 11 de `AGENTS.md` (este trabajo).
2. **#183** — derivar las horas a disposición desde las horas del turno (dato de
   Configuración). **Bloqueado por decisión del negocio**: falta definir de dónde
   sale el total del turno por UN y tipo de proceso, y cómo se define un turno que
   incluye perfilado, que no se puede medir en horas.
3. **#164** — PWA offline: smoke E2E obligatorio del circuito completo. Depende de
   #158, #159, #160, #161, #162, #163 y del PR #165 (circuitos offline abiertos).
4. **PR #172** — reconciliar el circuito offline PWA sobre `main`: está
   `CONFLICTING` y con el CI de frontend en rojo, así que **no se mergea sin
   revisión**: decidir si se rebasa sobre `main` o se descarta.
