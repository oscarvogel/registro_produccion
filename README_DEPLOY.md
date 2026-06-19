# Deploy Docker multi-instancia

Este repositorio `registro_produccion` alimenta dos instancias productivas:

- `indufor`: `produccion.indufor.com.ar`, backend Docker actual en `127.0.0.1:18004`.
- `produccion_fg`: `produccion.servinlgsm.com.ar`, backend actual en `0.0.0.0:8005`, contenedor futuro en `127.0.0.1:18005`.

`viajesfg` y `viajes_fgpy` usan otro repositorio y quedan fuera de este despliegue.

No cambiar Nginx ni detener servicios actuales hasta validar cada contenedor en paralelo.

## Instancia demo/staging

La instancia demo se documenta en `docs/DEMO_ENVIRONMENT.md` y no reemplaza a `indufor`.

Valores sugeridos:

```text
APP_INSTANCE=indufor_demo
APP_ENV=staging
DATABASE_URL=mysql://USER:PASSWORD@HOST:3306/indufor_demo
EXPECTED_DB_NAME=indufor_demo
contenedor: registro_produccion_indufor_demo
puerto: 127.0.0.1:18104
```

Compose opcional:

```bash
ssh fasa_195
cd /srv/apps/registro_produccion
docker compose -f docker-compose.yml -f docker-compose.demo.yml up -d --build indufor_demo
```

Seed de datos falsos, solo con `ALLOW_DEMO_SEED=true` en el env demo:

```bash
ssh fasa_195
cd /srv/apps/registro_produccion
docker compose -f docker-compose.yml -f docker-compose.demo.yml exec indufor_demo python -m app.seed.demo_data
```

Nunca ejecutar el seed demo contra una base real.

## Estado actual - Indufor migrado

`produccion.indufor.com.ar` ya usa Docker.

```text
contenedor: registro_produccion_indufor
puerto backend Docker: 127.0.0.1:18004
Nginx: proxy_pass http://127.0.0.1:18004;
servicio viejo: indufor_backend.service detenido, pero no eliminado
backup Nginx: /etc/nginx/sites-available/produccion.indufor.com.ar.bak-20260617-092001
```

Health interno:

```bash
curl -f http://127.0.0.1:18004/health
```

Smoke publico recomendado:

```bash
curl -f https://produccion.indufor.com.ar/api/produccion/lugares-carga
```

`/health` no esta expuesto como ruta publica directa por Nginx en el estado actual. Las rutas `/api/...` si llegan al backend Docker.

## Estructura recomendada

```text
/srv/apps/registro_produccion
/srv/env/registro_produccion/indufor.env
/srv/env/registro_produccion/produccion_fg.env
/srv/data/registro_produccion/indufor
/srv/data/registro_produccion/produccion_fg
/srv/logs/registro_produccion/indufor
/srv/logs/registro_produccion/produccion_fg
```

Los `.env` reales viven fuera del repo y no deben subirse a GitHub.

## Variables por instancia

Cada instancia usa la misma imagen Docker y se diferencia por su archivo `.env`.

```dotenv
DATABASE_URL=mysql://USER:PASSWORD@HOST:3306/DB_NAME
APP_NAME=registro_produccion
APP_INSTANCE=indufor
APP_ENV=production
APP_VERSION=unknown
EXPECTED_DB_NAME=
LOG_LEVEL=info
SECRET_KEY=change-me
ACCESS_TOKEN_EXPIRE_HOURS=8
```

Para `produccion_fg`, cambiar `APP_INSTANCE=produccion_fg` y usar su `DATABASE_URL`.

## Build

Desde `/srv/apps/registro_produccion`:

```bash
docker compose build
```

Para construir solo una instancia:

```bash
docker compose build indufor
docker compose build produccion_fg
```

## Validacion local

Sin tocar Nginx:

```bash
docker compose config
docker compose build
```

## Prueba de Indufor en paralelo

Indufor ya fue migrado a Docker. Esta seccion queda como referencia historica del procedimiento usado antes del switch.

```bash
docker compose up -d indufor
curl -f http://127.0.0.1:18004/
curl -f http://127.0.0.1:18004/docs
curl -f http://127.0.0.1:18004/openapi.json
curl -f http://127.0.0.1:18004/health
```

Comparar contra la instancia actual:

```bash
curl -f http://127.0.0.1:8004/
curl -f http://127.0.0.1:8004/openapi.json
curl -f http://127.0.0.1:18004/openapi.json
```

Para rollback, `indufor_backend.service` puede volver a iniciarse manualmente mientras exista la app vieja en disco.

## Prueba futura de produccion_fg en paralelo

No ejecutar hasta documentar el proceso actual del puerto `8005`, que corre como root con `--daemon` y sin systemd identificado.

```bash
docker compose up -d produccion_fg
curl -f http://127.0.0.1:18005/
curl -f http://127.0.0.1:18005/docs
curl -f http://127.0.0.1:18005/openapi.json
curl -f http://127.0.0.1:18005/health
```

Comparar contra la instancia actual:

```bash
curl -f http://127.0.0.1:8005/
curl -f http://127.0.0.1:8005/openapi.json
curl -f http://127.0.0.1:18005/openapi.json
```

## Cambio Nginx

No cambiar Nginx hasta que el contenedor paralelo este validado. El cambio debe ser minimo:

- Indufor: ya aplicado, `proxy_pass http://127.0.0.1:18004`.
- produccion_fg: `proxy_pass http://127.0.0.1:8005` a `proxy_pass http://127.0.0.1:18005`.

Siempre ejecutar:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

## Rollback

### Indufor

1. Restaurar la config Nginx anterior.
2. Volver `proxy_pass` a `http://127.0.0.1:8004`.
3. Ejecutar `sudo nginx -t`.
4. Recargar Nginx.
5. Iniciar `indufor_backend.service` si esta detenido.
6. Detener el contenedor si hace falta.
7. Validar `https://produccion.indufor.com.ar/`.

### produccion_fg

1. Restaurar la config Nginx anterior.
2. Volver `proxy_pass` a `http://127.0.0.1:8005`.
3. Ejecutar `sudo nginx -t`.
4. Recargar Nginx.
5. Detener el contenedor si hace falta.
6. Confirmar que el proceso viejo del puerto `8005` sigue operativo.
7. Validar `https://produccion.servinlgsm.com.ar/`.

## Pendientes antes de deploy

- Regularizar o documentar el proceso actual de `produccion_fg` en `8005`.
- Validar cada contenedor en puerto paralelo antes de tocar Nginx.
- No ejecutar migraciones sin autorizacion explicita.
