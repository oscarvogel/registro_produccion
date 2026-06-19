# Indufor Demo Deploy Result

Fecha y hora: 2026-06-17, ejecutado en `fasa_195` (`fg-ubuntu`).

## Version desplegada

- Repo: `https://github.com/oscarvogel/registro_produccion`
- PR: `oscarvogel/registro_produccion#37`
- Branch: `codex/docker-multi-instance-registro-produccion`
- Commit desplegado: `b23a057 Use explicit demo production IDs`
- Commit base del seed demo: `257dc75 Add demo environment and fake data seed`

## Instancia

- DB usada: `indufor_demo`
- Env usado: `/srv/env/registro_produccion/indufor_demo.env`
- Puerto: `127.0.0.1:18104`
- Contenedor: `registro_produccion_indufor_demo`
- Compose: `docker-compose.yml` + `docker-compose.demo.yml`

## Preparacion realizada

- Se actualizo `/srv/apps/registro_produccion` por `git pull --ff-only` en la rama demo.
- Se creo `/srv/env/registro_produccion/indufor_demo.env` con permisos `600`.
- Se valido sin imprimir secretos que `DATABASE_URL` apunta a `indufor_demo`.
- Se cargo esquema de tablas en `indufor_demo` porque la DB existia vacia.
- Se omitieron vistas del dump heredado para evitar referencias explicitas a la base real `fg`.
- Se sincronizaron columnas faltantes usadas por la app actual en `indufor_demo`.

## Compose y contenedor

- `docker compose -f docker-compose.yml -f docker-compose.demo.yml config` valido el servicio `indufor_demo`.
- Se levanto solo `indufor_demo` con:

```bash
docker compose -f docker-compose.yml -f docker-compose.demo.yml up -d --build indufor_demo
```

- Estado observado:

```text
registro_produccion_indufor_demo   Up (healthy)   127.0.0.1:18104->8000/tcp
```

## Health y endpoints

`/health` final:

```text
status= ok
service= registro_produccion
instance= indufor_demo
database= ok
database_name= {'expected': 'indufor_demo', 'actual': 'indufor_demo', 'matches': True}
```

Endpoints validados:

```bash
curl -f http://127.0.0.1:18104/health
curl -f http://127.0.0.1:18104/openapi.json
curl -f http://127.0.0.1:18104/api/produccion/lugares-carga
```

Respuesta de lugares de carga:

```json
[
  {"idLugarCarga":900001,"detalle":"Lugar Carga Demo 01"},
  {"idLugarCarga":900002,"detalle":"Lugar Carga Demo 02"},
  {"idLugarCarga":900003,"detalle":"Lugar Carga Demo 03"},
  {"idLugarCarga":900004,"detalle":"Lugar Carga Demo 04"}
]
```

## Seed

Se ejecuto:

```bash
docker compose -f docker-compose.yml -f docker-compose.demo.yml exec -T indufor_demo python -m app.seed.demo_data
```

Resultado informado por el seed:

```text
created_unidades_negocio: 1
created_tipos_proceso: 2
created_tipos_movil: 3
created_personal: 10
created_moviles: 6
created_lugares_carga: 4
created_predios: 2
created_rodales: 8
created_asignaciones: 6
created_moviles_operadores: 6
created_produccion: 200
created_cargas_combustible: 50
```

Conteos validados:

```text
database= indufor_demo
demo_production_rows= 200
demo_personal_rows= 10
demo_mobile_rows= 6
demo_loading_places= 4
```

## Confirmacion de no impacto productivo

- Nginx no fue modificado.
- `produccion.indufor.com.ar` sigue con `proxy_pass http://127.0.0.1:18004;`.
- No se levanto `produccion_fg`.
- El contenedor real `registro_produccion_indufor` siguio arriba en `127.0.0.1:18004`.
- El contenedor demo quedo separado en `127.0.0.1:18104`.
- No se modificaron `.env` productivos.
- No se ejecuto seed contra una DB distinta de `indufor_demo`.

## Detener demo

```bash
ssh fasa_195
cd /srv/apps/registro_produccion
docker compose -f docker-compose.yml -f docker-compose.demo.yml stop indufor_demo
```

## Recomendacion final

La instancia demo quedo operativa internamente en `http://127.0.0.1:18104` con datos ficticios cargados. Mantenerla sin Nginx/dominio publico hasta decidir exposicion, autenticacion y politica de acceso. Para mayor aislamiento futuro, conviene reemplazar el usuario de DB heredado por un usuario dedicado con permisos solo sobre `indufor_demo`.
