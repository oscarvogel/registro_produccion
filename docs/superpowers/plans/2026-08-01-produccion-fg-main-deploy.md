# Produccion FG Main Deploy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Entregar un flujo repetible, main-only y sin sudo para desplegar únicamente el backend y frontend de `produccion_fg` en `fasa_195`, con preflight, evidencia y rollback.

**Architecture:** Un nuevo script Bash remoto valida un paquete generado desde `origin/main`, comprueba que la revisión productiva sea ancestro del objetivo y que no haya migraciones pendientes, construye una imagen inmutable y publica sólo `produccion_fg` más su frontend estático. `DEPLOY.md` pasa a ser la guía canónica; un harness de comandos falsos valida las fronteras, el modo read-only y el rollback sin tocar producción.

**Tech Stack:** Bash, Git, Docker Compose, PowerShell, pytest, Vitest/Vite, SSH.

---

## Estructura de archivos

- Crear `scripts/deploy_produccion_fg_main_fasa195.sh`: única entrada remota para `--check` y `--deploy` de `produccion_fg` desde `origin/main`.
- Crear `backend/tests/test_deploy_produccion_fg_main_fasa195.py`: harness dinámico con Git/Docker/curl falsos para preflight, deploy y rollback.
- Modificar `backend/tests/test_deploy_scripts_contract.py`: contrato estático de alcance y documentación canónica.
- Modificar `DEPLOY.md`: runbook operativo principal con comandos copiables y checklist.
- Modificar `docs/DEPLOY_GITHUB_MAIN_RUNBOOK.md`: advertencia visible de que es un flujo multiinstancia y no el procedimiento normal de `produccion_fg`.

### Task 1: Definir el contrato ejecutable en tests

**Files:**
- Create: `backend/tests/test_deploy_produccion_fg_main_fasa195.py`
- Modify: `backend/tests/test_deploy_scripts_contract.py`
- Test: `backend/tests/test_deploy_produccion_fg_main_fasa195.py`

- [ ] **Step 1: Crear fixture de paquete y comandos falsos**

El fixture debe crear un tarball con esta estructura real:

```text
backend/app/main.py
backend/requirements.txt
frontend/dist/index.html
frontend/dist/assets/index-target.js
RELEASE_MANIFEST.txt
```

El manifiesto debe contener:

```text
name=registro_produccion
commit=target-commit
short_commit=target
branch=main
built_at=2026-08-01T00:00:00Z
```

Los binarios falsos deben registrar llamadas en `calls.log`. `git` debe responder a `status --porcelain`, `rev-parse origin/main`, `merge-base --is-ancestor` y `diff --name-only`. `docker` debe responder a `inspect`, `image inspect`, `build`, `run`, `tag` y `compose ... up` sin invocar Docker real.

- [ ] **Step 2: Escribir tests RED de preflight**

Agregar pruebas equivalentes a:

```python
def test_check_is_read_only(harness):
    result = harness.run("--check")
    assert result.returncode == 0, result.stderr
    assert "docker build" not in harness.calls
    assert "docker compose" not in harness.calls


def test_check_rejects_package_not_built_from_origin_main(harness):
    result = harness.run("--check", target_commit="different-main")
    assert result.returncode != 0
    assert "package commit does not match origin/main" in result.stderr


def test_check_rejects_diverged_or_newer_production(harness):
    result = harness.run("--check", deployed_is_ancestor=False)
    assert result.returncode != 0
    assert "deployed commit is not an ancestor" in result.stderr


def test_check_aborts_when_range_contains_db_migrations(harness):
    result = harness.run("--check", changed_files="db_migrations/20260801.sql\n")
    assert result.returncode != 0
    assert "database migrations require a separate procedure" in result.stderr
```

- [ ] **Step 3: Escribir tests RED de alcance y éxito**

```python
def test_deploy_updates_only_produccion_fg(harness):
    result = harness.run("--deploy", "--yes")
    assert result.returncode == 0, result.stderr
    assert "up -d --no-build --no-deps --force-recreate produccion_fg" in harness.calls
    assert "up -d --no-build --no-deps --force-recreate indufor" not in harness.calls
    assert "up -d --no-build --no-deps --force-recreate indufor_demo" not in harness.calls


def test_success_records_backend_frontend_and_unchanged_neighbors(harness):
    result = harness.run("--deploy", "--yes")
    assert "target_commit=target-commit" in result.stdout
    assert "produccion_fg_health=healthy" in result.stdout
    assert "frontend_asset=assets/index-target.js" in result.stdout
    assert "indufor_unchanged=yes" in result.stdout
    assert "indufor_demo_unchanged=yes" in result.stdout
```

- [ ] **Step 4: Escribir tests RED de rollback**

```python
def test_failed_health_restores_image_frontend_and_manifest(harness):
    result = harness.run("--deploy", "--yes", fail_target_health=True)
    assert result.returncode != 0
    assert "docker tag old-image registro_produccion:latest" in harness.calls
    assert harness.manifest["status"] == "rolled_back"
    assert (harness.frontend_dir / "index.html").read_text() == "old frontend"


def test_failed_rollback_is_reported_truthfully(harness):
    result = harness.run("--deploy", "--yes", fail_rollback=True)
    assert result.returncode != 0
    assert harness.manifest["status"] == "rollback_failed"
    assert "rollback failed" in result.stderr
```

- [ ] **Step 5: Extender el contrato estático**

En `test_deploy_scripts_contract.py`, exigir como mínimo:

```python
required_fragments = [
    'REMOTE="origin"',
    'BRANCH="main"',
    'SERVICE="produccion_fg"',
    "--check",
    "--deploy",
    "--yes",
    "git merge-base --is-ancestor",
    "db_migrations",
    "--no-deps",
    "frontend.next",
    "frontend.previous",
    "rollback_failed",
    "indufor_unchanged",
    "indufor_demo_unchanged",
]
```

- [ ] **Step 6: Ejecutar RED**

Run:

```powershell
py -3.12 -m pytest backend/tests/test_deploy_produccion_fg_main_fasa195.py backend/tests/test_deploy_scripts_contract.py -q
```

Expected: FAIL porque `scripts/deploy_produccion_fg_main_fasa195.sh` todavía no existe.

- [ ] **Step 7: Commit de tests RED**

```bash
git add backend/tests/test_deploy_produccion_fg_main_fasa195.py backend/tests/test_deploy_scripts_contract.py
git commit -m "test(deploy): definir contrato exclusivo de produccion_fg"
```

### Task 2: Implementar el script main-only

**Files:**
- Create: `scripts/deploy_produccion_fg_main_fasa195.sh`
- Test: `backend/tests/test_deploy_produccion_fg_main_fasa195.py`

- [ ] **Step 1: Implementar parsing y constantes no reemplazables**

El script debe comenzar con:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

EXPECTED_HOSTNAME="fg-ubuntu"
REMOTE="origin"
BRANCH="main"
SERVICE="produccion_fg"
CONTAINER="registro_produccion_produccion_fg"
HEALTH_URL="http://127.0.0.1:18005/health"
SOURCE_DIR="${SOURCE_DIR:-/srv/apps/registro_produccion}"
APP_PARENT="${APP_PARENT:-/var/www/html/django/produccion_fg}"
BACKUP_DIR="${BACKUP_DIR:-${HOME}/deploy-backups/registro_produccion}"
LOCK_FILE="${LOCK_FILE:-${TMPDIR:-/tmp}/registro_produccion-produccion-fg.lock}"
```

Aceptar únicamente:

```text
--check PACKAGE
--deploy PACKAGE
--deploy --yes PACKAGE
```

Cualquier otra combinación termina con código 2 y muestra el uso.

- [ ] **Step 2: Implementar preflight read-only**

El preflight valida hostname, comandos, checkout limpio, paquete, manifiesto y frontend. Después ejecuta:

```bash
git fetch --prune "$REMOTE"
target_commit="$(git rev-parse "$REMOTE/$BRANCH")"
[[ "$release_commit" == "$target_commit" ]] || fail "package commit does not match origin/main"
git merge-base --is-ancestor "$deployed_commit" "$target_commit" || \
  fail "deployed commit is not an ancestor of origin/main"
changed_migrations="$(git diff --name-only "$deployed_commit" "$target_commit" -- db_migrations)"
[[ -z "$changed_migrations" ]] || fail "database migrations require a separate procedure"
```

También registra IDs de `indufor` e `indufor_demo`, valida `docker compose config` y no construye ni recrea contenedores en `--check`.

- [ ] **Step 3: Implementar backup, imagen y publicación**

En `--deploy`, luego de confirmar `DEPLOY` o recibir `--yes`:

```bash
target_image="registro_produccion:${target_commit}"
docker build --tag "$target_image" .
docker run --rm "$target_image" python -m compileall -q /app
docker run --rm "$target_image" python -c "import app.main"
docker tag "$target_image" registro_produccion:latest
docker compose -f docker-compose.yml up -d --no-build --no-deps --force-recreate produccion_fg
```

El frontend del paquete se extrae primero a `frontend.next-${timestamp}`, se valida y se intercambia atómicamente con `frontend`, conservando `frontend.previous-${timestamp}` hasta finalizar.

- [ ] **Step 4: Implementar rollback completo**

El trap de error restaura en orden:

```text
RELEASE_MANIFEST.txt anterior
frontend anterior
tag registro_produccion:latest anterior
contenedor produccion_fg anterior
health interno
```

Registrar `status=rolled_back` sólo si todas las restauraciones pasan; en otro caso `status=rollback_failed` y un error explícito.

- [ ] **Step 5: Implementar evidencia e invariantes**

La salida de éxito incluye exactamente claves estables:

```text
deploy_status=success
target_commit=${target_commit}
target_image=${target_image}
target_image_id=${target_image_id}
produccion_fg_health=healthy
produccion_fg_health_url=http://127.0.0.1:18005/health
frontend_asset=assets/index-....js
indufor_unchanged=yes
indufor_demo_unchanged=yes
backup_dir=${backup_dir}
```

- [ ] **Step 6: Ejecutar GREEN**

```powershell
py -3.12 -m pytest backend/tests/test_deploy_produccion_fg_main_fasa195.py backend/tests/test_deploy_scripts_contract.py -q
```

Expected: PASS.

- [ ] **Step 7: Verificar sintaxis Bash en el host real sin ejecutar**

```powershell
Get-Content -Raw scripts\deploy_produccion_fg_main_fasa195.sh |
  ssh -o BatchMode=yes fasa_195 'bash -n'
```

Expected: exit 0, sin salida.

- [ ] **Step 8: Commit de implementación**

```bash
git add scripts/deploy_produccion_fg_main_fasa195.sh
git commit -m "feat(deploy): agregar flujo main-only para produccion_fg"
```

### Task 3: Convertir DEPLOY.md en la guía canónica

**Files:**
- Modify: `DEPLOY.md`
- Modify: `docs/DEPLOY_GITHUB_MAIN_RUNBOOK.md`
- Modify: `backend/tests/test_deploy_scripts_contract.py`

- [ ] **Step 1: Escribir test RED de documentación**

Agregar un test que exija en `DEPLOY.md`:

```python
required = [
    "Guía canónica",
    "origin/main",
    "únicamente `produccion_fg`",
    "build_deploy_package.ps1",
    "deploy_produccion_fg_main_fasa195.sh --check",
    "deploy_produccion_fg_main_fasa195.sh --deploy",
    "--no-deps",
    "No aplica migraciones",
    "Service Worker",
    "rollback_failed",
]
```

Agregar otro test que exija en el runbook multiinstancia la advertencia `NO usar para el deploy normal de produccion_fg`.

- [ ] **Step 2: Ejecutar RED documental**

```powershell
py -3.12 -m pytest backend/tests/test_deploy_scripts_contract.py -q
```

Expected: FAIL por textos todavía ausentes.

- [ ] **Step 3: Reescribir DEPLOY.md**

Orden obligatorio:

```text
1. Alcance y prohibiciones
2. Arquitectura y rutas
3. Requisitos
4. Checklist local desde main
5. Generación y subida del paquete
6. --check remoto
7. --deploy remoto
8. Evidencia esperada
9. Verificación pública y PWA
10. Rollback y diagnóstico
11. Migraciones como procedimiento separado
12. Referencias históricas/multiinstancia
```

Eliminar credenciales de ejemplo y comandos que impriman `DATABASE_URL` o contraseñas. No documentar `git reset --hard` como flujo normal.

- [ ] **Step 4: Marcar el runbook multiinstancia**

Agregar al inicio de `docs/DEPLOY_GITHUB_MAIN_RUNBOOK.md`:

```markdown
> **Flujo multiinstancia. NO usar para el deploy normal de `produccion_fg`.**
> El procedimiento canónico está en [`DEPLOY.md`](../DEPLOY.md).
```

- [ ] **Step 5: Ejecutar GREEN documental**

```powershell
py -3.12 -m pytest backend/tests/test_deploy_scripts_contract.py -q
git diff --check
```

Expected: PASS y sin errores de whitespace.

- [ ] **Step 6: Commit documental**

```bash
git add DEPLOY.md docs/DEPLOY_GITHUB_MAIN_RUNBOOK.md backend/tests/test_deploy_scripts_contract.py
git commit -m "docs(deploy): establecer runbook canónico de produccion_fg"
```

### Task 4: Validación integral y PR draft

**Files:**
- Verify: all changed files

- [ ] **Step 1: Ejecutar validaciones completas**

```powershell
git diff --check origin/main...HEAD
py -3.12 -m pytest backend/tests/test_deploy_produccion_fg_main_fasa195.py backend/tests/test_deploy_scripts_contract.py -q
py -3.12 -m compileall backend/app
Push-Location frontend
npm test
npm run build
Pop-Location
```

Expected: todos los comandos terminan con código 0.

- [ ] **Step 2: Ejecutar preflight real sin mutar producción**

Después de que la rama esté mergeada en `main`, generar un paquete desde un checkout limpio de `main`, subirlo y ejecutar:

```bash
cd /srv/apps/registro_produccion
bash scripts/deploy_produccion_fg_main_fasa195.sh --check \
  /home/ferreteria/registro_produccion_deploy_5ee50b0.tar.gz
```

Antes del merge, validar sólo `bash -n` y los tests; no presentar un `--check` de una rama como prueba main-only.

- [ ] **Step 3: Revisar alcance**

```powershell
git diff --stat origin/main...HEAD
git diff --name-status origin/main...HEAD
rg -n "nginx|mysql|DATABASE_URL|indufor_demo|indufor" scripts/deploy_produccion_fg_main_fasa195.sh DEPLOY.md
```

Confirmar que las menciones de Nginx, MySQL e instancias vecinas son prohibiciones o invariantes, nunca acciones.

- [ ] **Step 4: Push y PR draft**

```powershell
git push -u origin codex/tarea-deploy-produccion-fg-main
gh pr create --draft --base main --head codex/tarea-deploy-produccion-fg-main \
  --title "feat(deploy): flujo exclusivo de produccion_fg desde main" \
  --body "## Objetivo

Establecer un deploy main-only y exclusivo de produccion_fg.

## Validaciones

- Tests de contrato
- Sintaxis Bash
- Frontend tests y build

## Fuera de alcance

- Deploy productivo
- Migraciones
- indufor e indufor_demo"
```

La descripción debe incluir objetivo, alcance, archivos, tests, ausencia de deploy productivo, fuera de alcance y `Closes` sólo si existe un issue asociado.
