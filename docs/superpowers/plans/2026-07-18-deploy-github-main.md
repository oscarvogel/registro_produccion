# GitHub Main Docker Deploy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear y ejecutar un deploy seguro desde `origin/main` que actualice `indufor` y `produccion_fg` en `fasa_195`, con preflight, imagen inmutable, healthchecks y rollback.

**Architecture:** Un script Bash servidor controla el checkout Git y construye una imagen etiquetada por commit. Un override Compose temporal selecciona esa imagen para actualizar secuencialmente las dos instancias, mientras un manifiesto conserva el estado anterior para rollback. Las pruebas Python verifican el contrato estático y un harness Bash simula Git, Docker y curl para probar preflight, orden y rollback sin tocar infraestructura real.

**Tech Stack:** Bash 5, Git, Docker Compose v2, Python 3.12, pytest.

---

### Task 1: Contrato estático del script

**Files:**
- Modify: `backend/tests/test_deploy_scripts_contract.py`
- Create: `scripts/deploy_main_fasa195.sh`

- [ ] **Step 1: Escribir la prueba estática fallida**

Agregar a `backend/tests/test_deploy_scripts_contract.py`:

```python
def test_github_main_docker_deploy_has_safe_contract():
    script = read("scripts/deploy_main_fasa195.sh")

    required_fragments = [
        'EXPECTED_HOSTNAME="${EXPECTED_HOSTNAME:-fg-ubuntu}"',
        'APP_DIR="${APP_DIR:-/srv/apps/registro_produccion}"',
        'REMOTE="${REMOTE:-origin}"',
        'BRANCH="${BRANCH:-main}"',
        "--check",
        "--deploy",
        "--yes",
        "flock",
        "git status --porcelain",
        "git fetch --prune",
        "git merge-base --is-ancestor",
        "git merge --ff-only",
        "registro_produccion:${target_commit}",
        "docker compose config",
        "python -m compileall",
        "import app.main",
        "indufor produccion_fg",
        "http://127.0.0.1:18004/health",
        "http://127.0.0.1:18005/health",
        ".deploy-backups",
        "rollback",
    ]

    missing = [fragment for fragment in required_fragments if fragment not in script]
    assert missing == []
```

- [ ] **Step 2: Ejecutar la prueba y comprobar RED**

Run:

```powershell
& 'C:\Users\Ventas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -m pytest backend/tests/test_deploy_scripts_contract.py::test_github_main_docker_deploy_has_safe_contract -q
```

Expected: `FAIL` porque `scripts/deploy_main_fasa195.sh` todavía no existe.

- [ ] **Step 3: Crear la estructura mínima del script**

Crear `scripts/deploy_main_fasa195.sh` con:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

EXPECTED_HOSTNAME="${EXPECTED_HOSTNAME:-fg-ubuntu}"
APP_DIR="${APP_DIR:-/srv/apps/registro_produccion}"
REMOTE="${REMOTE:-origin}"
BRANCH="${BRANCH:-main}"
BACKUP_DIR="${BACKUP_DIR:-$APP_DIR/.deploy-backups}"
LOCK_FILE="${LOCK_FILE:-$APP_DIR/.deploy-main.lock}"
SERVICES=(indufor produccion_fg)
HEALTH_INDUFOR="${HEALTH_INDUFOR:-http://127.0.0.1:18004/health}"
HEALTH_PRODUCCION_FG="${HEALTH_PRODUCCION_FG:-http://127.0.0.1:18005/health}"

usage() {
  printf '%s\n' \
    "Usage: $0 --check" \
    "       $0 --deploy [--yes]"
}

mode=""
assume_yes=false
for argument in "$@"; do
  case "$argument" in
    --check|--deploy) mode="$argument" ;;
    --yes) assume_yes=true ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'ERROR: unknown argument: %s\n' "$argument" >&2; exit 2 ;;
  esac
done
[[ -n "$mode" ]] || { usage >&2; exit 2; }

rollback() {
  printf 'ERROR: rollback requested before implementation\n' >&2
  return 1
}

printf '%s\n' \
  "git status --porcelain" \
  "git fetch --prune" \
  "git merge-base --is-ancestor" \
  "git merge --ff-only" \
  'registro_produccion:${target_commit}' \
  "docker compose config" \
  "python -m compileall" \
  "import app.main" \
  "indufor produccion_fg" \
  "$HEALTH_INDUFOR" \
  "$HEALTH_PRODUCCION_FG" \
  "$BACKUP_DIR"
command -v flock >/dev/null
```

- [ ] **Step 4: Ejecutar prueba estática y sintaxis**

Run:

```powershell
& 'C:\Users\Ventas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -m pytest backend/tests/test_deploy_scripts_contract.py::test_github_main_docker_deploy_has_safe_contract -q
bash -n scripts/deploy_main_fasa195.sh
```

Expected: test `PASS`; `bash -n` exit code `0`.

- [ ] **Step 5: Commit**

```powershell
git add backend/tests/test_deploy_scripts_contract.py scripts/deploy_main_fasa195.sh
git commit -m "test: define safe GitHub deploy contract"
```

### Task 2: Harness de preflight y checkout fast-forward

**Files:**
- Create: `backend/tests/test_deploy_main_fasa195.py`
- Modify: `scripts/deploy_main_fasa195.sh`

- [ ] **Step 1: Escribir pruebas fallidas de preflight**

Crear un harness que copie el script a un directorio temporal, anteponga
ejecutables fake a `PATH` y registre invocaciones en `CALL_LOG`. Agregar:

```python
def test_check_rejects_dirty_checkout(deploy_harness):
    result = deploy_harness.run("--check", git_status=" M backend/app/main.py")
    assert result.returncode != 0
    assert "checkout is not clean" in result.stderr
    assert "docker compose up" not in deploy_harness.calls


def test_check_rejects_non_fast_forward_main(deploy_harness):
    result = deploy_harness.run("--check", merge_base_exit=1)
    assert result.returncode != 0
    assert "not a fast-forward" in result.stderr


def test_check_is_read_only(deploy_harness):
    result = deploy_harness.run("--check")
    assert result.returncode == 0
    assert "git merge --ff-only" not in deploy_harness.calls
    assert "docker compose build" not in deploy_harness.calls
    assert "docker compose up" not in deploy_harness.calls
```

El fixture debe crear fakes deterministas para `hostname`, `git`, `docker`,
`curl`, `flock` y `sleep`; nunca debe invocar herramientas reales.

- [ ] **Step 2: Ejecutar y comprobar RED**

```powershell
& 'C:\Users\Ventas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -m pytest backend/tests/test_deploy_main_fasa195.py -q
```

Expected: fallos por ausencia de preflight real.

- [ ] **Step 3: Implementar preflight**

Reemplazar la estructura provisional por funciones:

```bash
log() { printf '==> %s\n' "$*"; }
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
require_command() { command -v "$1" >/dev/null 2>&1 || fail "missing command: $1"; }

preflight() {
  [[ "$(hostname)" == "$EXPECTED_HOSTNAME" ]] ||
    fail "hostname must be $EXPECTED_HOSTNAME"
  for command_name in git docker curl flock; do
    require_command "$command_name"
  done
  [[ -d "$APP_DIR/.git" ]] || fail "application checkout not found: $APP_DIR"
  cd "$APP_DIR"
  [[ -z "$(git status --porcelain)" ]] || fail "checkout is not clean"
  [[ -f /srv/env/registro_produccion/indufor.env ]] ||
    fail "missing indufor env file"
  [[ -f /srv/env/registro_produccion/produccion_fg.env ]] ||
    fail "missing produccion_fg env file"
  git fetch --prune "$REMOTE"
  target_commit="$(git rev-parse "$REMOTE/$BRANCH")"
  current_commit="$(git rev-parse HEAD)"
  git merge-base --is-ancestor "$current_commit" "$target_commit" ||
    fail "current commit is not a fast-forward of $REMOTE/$BRANCH"
  if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
    local_main="$(git rev-parse "$BRANCH")"
    git merge-base --is-ancestor "$local_main" "$target_commit" ||
      fail "local $BRANCH is not a fast-forward of $REMOTE/$BRANCH"
  fi
  docker compose config >/dev/null
  available_services="$(docker compose config --services)"
  for service in "${SERVICES[@]}"; do
    grep -Fxq "$service" <<<"$available_services" ||
      fail "missing compose service: $service"
  done
}
```

Adquirir el lock con descriptor:

```bash
exec 9>"$LOCK_FILE"
flock -n 9 || fail "another deploy is running"
```

En `--check`, terminar después de `preflight` mostrando commit actual y commit
objetivo, sin cambiar el checkout.

- [ ] **Step 4: Ejecutar pruebas de preflight**

```powershell
& 'C:\Users\Ventas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -m pytest backend/tests/test_deploy_main_fasa195.py -q
```

Expected: `3 passed`.

- [ ] **Step 5: Commit**

```powershell
git add backend/tests/test_deploy_main_fasa195.py scripts/deploy_main_fasa195.sh
git commit -m "feat: add guarded deploy preflight"
```

### Task 3: Imagen inmutable y actualización secuencial

**Files:**
- Modify: `backend/tests/test_deploy_main_fasa195.py`
- Modify: `scripts/deploy_main_fasa195.sh`

- [ ] **Step 1: Escribir pruebas fallidas de despliegue**

Agregar:

```python
def test_deploy_builds_commit_image_and_updates_services_in_order(deploy_harness):
    result = deploy_harness.run("--deploy", "--yes", target_commit="abc123")
    assert result.returncode == 0
    calls = deploy_harness.calls.splitlines()
    assert "git switch main" in calls
    assert "git merge --ff-only origin/main" in calls
    assert "docker build --tag registro_produccion:abc123 ." in calls
    assert calls.index("compose_up indufor abc123") < calls.index(
        "compose_up produccion_fg abc123"
    )
    assert "curl http://127.0.0.1:18004/health" in calls
    assert "curl http://127.0.0.1:18005/health" in calls


def test_deploy_requires_confirmation_without_yes(deploy_harness):
    result = deploy_harness.run("--deploy", stdin="NO\n")
    assert result.returncode != 0
    assert "deployment cancelled" in result.stderr
```

- [ ] **Step 2: Ejecutar y comprobar RED**

```powershell
& 'C:\Users\Ventas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -m pytest backend/tests/test_deploy_main_fasa195.py -q
```

Expected: fallos porque no existen build, confirmación ni actualización.

- [ ] **Step 3: Implementar build y despliegue**

Agregar confirmación y funciones:

```bash
confirm_deploy() {
  [[ "$assume_yes" == true ]] && return
  [[ -t 0 ]] || fail "--deploy requires an interactive terminal or --yes"
  read -r -p "Type DEPLOY to continue: " answer
  [[ "$answer" == DEPLOY ]] || fail "deployment cancelled"
}

write_override() {
  override_file="$(mktemp)"
  cat >"$override_file" <<YAML
services:
  indufor:
    image: registro_produccion:${target_commit}
  produccion_fg:
    image: registro_produccion:${target_commit}
YAML
}

compose_target() {
  docker compose -f docker-compose.yml -f "$override_file" "$@"
}

wait_healthy() {
  local container="$1"
  local health_url="$2"
  for _ in {1..30}; do
    if [[ "$(docker inspect -f '{{.State.Health.Status}}' "$container")" == healthy ]]; then
      curl -fsS "$health_url" >/dev/null
      return
    fi
    sleep 2
  done
  return 1
}
```

El flujo principal debe ejecutar:

```bash
git switch "$BRANCH"
git merge --ff-only "$REMOTE/$BRANCH"
target_commit="$(git rev-parse HEAD)"
target_image="registro_produccion:${target_commit}"
docker build --tag "$target_image" .
docker run --rm "$target_image" python -m compileall -q /app
docker run --rm "$target_image" python -c "import app.main"
write_override
compose_target up -d --no-build --force-recreate indufor
wait_healthy registro_produccion_indufor "$HEALTH_INDUFOR"
compose_target up -d --no-build --force-recreate produccion_fg
wait_healthy registro_produccion_produccion_fg "$HEALTH_PRODUCCION_FG"
docker tag "$target_image" registro_produccion:latest
```

- [ ] **Step 4: Ejecutar pruebas**

```powershell
& 'C:\Users\Ventas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -m pytest backend/tests/test_deploy_main_fasa195.py -q
bash -n scripts/deploy_main_fasa195.sh
```

Expected: pruebas `PASS`; sintaxis exit code `0`.

- [ ] **Step 5: Commit**

```powershell
git add backend/tests/test_deploy_main_fasa195.py scripts/deploy_main_fasa195.sh
git commit -m "feat: deploy immutable image sequentially"
```

### Task 4: Manifiesto y rollback

**Files:**
- Modify: `backend/tests/test_deploy_main_fasa195.py`
- Modify: `scripts/deploy_main_fasa195.sh`

- [ ] **Step 1: Escribir pruebas fallidas de rollback**

Agregar:

```python
def test_indufor_failure_restores_only_indufor(deploy_harness):
    result = deploy_harness.run(
        "--deploy", "--yes", fail_health="registro_produccion_indufor"
    )
    assert result.returncode != 0
    assert "rollback_service indufor old-indufor-image" in deploy_harness.calls
    assert "compose_up produccion_fg" not in deploy_harness.calls


def test_produccion_failure_restores_both_services(deploy_harness):
    result = deploy_harness.run(
        "--deploy", "--yes", fail_health="registro_produccion_produccion_fg"
    )
    assert result.returncode != 0
    assert "rollback_service produccion_fg old-produccion-image" in deploy_harness.calls
    assert "rollback_service indufor old-indufor-image" in deploy_harness.calls
    assert "curl http://127.0.0.1:18004/health" in deploy_harness.calls
    assert "curl http://127.0.0.1:18005/health" in deploy_harness.calls


def test_manifest_records_previous_and_target_state(deploy_harness):
    result = deploy_harness.run("--deploy", "--yes", target_commit="abc123")
    assert result.returncode == 0
    manifest = deploy_harness.latest_manifest()
    assert manifest["target_commit"] == "abc123"
    assert manifest["previous_indufor_image"] == "old-indufor-image"
    assert manifest["previous_produccion_fg_image"] == "old-produccion-image"
```

- [ ] **Step 2: Ejecutar y comprobar RED**

```powershell
& 'C:\Users\Ventas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -m pytest backend/tests/test_deploy_main_fasa195.py -q
```

Expected: fallos por falta de manifiesto y rollback.

- [ ] **Step 3: Implementar captura y restauración**

Capturar imágenes y escribir el manifiesto sin secretos:

```bash
previous_branch="$(git branch --show-current)"
previous_commit="$(git rev-parse HEAD)"
previous_indufor_image="$(docker inspect -f '{{.Image}}' registro_produccion_indufor)"
previous_produccion_image="$(docker inspect -f '{{.Image}}' registro_produccion_produccion_fg)"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP_DIR"
manifest="$BACKUP_DIR/deploy_${timestamp}_${target_commit}.env"
printf '%s\n' \
  "previous_branch=$previous_branch" \
  "previous_commit=$previous_commit" \
  "previous_indufor_image=$previous_indufor_image" \
  "previous_produccion_fg_image=$previous_produccion_image" \
  "target_commit=$target_commit" >"$manifest"
```

`rollback_service` debe crear un override temporal con el ID de imagen anterior,
recrear sólo el servicio solicitado y esperar su healthcheck. Un trap `ERR`
debe consultar marcadores `indufor_updated` y `produccion_updated`: si falló la
segunda instancia restaura ambas; si falló la primera restaura sólo `indufor`.
Después restaura la rama y el commit mediante:

```bash
git switch "$previous_branch"
git reset --keep "$previous_commit"
```

El trap debe deshabilitarse durante el propio rollback para evitar recursión.

- [ ] **Step 4: Ejecutar suite del nuevo script**

```powershell
& 'C:\Users\Ventas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -m pytest backend/tests/test_deploy_main_fasa195.py backend/tests/test_deploy_scripts_contract.py -q
bash -n scripts/deploy_main_fasa195.sh
```

Expected: todas las pruebas `PASS`; sintaxis exit code `0`.

- [ ] **Step 5: Commit**

```powershell
git add backend/tests/test_deploy_main_fasa195.py scripts/deploy_main_fasa195.sh
git commit -m "feat: rollback failed Docker deployments"
```

### Task 5: Documentación y validación local completa

**Files:**
- Create: `docs/DEPLOY_GITHUB_MAIN_RUNBOOK.md`
- Modify: `backend/tests/test_deploy_scripts_contract.py`

- [ ] **Step 1: Escribir contrato documental fallido**

Agregar:

```python
def test_github_main_runbook_documents_safe_operator_flow():
    runbook = read("docs/DEPLOY_GITHUB_MAIN_RUNBOOK.md")
    required = [
        "--check",
        "--deploy",
        "--yes",
        "indufor",
        "produccion_fg",
        "indufor_demo",
        "Nginx",
        ".env",
        "rollback",
    ]
    assert [fragment for fragment in required if fragment not in runbook] == []
```

- [ ] **Step 2: Ejecutar y comprobar RED**

```powershell
& 'C:\Users\Ventas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -m pytest backend/tests/test_deploy_scripts_contract.py::test_github_main_runbook_documents_safe_operator_flow -q
```

Expected: `FAIL` porque el runbook no existe.

- [ ] **Step 3: Crear runbook**

Documentar:

```markdown
# Deploy desde GitHub main

## Alcance

Actualiza exclusivamente los servicios Docker `indufor` y `produccion_fg`.
No modifica Nginx, archivos `.env`, bases de datos ni `indufor_demo`.

## Preflight

`bash scripts/deploy_main_fasa195.sh --check`

## Deploy interactivo

`bash scripts/deploy_main_fasa195.sh --deploy`

## Deploy no interactivo aprobado

`bash scripts/deploy_main_fasa195.sh --deploy --yes`

## Evidencia y rollback

Los manifiestos quedan en `.deploy-backups/`. Ante un healthcheck fallido el
script ejecuta rollback automático y vuelve a comprobar ambas instancias.
```

- [ ] **Step 4: Ejecutar validación completa**

```powershell
& 'C:\Users\Ventas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -m pytest backend/tests/test_deploy_main_fasa195.py backend/tests/test_deploy_scripts_contract.py backend/tests/test_demo_deploy_contract.py -q
bash -n scripts/deploy_main_fasa195.sh
git diff --check origin/main...HEAD
git status -sb
```

Expected: todas las pruebas `PASS`; Bash exit code `0`; diff check limpio; sólo
archivos de alcance presentes.

- [ ] **Step 5: Commit**

```powershell
git add docs/DEPLOY_GITHUB_MAIN_RUNBOOK.md backend/tests/test_deploy_scripts_contract.py
git commit -m "docs: add GitHub main deploy runbook"
```

### Task 6: Publicar rama y ejecutar en fasa_195

**Files:**
- Remote checkout: `/srv/apps/registro_produccion`
- Remote evidence: `/srv/apps/registro_produccion/.deploy-backups/`

- [ ] **Step 1: Repetir verificación antes de publicar**

```powershell
& 'C:\Users\Ventas\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe' -m pytest backend/tests/test_deploy_main_fasa195.py backend/tests/test_deploy_scripts_contract.py backend/tests/test_demo_deploy_contract.py -q
bash -n scripts/deploy_main_fasa195.sh
git diff --check origin/main...HEAD
```

Expected: todo `PASS`.

- [ ] **Step 2: Integrar el script en main**

Publicar la rama, abrir PR draft, revisar el diff completo y, si las validaciones
remotas obligatorias pasan, pasar a ready y mergear. No desplegar una rama de
feature: el servidor debe recibir el script desde `origin/main`.

- [ ] **Step 3: Confirmar main remoto**

```powershell
git fetch --prune origin
git rev-parse origin/main
```

Expected: commit de merge que contiene `scripts/deploy_main_fasa195.sh`.

- [ ] **Step 4: Ejecutar preflight remoto**

```powershell
ssh fasa_195 "cd /srv/apps/registro_produccion && git fetch --prune origin && git switch main && git merge --ff-only origin/main && bash scripts/deploy_main_fasa195.sh --check"
```

Expected: checkout limpio, Compose válido, ambos env files presentes y
fast-forward confirmado.

- [ ] **Step 5: Ejecutar deploy remoto**

```powershell
ssh fasa_195 "cd /srv/apps/registro_produccion && bash scripts/deploy_main_fasa195.sh --deploy --yes"
```

Expected: build exitoso; `indufor` y `produccion_fg` actualizados
secuencialmente y saludables.

- [ ] **Step 6: Verificar evidencia viva**

```powershell
ssh fasa_195 "cd /srv/apps/registro_produccion && git status -sb && git rev-parse HEAD && docker compose ps && docker inspect -f '{{.Name}} {{.Image}} {{.State.Health.Status}}' registro_produccion_indufor registro_produccion_produccion_fg && curl -fsS http://127.0.0.1:18004/health && curl -fsS http://127.0.0.1:18005/health"
```

Expected: servidor en `main`, HEAD igual a `origin/main`, ambos contenedores con
la misma imagen del commit y estado `healthy`, ambos endpoints HTTP exitosos.

- [ ] **Step 7: Reporte final**

Informar commit/PR/merge, manifiesto remoto, imagen desplegada, estado de ambas
instancias, healthchecks, límites preservados y estado final del checkout.
