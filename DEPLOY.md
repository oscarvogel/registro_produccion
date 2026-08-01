# Deploy de producción — `produccion_fg`

> **Guía canónica.** Este es el procedimiento oficial para desplegar
> únicamente `produccion_fg` en `fasa_195` desde `origin/main`.

El objetivo es que una persona autorizada pueda ejecutar el despliegue sin
conocer previamente la arquitectura y obtener evidencia suficiente para
confirmar o revertir el cambio.

## Alcance obligatorio

El procedimiento:

- acepta exclusivamente un paquete construido desde el commit actual de
  `origin/main`;
- actualiza juntos el backend Docker y el frontend estático de
  `produccion_fg`;
- construye una imagen inmutable etiquetada con el SHA completo;
- asigna esa imagen únicamente a `produccion_fg` mediante un override temporal,
  sin modificar la etiqueta `registro_produccion:latest` compartida;
- crea backup, manifiesto y rollback automático;
- valida el contenedor, el endpoint interno y el asset del frontend;
- usa `docker compose ... --no-deps` para no recrear servicios vecinos.

El procedimiento **no**:

- despliega ramas, tags ni commits que todavía no estén en `main`;
- modifica `indufor` ni `indufor_demo`;
- modifica Nginx, archivos `.env` o credenciales;
- consulta ni modifica bases de datos;
- aplica migraciones;
- requiere `sudo`.

Si el rango entre la revisión publicada y `origin/main` contiene archivos bajo
`db_migrations/`, el preflight aborta. Ver [Migraciones](#migraciones).

## Arquitectura vigente

| Componente | Ruta o puerto | Publicación |
|---|---|---|
| Repo remoto | `/srv/apps/registro_produccion` | Checkout Git usado para construir la imagen |
| Backend | `registro_produccion_produccion_fg` | Docker, host `127.0.0.1:18005` |
| Frontend | `/var/www/html/django/produccion_fg/frontend/` | Archivos estáticos servidos por Nginx |
| Manifiesto | `/var/www/html/django/produccion_fg/RELEASE_MANIFEST.txt` | Commit publicado |
| Backups | `~/deploy-backups/registro_produccion/` | Imagen, frontend y manifiesto recuperables |

Nginx publica `https://produccion.servinlgsm.com.ar/` y deriva `/api/*` al
puerto interno `18005`. Este flujo no modifica esa configuración.

## Requisitos

### En la computadora local

- Checkout limpio del repositorio.
- Git y GitHub accesible como remoto `origin`.
- PowerShell 7.
- Python 3.12 con las dependencias de test del backend.
- Node.js/npm con las dependencias del frontend.
- Espacio temporal suficiente para materializar el commit e instalar sus
  dependencias con `npm ci`.
- SSH/SCP con el alias `fasa_195` configurado.

### En `fasa_195`

- Hostname `fg-ubuntu`.
- Usuario autorizado `ferreteria`.
- Acceso a Git, Docker, Compose, `curl`, `tar`, `flock` y `sha256sum`.
- Permiso del usuario sobre Docker, el repo remoto y el directorio del
  frontend.

No hace falta `sudo`. No imprimir el contenido de ningún `.env`.

## 1. Preparar `main` local

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

## 2. Validar y generar el paquete

El generador materializa `HEAD` en un directorio temporal mediante
`git archive`, instala el frontend con `npm ci` y ejecuta tests del backend,
tests del frontend y build Vite sobre esa copia. El paquete se copia
exclusivamente desde el commit materializado: archivos locales no trackeados o
ignorados no pueden incorporarse. También verifica que el paquete no contenga
`.env` y escribe `RELEASE_MANIFEST.txt`.

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_deploy_package.ps1

$shortSha = (git rev-parse --short HEAD).Trim()
$fullSha = (git rev-parse HEAD).Trim()
$package = Resolve-Path "dist_deploy\registro_produccion_deploy_$shortSha.tar.gz"
Get-FileHash $package -Algorithm SHA256
```

No usar `-AllowAnyBranch` ni `-SkipTests` para producción.

La carpeta temporal se elimina siempre, tanto al terminar correctamente como
ante un error.

## 3. Subir el paquete

```powershell
scp $package "fasa_195:/home/ferreteria/$($package.Path | Split-Path -Leaf)"
```

Guardar el SHA256 local para compararlo con la salida del preflight.

## 4. Actualizar el checkout remoto

Esto actualiza únicamente el checkout Git; todavía no cambia contenedores ni
frontend publicado.

```powershell
ssh -o BatchMode=yes fasa_195
```

En el servidor:

```bash
cd /srv/apps/registro_produccion
git status -sb
git fetch --prune origin
git switch main
git pull --ff-only origin main
test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"
```

Si el checkout no está limpio o el pull no es fast-forward, detenerse. No usar
`git reset --hard` para forzar el procedimiento.

## 5. Ejecutar el preflight

Reemplazar el nombre de ejemplo por el paquete generado en el paso 2:

```bash
cd /srv/apps/registro_produccion
bash scripts/deploy_produccion_fg_main_fasa195.sh --check \
  /home/ferreteria/registro_produccion_deploy_5ee50b0.tar.gz
```

El modo `--check` puede ejecutar `git fetch`, inspeccionar Docker y extraer el
paquete en un temporal. No construye imágenes, no recrea contenedores y no
publica archivos.

Debe terminar con:

```text
==> Preflight successful
deployed_commit=...
target_commit=...
package_sha256=...
```

Detenerse si:

- el paquete no coincide con `origin/main`;
- el checkout remoto no coincide con `origin/main`;
- la revisión publicada no es ancestro de `origin/main`;
- hay migraciones entre ambas revisiones;
- el contenedor actual no está healthy;
- faltan el frontend o el manifiesto actuales.

## 6. Ejecutar el deploy

### Interactivo, recomendado

```bash
cd /srv/apps/registro_produccion
bash scripts/deploy_produccion_fg_main_fasa195.sh --deploy \
  /home/ferreteria/registro_produccion_deploy_5ee50b0.tar.gz
```

Escribir exactamente `DEPLOY` cuando se solicite.

### No interactivo

Usar solamente después de revisar un `--check` exitoso:

```bash
cd /srv/apps/registro_produccion
bash scripts/deploy_produccion_fg_main_fasa195.sh --deploy --yes \
  /home/ferreteria/registro_produccion_deploy_5ee50b0.tar.gz
```

El script construye la imagen, valida Python dentro de ella, recrea únicamente
`produccion_fg` con `--no-deps`, espera health y después intercambia el
frontend de forma atómica.

## 7. Revisar la evidencia

Una ejecución correcta termina con estas claves:

```text
deploy_status=success
target_commit=...
target_image=registro_produccion:...
target_image_id=sha256:...
produccion_fg_health=healthy
produccion_fg_health_url=http://127.0.0.1:18005/health
frontend_asset=assets/index-....js
indufor_unchanged=yes
indufor_demo_unchanged=yes
backup_dir=...
```

Comprobación adicional en el servidor:

```bash
docker inspect registro_produccion_produccion_fg \
  --format '{{.Image}}|{{.State.Health.Status}}'
curl -fsS http://127.0.0.1:18005/health
grep -E '^(commit|branch)=' \
  /var/www/html/django/produccion_fg/RELEASE_MANIFEST.txt
```

El campo `version` del health puede provenir del `.env` y quedar desactualizado.
La evidencia autoritativa es el commit del manifiesto junto con el ID real de
la imagen activa.

## 8. Verificación pública y PWA

La red de `fasa_195` no tiene hairpin NAT confiable. Verificar el sitio público
desde la computadora local:

```powershell
$response = Invoke-WebRequest https://produccion.servinlgsm.com.ar/ -UseBasicParsing
$response.StatusCode
[regex]::Match($response.Content, 'assets/index-[A-Za-z0-9_-]+\.js').Value
```

Resultado esperado: HTTP 200 y el mismo `frontend_asset` informado por el
deploy.

Para la prueba funcional, pedir a una persona operadora que cierre y vuelva a
abrir la aplicación. Si la PWA conserva la revisión anterior:

1. hacer recarga completa;
2. desregistrar el Service Worker;
3. limpiar los datos del sitio;
4. abrir nuevamente la aplicación.

## Rollback

El rollback es automático si falla la imagen, el health, el frontend, el
manifiesto o las invariantes de servicios vecinos. Restaura:

1. imagen/tag anterior de `produccion_fg`;
2. contenedor anterior;
3. frontend anterior;
4. `RELEASE_MANIFEST.txt` anterior;
5. health interno.

El manifiesto del intento queda en `~/deploy-backups/registro_produccion/` con
uno de estos estados:

- `status=success`;
- `status=rolled_back`;
- `status=rollback_failed`.

Si aparece `rollback_failed`, no improvisar cambios sobre Nginx, `.env`, bases
o instancias vecinas. Conservar la salida y revisar el backup, el ID de imagen
y el estado del contenedor.

## Migraciones

**No aplica migraciones.** El deploy normal aborta si detecta cambios bajo
`db_migrations/` entre la revisión publicada y `origin/main`.

Una migración requiere una tarea separada con:

- revisión del SQL;
- identificación explícita de la base de `produccion_fg`;
- backup verificado;
- aprobación específica antes de modificar datos;
- validación y rollback propios.

No agregar migraciones manuales al procedimiento de esta guía.

## Diagnóstico rápido

### El frontend sigue viejo

Comparar el asset publicado con la salida del deploy:

```bash
grep -oE 'assets/index-[A-Za-z0-9_-]+\.js' \
  /var/www/html/django/produccion_fg/frontend/index.html | head -1
```

Si el servidor tiene el asset correcto, aplicar los pasos de PWA/Service
Worker del apartado anterior.

### El contenedor no queda healthy

```bash
docker inspect registro_produccion_produccion_fg \
  --format '{{.Image}}|{{.State.Status}}|{{.State.Health.Status}}'
docker logs registro_produccion_produccion_fg --tail 100
```

No mostrar ni copiar secretos de los logs.

### El preflight dice que producción no es ancestro de `main`

Existe una revisión desplegada que todavía no fue mergeada o el historial
divergió. Mergear primero el PR correcto o preparar un rollback explícito. No
forzar el deploy.

## Otros documentos

- [`docs/DEPLOY_GITHUB_MAIN_RUNBOOK.md`](docs/DEPLOY_GITHUB_MAIN_RUNBOOK.md):
  flujo multiinstancia que actualiza `indufor` y `produccion_fg`; no usar para
  el deploy normal descrito aquí.
- [`docs/DEMO_DEPLOY_RUNBOOK.md`](docs/DEMO_DEPLOY_RUNBOOK.md): entorno demo.
- `README_DEPLOY.md`: referencia histórica de la migración Docker.
