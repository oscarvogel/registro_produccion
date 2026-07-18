# Deploy desde GitHub main para produccion_fg e indufor

## Objetivo

Agregar un script Bash ejecutable en `fasa_195` que actualice
`/srv/apps/registro_produccion` desde `origin/main`, reconstruya el backend
Docker y publique la misma revisión en `indufor` y `produccion_fg`.

El despliegue no debe modificar Nginx, archivos `.env`, bases de datos ni el
servicio `indufor_demo`.

## Interfaz

El script será `scripts/deploy_main_fasa195.sh` y se ejecutará desde cualquier
directorio:

```bash
bash /srv/apps/registro_produccion/scripts/deploy_main_fasa195.sh --check
bash /srv/apps/registro_produccion/scripts/deploy_main_fasa195.sh --deploy
```

`--check` realizará todas las verificaciones que no cambian el checkout, las
imágenes ni los contenedores. `--deploy` requerirá la confirmación textual
`DEPLOY` cuando haya una terminal interactiva. Para automatización futura se
aceptará `--yes`, sin cambiar el alcance del despliegue.

## Precondiciones

El script debe abortar antes de cambiar estado cuando:

- el hostname no sea `fg-ubuntu`;
- falten `git`, `docker` o `curl`;
- el directorio de aplicación no sea
  `/srv/apps/registro_produccion`;
- el checkout tenga cambios trackeados o archivos no trackeados;
- `origin/main` no pueda obtenerse o el avance no sea fast-forward;
- falte alguno de los env files absolutos de `indufor` o `produccion_fg`;
- Docker Compose no pueda resolver la configuración;
- falte alguno de los servicios `indufor` o `produccion_fg`.

Los env files sólo se comprobarán por existencia; nunca se imprimirán.

## Flujo de despliegue

1. Adquirir un lock no bloqueante para impedir dos despliegues simultáneos.
2. Registrar el commit, la rama y el ID de imagen actualmente usados.
3. Ejecutar `git fetch --prune origin`.
4. Confirmar que el commit actual y la rama local `main` son ancestros de
   `origin/main`.
5. Cambiar a `main` y actualizar mediante
   `git merge --ff-only origin/main`. El árbol limpio y las validaciones de
   ancestro evitan descartar trabajo local.
6. Construir una imagen candidata e inspeccionarla mediante `compileall` y una
   importación de `app.main` dentro de un contenedor efímero.
7. Etiquetar la imagen candidata de forma inmutable como
   `registro_produccion:<commit-completo>` sin reemplazar todavía los
   contenedores.
8. Actualizar `indufor`, esperar que su healthcheck quede `healthy` y comprobar
   `http://127.0.0.1:18004/health`.
9. Actualizar `produccion_fg`, esperar que su healthcheck quede `healthy` y
   comprobar `http://127.0.0.1:18005/health`.
10. Etiquetar la imagen validada como `registro_produccion:latest`.
11. Mostrar commit desplegado, IDs de imagen, estado de contenedores y URLs
    comprobadas.

La actualización será secuencial para evitar bajar ambas instancias al mismo
tiempo.

## Rollback

Antes de publicar, el script guardará un manifiesto bajo
`~/.deploy-backups/registro_produccion/` con:

- commit anterior;
- rama anterior;
- imagen anterior de cada contenedor;
- fecha y commit objetivo.

Si falla la construcción o las pruebas, ningún contenedor será reemplazado. Si
falla `indufor`, se restaurará su imagen anterior y no se tocará
`produccion_fg`. Si falla `produccion_fg`, se restaurarán ambos servicios para
evitar que queden en revisiones diferentes. Después del rollback se repetirán
los dos healthchecks.

El checkout se devolverá al commit y rama anteriores únicamente cuando el
rollback de contenedores haya terminado. El manifiesto se conservará como
evidencia.

## Implementación y aislamiento

El script reutilizará `docker-compose.yml` para resolver nombres, puertos y env
files, pero utilizará una sobreescritura temporal de imagen para seleccionar la
etiqueta inmutable del commit. No editará el Compose ni los env files en el
servidor.

El lock bajo `/tmp` y el override temporal se limpiarán mediante traps. El
manifiesto se conservará como evidencia. Los errores incluirán la fase que
falló sin mostrar secretos.

## Pruebas y aceptación

Se ampliará `backend/tests/test_deploy_scripts_contract.py` con contratos que
comprueben:

- rama y remoto fijos en `main` y `origin/main`;
- rechazo de árboles sucios y avances no fast-forward;
- presencia de `--check`, `--deploy`, confirmación y lock;
- imagen etiquetada por commit;
- actualización secuencial `indufor` antes de `produccion_fg`;
- healthchecks en los puertos `18004` y `18005`;
- rollback de ambos servicios;
- ausencia de operaciones sobre Nginx, bases e `indufor_demo`.

La validación final incluirá:

```bash
pytest backend/tests/test_deploy_scripts_contract.py
bash -n scripts/deploy_main_fasa195.sh
git diff --check
```

En `fasa_195` se ejecutará primero `--check`. El despliegue real sólo avanzará
si el preflight termina correctamente. La aceptación requiere que ambos
contenedores queden `healthy`, respondan sus endpoints locales y utilicen la
misma imagen correspondiente al commit actual de `origin/main`.

## Fuera de alcance

- Migraciones o modificaciones manuales de bases.
- Cambios de Nginx, DNS, certificados o puertos.
- Despliegue del frontend fuera de lo que ya contenga la imagen backend.
- Actualización o seed de `indufor_demo`.
- Limpieza automática de imágenes Docker antiguas.
