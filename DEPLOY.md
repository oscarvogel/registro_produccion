# Deploy de producción — `registro_produccion`

> **Guía canónica.** El deploy de producción se hace con **Coolify** sobre el host
> `fasa_189`. No hay paquete que subir ni archivos que copiar: el build ocurre en el
> host y el reverse proxy es **traefik**.

> **Histórico:** hasta 2026-10-23 este documento describía un flujo manual (paquete
> `.tar.gz` + script `deploy_produccion_fg_main_fasa195.sh` + copia de archivos a un
> Nginx del host). Ese flujo **no sirve más producción**: las rutas que usaba
> (`/srv/apps/registro_produccion`, `/var/www/html/django/produccion_fg/`) no existen
> en el host. Se conserva la referencia al final, sólo como antecedente.

## Topología vigente (verificada el 2026-10-23)

| Componente | Dónde | Publicación |
|---|---|---|
| Host | `fasa_189` = 192.168.0.189 = `fasa-PowerEdge-T40` — público 186.5.245.12, Tailscale `fg-ubuntu` (100.112.112.65) | Coolify 4.4.7 + `coolify-proxy` (traefik v3.6) |
| App en Coolify | `registro-produccion-production` — uuid `4hcjxromkdmdylfjbw0fgvs4` | repo `oscarvogel/registro_produccion`, rama `main`, build pack `dockercompose` |
| Backend producción | servicio `produccion_fg` — imagen `registro_produccion-produccion-fg:latest` | `127.0.0.1:18005` |
| Backend Indufor | servicio `indufor` — imagen `registro_produccion-indufor:latest` | `127.0.0.1:18004` |
| Frontend producción | servicio `frontend_servinlgsm` — nginx dentro del contenedor | traefik → `https://produccion.servinlgsm.com.ar` |
| Frontend Indufor | servicio `frontend_indufor` — nginx dentro del contenedor | traefik → `https://produccion.indufor.com.ar` |
| Secretos por servicio | `/srv/env/registro_produccion/*.env` (root, `700`) | montados como `/run/secrets/registro.env` |
| Base de datos | `fg` en el mismo host | MySQL/MariaDB, por `mysql-central-ca.pem` |

Dos consecuencias que hay que tener presentes:

- **Un deploy actualiza las dos instancias** (producción e Indufor): el compose es uno solo.
- **El frontend lo sirve el contenedor**, no un Nginx del host. Ese nginx interno hace
  proxy de `/api/` al backend de su servicio.

## Alcance obligatorio

El procedimiento:

- despliega **exclusivamente `origin/main`** (ya mergeado y con CI verde);
- reconstruye las cuatro imágenes del compose en el host;
- recrea los cuatro contenedores;
- aplica las migraciones de `db_migrations/` **al arrancar el backend**;
- se verifica con evidencia pública, no con suposiciones.

El procedimiento **no**:

- despliega ramas, tags ni commits que todavía no estén en `main`;
- modifica a mano los `.env` de `/srv/env/registro_produccion/` (son de `root` y el
  usuario `fasa` no tiene `sudo` sin contraseña);
- modifica la base de datos a mano;
- requiere un build local ni subir artefactos.

## Requisitos

### En la computadora local

- Checkout limpio del repositorio y `origin/main` al día.
- Git y GitHub accesibles como remoto `origin`.
- Node.js/npm (para correr la suite del frontend si se quiere verificar local).
- Python 3.12 (para correr la suite del backend).
- Token de la API de Coolify en `%USERPROFILE%\.coolify-token` (sólo para la opción B).

### En `fasa_189`

- Acceso SSH con el alias `fasa_189` (usuario `fasa`), para diagnóstico.
- Docker, Coolify y traefik ya instalados y gestionados por Coolify.

## 1. Preparar `main` y revisar el CI

```powershell
git fetch --prune origin
git log --oneline origin/main -3
gh pr checks <pr>
```

El PR tiene que estar **mergeado** y con **CI verde** antes de desplegar: el CI
(`.github/workflows/ci.yml`) corre los tests del backend y del frontend, pero **no**
despliega. Mergear a `main` no publica nada.

## 2. Desplegar

### Opción A — Panel (la habitual)

1. Panel: <https://coolify.vogelconsultoria.com.ar>
2. App `registro-produccion-production` → **Deploy**.
3. Esperar a que el deployment termine en `finished`.

### Opción B — API (desde la PC de desarrollo, sin SSH)

```powershell
$token = (Get-Content "$env:USERPROFILE\.coolify-token" -Raw).Trim()
$body = @{ uuid = '4hcjxromkdmdylfjbw0fgvs4'; force = $true } | ConvertTo-Json
Invoke-RestMethod -Uri 'https://coolify.vogelconsultoria.com.ar/api/v1/deploy' `
  -Method POST -Headers @{ Authorization = "Bearer $token" } `
  -ContentType 'application/json' -Body $body
```

`force = $true` reconstruye las imágenes sin caché (`docker compose build --no-cache`).
Devuelve el `deployment_uuid` del intento.

Monitorear el intento:

```powershell
$dep = '<deployment_uuid>'
Invoke-RestMethod -Uri "https://coolify.vogelconsultoria.com.ar/api/v1/deployments/$dep" `
  -Headers @{ Authorization = "Bearer $token" }
```

- `status`: `queued` → `in_progress` → `finished` (o `failed`).
- `commit`: **el SHA realmente desplegado**. Es la evidencia de qué versión quedó.
- `logs`: JSON por línea; `output` es la salida del comando y `command` el comando.

En el log se ven, en este orden: el build de las cuatro imágenes, la creación del
`.env` de runtime, el `stop`/`rm` de los contenedores anteriores y el arranque de los
nuevos.

### Opción C — desde el host

El panel de Coolify también está servido en el propio host (`http://127.0.0.1:8000`,
detrás de `coolify-proxy`). Para diagnosticar por SSH:

```bash
ssh fasa_189
docker ps --format '{{.Names}} | {{.Image}} | {{.Status}}' | grep registro_produccion
docker logs --tail 200 <nombre-del-contenedor>
```

Los contenedores se llaman `<servicio>-<uuid-app>-<timestamp>`; el timestamp del
contenedor anterior **es la fecha del deploy anterior**.

## 3. Verificar (obligatorio)

### 3.1 El bundle cambió

```powershell
$html = (Invoke-WebRequest https://produccion.servinlgsm.com.ar/ -UseBasicParsing).Content
[regex]::Match($html, 'assets/index-[A-Za-z0-9_-]+\.js').Value
```

El `Last-Modified` del `index.html` es la fecha del deploy. Si el bundle no cambió,
el deploy no llegó.

### 3.2 Los marcadores del cambio están en el bundle

Los textos de las vistas viven en los **chunks lazy**, no en el bundle principal: para
verificar un cambio hay que buscar el texto en los chunks que el entry referencia.

```powershell
$base = 'https://produccion.servinlgsm.com.ar/'
$entry = [regex]::Match((Invoke-WebRequest $base -UseBasicParsing).Content, 'assets/index-[A-Za-z0-9_-]+\.js').Value
$js = (Invoke-WebRequest "$base$entry" -UseBasicParsing).Content
$chunks = [regex]::Matches($js, 'assets/[A-Za-z0-9_-]+\.js') | ForEach-Object { $_.Value } | Sort-Object -Unique
$todo = $js
foreach ($c in $chunks) { $todo += (Invoke-WebRequest "$base$c" -UseBasicParsing).Content }
$todo.Contains('Total del turno')
```

Sólo la **presencia** de un texto prueba algo: que no aparezca no demuestra que el
deploy sea viejo (el texto puede haber cambiado de nombre, o vivir en otro chunk).

### 3.3 La API responde

```powershell
Invoke-WebRequest https://produccion.servinlgsm.com.ar/api/health -UseBasicParsing | Select-Object -ExpandProperty Content
```

Esperado: HTTP 200 y `"database":"ok"`.

### 3.4 Los contenedores están healthy

```bash
ssh fasa_189 "docker ps --format '{{.Names}} | {{.Status}}' | grep registro_produccion"
```

### 3.5 Smoke funcional

```powershell
# Cargar el login y comprobar que no hay errores de consola (Playwright)
```

Como mínimo: el login carga, el bundle nuevo se está sirviendo y `/api/health` da
`database: ok`. Para la prueba funcional completa (cargar un parte de Caminos) hace
falta una persona operadora con credenciales.

## 4. Sobre las etiquetas de versión

`/api/health` devuelve `version` (`APP_VERSION`) y `commit` (`BUILD_COMMIT`). **Hoy
pueden quedar desactualizadas**: `APP_VERSION` viene de los env files del host y
`BUILD_COMMIT` del `SOURCE_COMMIT` que Coolify inyecta.

Por eso la **evidencia autoritativa** de qué está desplegado es:

1. el `commit` del deployment de Coolify, y
2. el **hash del bundle** que sirve el sitio.

## Rollback

El compose no tiene rollback automático: si el deploy sale mal, la forma segura de
volver atrás es **revertir en `main` y redesplegar** (commit revert + deploy), que
deja el historial auditado.

Si el problema es sólo de configuración del host (por ejemplo un env file), no
improvisar: los `/srv/env/registro_produccion/` son de `root` y no se editan a mano.

## Migraciones

- Se aplican **al arrancar el backend** (`RUN_MIGRATIONS=1` en el compose). El
  pre-deployment command de Coolify no funciona con el build pack `dockercompose`.
- Cada `.sql` de `db_migrations/` tiene que ser **idempotente**: el runner las
  ejecuta en cada arranque.
- Ojo: como el compose despliega las dos instancias, una migración nueva corre en el
  mismo deploy contra la base de producción y contra la de Indufor.
- Si una migración falla, los backends no levantan: el síntoma es
  `produccion_fg` reiniciando en loop. Ver los logs del contenedor.

## Diagnóstico rápido

### El frontend sigue viejo

1. Verificar el hash del bundle (§3.1). Si no cambió, el deploy no llegó.
2. Si el bundle cambió pero el navegador muestra la versión anterior: es el **service
   worker** de la PWA. Recargar sin caché, o desregistrar el SW y limpiar los datos
   del sitio.

### El contenedor no queda healthy

```bash
ssh fasa_189 "docker logs --tail 200 <contenedor>"
```

Causas frecuentes: migración que falla, `.env` del servicio ilegible o build roto.

### `/api/health` dice `commit: unknown`

No es un síntoma de que falte el deploy: es una etiqueta. Ver §4.

### El deploy quedó `failed`

Releer el `logs` del deployment en la API de Coolify: cada línea trae el `command` y
su `output`. Si el fallo es de build, el error está en la etapa de la imagen; si es de
arranque, en la etapa de los contenedores.

## Otros documentos

| Documento | Estado |
|---|---|
| `docs/DEPLOY_GITHUB_MAIN_RUNBOOK.md` | Runbook del **flujo manual anterior** (paquete + Nginx). Legacy: describe un host y rutas que ya no sirven producción. |
| `docs/DEMO_ENVIRONMENT.md`, `docs/DEMO_DEPLOY_RUNBOOK.md` | Instancia `indufor_demo`. |
| `README_DEPLOY.md` | Resumen del flujo anterior. Legacy. |
| `AGENTS.md` §11 | Reglas del proyecto. |
