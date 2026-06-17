# Entorno demo/staging

Esta guía describe una instancia demo separada para probar `registro_produccion` sin usar datos reales.

Advertencia: nunca ejecutar el seed demo contra una base real. El seed aborta con `APP_ENV=production`, aborta si `ALLOW_DEMO_SEED` no es `true`, y exige que `APP_INSTANCE` contenga `demo`, `test` o `staging` salvo uso explícito de `--force-instance`.

## Identidad sugerida

```dotenv
APP_NAME=registro_produccion
APP_INSTANCE=indufor_demo
APP_ENV=staging
DATABASE_URL=mysql://USER:PASSWORD@HOST:3306/indufor_demo
EXPECTED_DB_NAME=indufor_demo
ALLOW_DEMO_SEED=false
DEMO_SEED_RECORDS=200
```

Contenedor:

```text
registro_produccion_indufor_demo
```

Puerto local sugerido:

```text
127.0.0.1:18104
```

## Crear base demo

Crear una base separada, sin reutilizar bases productivas:

```sql
CREATE DATABASE indufor_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'registro_demo'@'%' IDENTIFIED BY 'CAMBIAR_PASSWORD_DEMO';
GRANT ALL PRIVILEGES ON indufor_demo.* TO 'registro_demo'@'%';
FLUSH PRIVILEGES;
```

Aplicar el esquema que corresponda al ambiente demo. No ejecutar migraciones ni cambios de esquema sobre bases productivas como parte de esta guía.

## Preparar env file

Crear `/srv/env/registro_produccion/indufor_demo.env` en el host:

```dotenv
DATABASE_URL=mysql://registro_demo:CAMBIAR_PASSWORD_DEMO@HOST:3306/indufor_demo
APP_NAME=registro_produccion
APP_INSTANCE=indufor_demo
APP_ENV=staging
APP_VERSION=unknown
EXPECTED_DB_NAME=indufor_demo
LOG_LEVEL=info
SECRET_KEY=CAMBIAR_SECRET_DEMO
ACCESS_TOKEN_EXPIRE_HOURS=8
ALLOW_DEMO_SEED=false
DEMO_SEED_RECORDS=200
```

Los `.env` reales viven fuera del repo y no deben subirse a GitHub.

## Levantar contenedor demo en fasa_195

El Docker de esta app corre en el host `fasa_195`. Entrar por SSH y trabajar desde `/srv/apps/registro_produccion`:

```bash
ssh fasa_195
cd /srv/apps/registro_produccion
```

Luego levantar la instancia demo:

```bash
docker compose -f docker-compose.yml -f docker-compose.demo.yml up -d --build indufor_demo
```

Validar:

```bash
curl -f http://127.0.0.1:18104/health
curl -f http://127.0.0.1:18104/openapi.json
```

Si `EXPECTED_DB_NAME=indufor_demo`, `/health` informa `database_name.expected`, `database_name.actual` y `database_name.matches` sin exponer credenciales ni `DATABASE_URL`.

## Ejecutar seed demo en fasa_195

Activar explícitamente el permiso solo en el env demo:

```dotenv
ALLOW_DEMO_SEED=true
```

Ejecutar dentro del contenedor:

```bash
ssh fasa_195
cd /srv/apps/registro_produccion
docker compose -f docker-compose.yml -f docker-compose.demo.yml exec indufor_demo python -m app.seed.demo_data
```

Para ver el resumen sin escribir en la base:

```bash
ssh fasa_195
cd /srv/apps/registro_produccion
docker compose -f docker-compose.yml -f docker-compose.demo.yml exec indufor_demo python -m app.seed.demo_data --dry-run
```

Para limpiar solo datos marcados como demo:

```bash
ssh fasa_195
cd /srv/apps/registro_produccion
docker compose -f docker-compose.yml -f docker-compose.demo.yml exec indufor_demo python -m app.seed.demo_data --clear-only
```

El seed elimina y recrea datos demo por nombre/marcador antes de insertar, por lo que es idempotente para la instancia demo. Los datos generados usan nombres ficticios como `Operador Demo 01`, `Movil Demo 01`, `Predio Demo Norte`, `Rodal Demo A-01` y `Lugar Carga Demo 01`.

## Datos incluidos

- Usuarios/personas ficticias: admin demo, encargado demo y operadores demo.
- Moviles ficticios.
- Lugares de carga ficticios.
- Predios y rodales ficticios.
- Tipos de proceso y tipos de movil ficticios.
- Unidad de negocio demo.
- Asignaciones operativas ficticias.
- Registros de produccion de los ultimos 60 dias.
- Cargas de combustible ficticias.

## Checklist de seguridad

- Confirmar que `APP_ENV=staging`.
- Confirmar que `APP_INSTANCE=indufor_demo`.
- Confirmar que `EXPECTED_DB_NAME=indufor_demo`.
- Confirmar que `DATABASE_URL` apunta a la base `indufor_demo`.
- Activar `ALLOW_DEMO_SEED=true` solo para ejecutar el seed y volver a `false` despues.
- No cambiar Nginx para esta instancia demo salvo decision separada.
