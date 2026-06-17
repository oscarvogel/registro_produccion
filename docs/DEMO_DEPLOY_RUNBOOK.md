# Runbook de despliegue demo/staging Indufor

Este runbook prepara la instancia `indufor_demo` de `registro_produccion` en `fasa_195` sin tocar las instancias productivas.

## Estado objetivo

- Host: `fasa_195` (`fg-ubuntu`)
- Repo en servidor: `/srv/apps/registro_produccion`
- Branch: `codex/docker-multi-instance-registro-produccion`
- App env: `APP_ENV=staging`
- App instance: `APP_INSTANCE=indufor_demo`
- DB esperada: `EXPECTED_DB_NAME=indufor_demo`
- Env real: `/srv/env/registro_produccion/indufor_demo.env`
- Contenedor: `registro_produccion_indufor_demo`
- Puerto host: `127.0.0.1:18104`
- Puerto interno: `8000`

## Prerrequisitos

Entrar al servidor:

```bash
ssh fasa_195
```

Validar herramientas y ruta:

```bash
hostname
docker compose version
test -d /srv/apps/registro_produccion
test -f /srv/env/registro_produccion/indufor.env
```

No modificar Nginx, dominios publicos, `indufor.env`, `produccion_fg.env` ni servicios productivos durante este procedimiento.

## Base demo recomendada

La instancia productiva de Indufor usa MySQL remoto. Para demo, la opcion mas segura es una base MySQL remota dedicada con usuario dedicado y permisos solo sobre `indufor_demo`.

Recomendacion:

- Base: `indufor_demo`
- Usuario: `indufor_demo_user`
- Host: el mismo servidor MySQL remoto que se decida usar para demo
- Permisos: solo sobre `indufor_demo.*`

No reutilizar el usuario productivo ni la DB productiva.

SQL orientativo para ejecutar solo con autorizacion explicita y credenciales administrativas seguras:

```sql
CREATE DATABASE indufor_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'indufor_demo_user'@'%' IDENTIFIED BY 'PASSWORD_SEGURO';
GRANT ALL PRIVILEGES ON indufor_demo.* TO 'indufor_demo_user'@'%';
FLUSH PRIVILEGES;
```

Alternativas si no hay permisos para crear base/usuario:

- Opcion A: crear `indufor_demo` manualmente desde el panel/hosting/VPS.
- Opcion B: pedir o crear un usuario dedicado `indufor_demo_user` limitado a `indufor_demo`.
- Opcion C: usar MySQL local en Docker solo para demo. Esta opcion aisla mas, pero agrega persistencia/backups/operacion de otro contenedor de DB.

Para este caso recomiendo MySQL remoto dedicado con usuario limitado, porque mantiene el mismo tipo de infraestructura que produccion sin exponer la base real.

## Detectar host/tipo de DB sin secretos

Usar este comando solo para ver host, base y usuario. No imprime password:

```bash
python3 - <<'PY'
from pathlib import Path
from urllib.parse import urlparse

for path in ["/srv/env/registro_produccion/indufor.env", "/var/www/html/django/indufor/backend/.env"]:
    p = Path(path)
    print("path=", path, "exists=", p.exists())
    if not p.exists():
        continue
    values = {}
    for line in p.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    url = urlparse(values.get("DATABASE_URL", ""))
    if url.scheme:
        print("scheme=", url.scheme)
        print("host=", url.hostname)
        print("port=", url.port)
        print("database=", (url.path or "").lstrip("/"))
        print("username=", url.username)
PY
```

## Crear env demo

Copiar la plantilla del repo:

```bash
cd /srv/apps/registro_produccion
mkdir -p /srv/env/registro_produccion
install -m 600 docs/examples/indufor_demo.env.example /srv/env/registro_produccion/indufor_demo.env
```

Editar solo el archivo demo:

```bash
nano /srv/env/registro_produccion/indufor_demo.env
```

Valores esperados:

```dotenv
DATABASE_URL=mysql://indufor_demo_user:CAMBIAR_PASSWORD@HOST:3306/indufor_demo
APP_NAME=registro_produccion
APP_INSTANCE=indufor_demo
APP_ENV=staging
APP_VERSION=257dc75
EXPECTED_DB_NAME=indufor_demo
ALLOW_DEMO_SEED=false
DEMO_SEED_RECORDS=200
LOG_LEVEL=info
```

Para ejecutar seed, cambiar temporalmente:

```dotenv
ALLOW_DEMO_SEED=true
```

Luego volver a:

```dotenv
ALLOW_DEMO_SEED=false
```

## Acceder a datos de conexion sin imprimir password

```bash
python3 - <<'PY'
from pathlib import Path
from sqlalchemy.engine.url import make_url

values = {}
for line in Path("/srv/env/registro_produccion/indufor_demo.env").read_text().splitlines():
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    key, value = line.split("=", 1)
    values[key.strip()] = value.strip().strip('"').strip("'")

url = make_url(values["DATABASE_URL"])
print("host=", url.host)
print("port=", url.port)
print("database=", url.database)
print("username=", url.username)
PY
```

## Deploy sin seed

```bash
cd /srv/apps/registro_produccion
scripts/deploy_indufor_demo.sh
```

Equivale a validar config, construir y levantar solamente:

```bash
docker compose -f docker-compose.yml -f docker-compose.demo.yml up -d --build indufor_demo
```

## Deploy con seed

Requiere `ALLOW_DEMO_SEED=true` en `/srv/env/registro_produccion/indufor_demo.env`.

```bash
cd /srv/apps/registro_produccion
scripts/deploy_indufor_demo.sh --seed
```

El seed ejecuta:

```bash
docker compose -f docker-compose.yml -f docker-compose.demo.yml exec -T indufor_demo python -m app.seed.demo_data
```

## Smoke tests

```bash
curl -f http://127.0.0.1:18104/health
curl -f http://127.0.0.1:18104/openapi.json
docker compose -f docker-compose.yml -f docker-compose.demo.yml ps indufor_demo
```

`/health` debe mostrar `instance=indufor_demo` y `database_name.matches=true` cuando `EXPECTED_DB_NAME=indufor_demo`.

## Verificar datos demo

Sin imprimir credenciales:

```bash
docker compose -f docker-compose.yml -f docker-compose.demo.yml exec -T indufor_demo python - <<'PY'
from sqlalchemy import text
from app.core.database import engine

with engine.connect() as conn:
    rows = conn.execute(text("""
        SELECT COUNT(*) FROM tablero_produccion
        WHERE observaciones LIKE '%DEMO_SEED%' OR operador LIKE '%Demo%'
    """)).scalar()
    print("demo_production_rows=", rows)
PY
```

## Detener demo

```bash
cd /srv/apps/registro_produccion
docker compose -f docker-compose.yml -f docker-compose.demo.yml stop indufor_demo
```

## Destruir demo solo con autorizacion expresa

Detener y remover el contenedor demo:

```bash
cd /srv/apps/registro_produccion
docker compose -f docker-compose.yml -f docker-compose.demo.yml rm -sf indufor_demo
```

Eliminar la DB `indufor_demo` solo con autorizacion explicita y despues de confirmar que no es una DB real.

## Rollback y no impacto sobre produccion

- No se modifica Nginx.
- No se cambian dominios publicos.
- No se levantan `indufor` ni `produccion_fg`.
- No se modifican `/srv/env/registro_produccion/indufor.env` ni `/srv/env/registro_produccion/produccion_fg.env`.
- El rollback operativo es detener o remover solo `indufor_demo`.
