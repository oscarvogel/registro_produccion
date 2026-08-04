# Deploy desde GitHub main

> **Guía canónica de deploy a `fasa_195` desde `origin/main`.**
> Cubre **backend** (containers `indufor` + `produccion_fg`) y **frontend**
> (estáticos de `produccion_fg` servidos por Nginx).
> El commit debe estar mergeado en `origin/main` antes de empezar.

## Resumen

Un deploy completo a `fasa_195` son **dos pasos secuenciales** sobre el mismo
commit:

1. **Backend** — `scripts/deploy_main_fasa195.sh` recompila la imagen Docker y
   recrea los containers `indufor` (puerto 18004) y `produccion_fg` (puerto
   18005).
2. **Frontend** — `scripts/deploy_produccion_fg_main_fasa195.sh` (vía paquete
   `build_deploy_package.ps1` + `scp`) reemplaza el bundle estático publicado
   en `/var/www/html/django/produccion_fg/frontend/`.

**Si hacés solo el paso 1, el backend queda actualizado pero el frontend
sirve la versión vieja.** El índice `index.html` y el manifest que ven los
operadores se actualiza recién en el paso 2.

## Scripts y lo que hace cada uno

| Script | Qué deploya | Cuándo correrlo |
|---|---|---|
| `scripts/deploy_main_fasa195.sh` | Containers Docker `indufor` + `produccion_fg` (FastAPI + gunicorn) | Cada vez que cambia `backend/` o `Dockerfile` |
| `scripts/deploy_produccion_fg_main_fasa195.sh` (con paquete) | Imagen Docker de `produccion_fg`, frontend estático, manifiesto | Cada vez que cambia `backend/` o `frontend/` |

Ambos scripts comparten el flujo: `git pull --ff-only origin main` →
preflight → build/recreate → healthcheck → rollback automático si algo falla.

## Alcance obligatorio

- Acepta exclusivamente commits mergeados en `origin/main`.
- Backend: actualiza `indufor` y `produccion_fg`. Frontend: actualiza solo
  `produccion_fg` (Nginx publica `https://produccion.servinlgsm.com.ar/` y
  deriva `/api/*` al container `produccion_fg` en `127.0.0.1:18005`).
- Construye imágenes inmutables etiquetadas con el SHA completo.
- Crea backup, manifiesto y rollback automático por script.
- Valida contenedores, healthcheck HTTP y asset del frontend.
- Usa `docker compose ... --no-deps` para no recrear servicios vecinos.

**No** modifica `indufor_demo`, Nginx, archivos `.env`, bases de datos ni
aplica migraciones. **No** requiere `sudo`. **No** imprime contenido de
archivos `.env`.

Si el rango entre la revisión publicada y `origin/main` contiene archivos bajo
`db_migrations/`, el preflight del frontend aborta.

## Requisitos

### En la computadora local

- Checkout limpio del repositorio.
- Git y GitHub accesible como remoto `origin`.
- PowerShell 7.
- Python 3.12 con las dependencias de test del backend.
- Node.js/npm con las dependencias del frontend (`frontend/node_modules`).
- Espacio temporal para materializar el commit y correr `npm ci` + `vite build`.
- SSH/SCP con el alias `fasa_195` configurado (`~/.ssh/config`).

### En `fasa_195`

- Hostname `fg-ubuntu`.
- Usuario autorizado `ferreteria`.
- Acceso a Git, Docker, Compose, `curl`, `tar`, `flock`, `sha256sum`.
- Env files existentes en `/srv/env/registro_produccion/`.

## Flujo completo paso a paso

### 1. Preparar `main` local

Desde PowerShell:

```powershell
Set-Location D:\notebook\active\registro_produccion
git status -sb
git fetch --prune origin
git switch main
git pull --ff-only origin main

$head = (git rev-parse HEAD).Trim()
$originMain = (git rev-parse origin/main).Trim()
if ($head -ne $originMain) {
    throw "HEAD no coincide con origin/main"
}

$trackedChanges = git status --porcelain --untracked-files=no
if ($trackedChanges) {
    throw "Hay cambios trackeados sin commitear"
}
```

No continuar desde una rama de trabajo. El PR debe estar mergeado y visible en
`origin/main`.

### 2. Backend: deploy de containers

Pegá esto en una terminal ssh contra `fasa_195`:

```bash
cd /srv/apps/registro_produccion

# 2a. Preflight (no rompe nada)
bash scripts/deploy_main_fasa195.sh --check
```

**Si termina OK** (`==> Preflight successful`), seguís con:

```bash
# 2b. Deploy (te pide escribir "DEPLOY" cuando lo solicita)
bash scripts/deploy_main_fasa195.sh --deploy
```

O no interactivo, solo después de un `--check` exitoso:

```bash
bash scripts/deploy_main_fasa195.sh --deploy --yes
```

El script construye la imagen, valida Python adentro, recrea `indufor` y
después `produccion_fg` con `--no-deps`, espera health y taggea
`registro_produccion:latest`.

### 3. Frontend: paquete + scp + deploy

El backend se actualizó, pero el bundle estático que ven los operadores
sigue siendo el viejo. Para el frontend:

```powershell
# 3a. Generar el paquete desde la máquina local
# (corre pytest del backend, npm test del frontend, vite build, y empaqueta)
powershell -ExecutionPolicy Bypass -File scripts\build_deploy_package.ps1

$shortSha = (git rev-parse --short HEAD).Trim()
$package = Resolve-Path "dist_deploy\registro_produccion_deploy_$shortSha.tar.gz"
Get-FileHash $package -Algorithm SHA256
```

No usar `-AllowAnyBranch` ni `-SkipTests` para producción. La carpeta
temporal se elimina siempre, tanto al terminar OK como ante un error.

```powershell
# 3b. Subir el paquete a fasa_195
scp $package "fasa_195:/home/ferreteria/$($package.Path | Split-Path -Leaf)"
```

Guardar el SHA256 local para compararlo con la salida del preflight.

```bash
# 3c. Verificar que el checkout remoto esté en el commit correcto
cd /srv/apps/registro_produccion
git status -sb
git rev-parse HEAD
git rev-parse origin/main
```

Si el checkout no coincide, hacer `git fetch --prune origin && git switch main
&& git pull --ff-only origin main`. **No usar `git reset --hard`** para
forzar el procedimiento.

```bash
# 3d. Preflight del frontend (incluye el SHA del paquete)
bash scripts/deploy_produccion_fg_main_fasa195.sh --check \
  /home/ferreteria/registro_produccion_deploy_<short_sha>.tar.gz
```

Debe terminar con `==> Preflight successful` y mostrar
`deployed_commit`, `target_commit` y `package_sha256`. Si aborta por
migraciones nuevas o cualquier otro motivo, detener y revisar.

```bash
# 3e. Deploy del frontend (interactivo)
bash scripts/deploy_produccion_fg_main_fasa195.sh --deploy \
  /home/ferreteria/registro_produccion_deploy_<short_sha>.tar.gz
```

Escribir exactamente `DEPLOY` cuando el script lo pida. O no interactivo
después de un `--check` exitoso:

```bash
bash scripts/deploy_produccion_fg_main_fasa195.sh --deploy --yes \
  /home/ferreteria/registro_produccion_deploy_<short_sha>.tar.gz
```

El script construye la imagen, valida Python dentro de ella, recrea
únicamente `produccion_fg` con `--no-deps`, espera health y después
intercambia el frontend de forma atómica.

## 4. Evidencia y verificación

### Containers (en fasa_195)

```bash
git rev-parse HEAD
docker compose ps
docker inspect -f '{{.Name}} {{.Image}} {{.State.Health.Status}}' \
  registro_produccion_indufor \
  registro_produccion_produccion_fg
curl -fsS http://127.0.0.1:18004/health
curl -fsS http://127.0.0.1:18005/health
```

### Manifiesto del deploy del frontend

```bash
cat /var/www/html/django/produccion_fg/RELEASE_MANIFEST.txt
grep -E '^(commit|branch)=' \
  /var/www/html/django/produccion_fg/RELEASE_MANIFEST.txt
```

### Frontend público (en la máquina local)

La red de `fasa_195` no tiene hairpin NAT confiable. Verificar el sitio
público desde afuera:

```powershell
$response = Invoke-WebRequest https://produccion.servinlgsm.com.ar/ -UseBasicParsing
$response.StatusCode
[regex]::Match($response.Content, 'assets/index-[A-Za-z0-9_-]+\.js').Value
```

Resultado esperado: HTTP 200 + un `assets/index-*.js` igual al
`frontend_asset` informado por el deploy.

Adicional: corroborar que el `index.html` público tiene los tags esperados
(theme-color, apple-mobile-web-app-capable, etc.) y que `manifest.webmanifest`
incluye `id`, `lang` y `scope`:

```powershell
$html = (Invoke-WebRequest https://produccion.servinlgsm.com.ar/ -UseBasicParsing).Content
$html -match 'theme-color'
$html -match 'apple-mobile-web-app-capable'

$manifest = (Invoke-WebRequest https://produccion.servinlgsm.com.ar/manifest.webmanifest -UseBasicParsing).Content
$manifest -match '"id"'
$manifest -match '"lang"\s*:\s*"es-AR"'
```

### PWA en celulares

Para la prueba funcional, pedir a una persona operadora que cierre y vuelva a
abrir la aplicación. Si la PWA conserva la revisión anterior:

1. hacer recarga completa;
2. desregistrar el Service Worker;
3. limpiar los datos del sitio;
4. abrir nuevamente la aplicación.

## Rollback

El rollback es **automático e independiente por script**:

- `deploy_main_fasa195.sh` (backend): si falla `indufor`, restaura solamente
  `indufor` y no actualiza `produccion_fg`. Si falla `produccion_fg`,
  restaura **ambas** instancias para que no queden en revisiones diferentes.
- `deploy_produccion_fg_main_fasa195.sh` (frontend): si falla la imagen, el
  health o el intercambio atómico del frontend, restaura la imagen, el
  contenedor, el frontend y el manifiesto anteriores.

Los manifiestos quedan en `~/.deploy-backups/registro_produccion/` con uno de
estos estados:

- `status=success`;
- `status=rolled_back`;
- `status=rollback_failed`.

Si aparece `rollback_failed`, no improvisar cambios sobre Nginx, `.env`,
bases o instancias vecinas. Conservar la salida, revisar el backup, el ID de
imagen y el estado del contenedor.

## Diagnóstico rápido

### El backend quedó bien pero el frontend sigue viejo

El deploy del backend (`deploy_main_fasa195.sh`) **no toca el frontend**. Si
solo corriste ese paso, falta el paso 3 de este runbook.

Comparar el asset publicado con la salida del deploy:

```bash
grep -oE 'assets/index-[A-Za-z0-9_-]+\.js' \
  /var/www/html/django/produccion_fg/frontend/index.html | head -1
```

Si el server tiene el asset correcto, aplicar los pasos de PWA/Service
Worker del apartado anterior.

### El contenedor no queda healthy

```bash
docker inspect registro_produccion_produccion_fg \
  --format '{{.Image}}|{{.State.Status}}|{{.State.Health.Status}}'
docker logs registro_produccion_produccion_fg --tail 100
```

No mostrar ni copiar secretos de los logs.

### El preflight del frontend dice que producción no es ancestro de main

Existe una revisión desplegada que todavía no fue mergeada o el historial
divergió. Mergear primero el PR correcto o preparar un rollback explícito. No
forzar el deploy.

## Otros documentos

- [`DEPLOY.md`](../DEPLOY.md): flujo detallado del paso 3 (frontend) con
  descripción de cada variable de entorno y de los archivos publicados.
- `docs/DEMO_DEPLOY_RUNBOOK.md`: entorno demo.
- `README_DEPLOY.md`: referencia histórica de la migración Docker.
