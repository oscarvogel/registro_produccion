# Deploy desde GitHub main

## Alcance

`scripts/deploy_main_fasa195.sh` actualiza exclusivamente los servicios Docker
`indufor` y `produccion_fg` en `fasa_195`.

El script:

- obtiene el código desde `origin/main`;
- construye una imagen inmutable etiquetada con el commit;
- actualiza primero `indufor` y después `produccion_fg`;
- comprueba el healthcheck Docker y el endpoint HTTP de cada instancia;
- ejecuta rollback automático si una instancia no queda saludable.

No modifica Nginx, archivos `.env`, bases de datos ni `indufor_demo`. Tampoco
elimina imágenes Docker anteriores.

## Requisitos

- Hostname `fg-ubuntu`.
- Checkout limpio en `/srv/apps/registro_produccion`.
- Acceso de lectura a GitHub mediante el remoto `origin`.
- Acceso del usuario a Docker.
- Env files existentes:
  - `/srv/env/registro_produccion/indufor.env`
  - `/srv/env/registro_produccion/produccion_fg.env`

El contenido de los env files nunca se imprime.

## Preflight

El preflight actualiza referencias remotas, pero no cambia rama, imágenes ni
contenedores:

```bash
cd /srv/apps/registro_produccion
bash scripts/deploy_main_fasa195.sh --check
```

El comando aborta ante archivos locales, divergencia Git, configuración Compose
inválida, servicios ausentes o env files faltantes.

## Deploy interactivo

```bash
cd /srv/apps/registro_produccion
bash scripts/deploy_main_fasa195.sh --deploy
```

Escribir `DEPLOY` cuando el script lo solicite.

## Deploy no interactivo aprobado

```bash
cd /srv/apps/registro_produccion
bash scripts/deploy_main_fasa195.sh --deploy --yes
```

`--yes` sólo debe usarse después de revisar un `--check` exitoso.

## Evidencia

Los manifiestos quedan en:

```text
~/.deploy-backups/registro_produccion/
```

Cada manifiesto registra commit y rama anteriores, imagen anterior de cada
instancia, commit objetivo y estado final. No contiene secretos.

Verificación manual:

```bash
git status -sb
git rev-parse HEAD
docker compose ps
docker inspect \
  -f '{{.Name}} {{.Image}} {{.State.Health.Status}}' \
  registro_produccion_indufor \
  registro_produccion_produccion_fg
curl -fsS http://127.0.0.1:18004/health
curl -fsS http://127.0.0.1:18005/health
```

## Rollback

El rollback es automático:

- si falla la construcción, no reemplaza contenedores;
- si falla `indufor`, restaura solamente `indufor` y no actualiza
  `produccion_fg`;
- si falla `produccion_fg`, restaura ambas instancias para que no queden en
  revisiones diferentes;
- restaura el checkout anterior y vuelve a comprobar los healthchecks.

El manifiesto se conserva con `status=rolled_back`. Si el rollback automático
también falla, no improvisar cambios sobre Nginx, `.env` o la base: inspeccionar
el manifiesto y los IDs de imagen antes de intervenir manualmente.
