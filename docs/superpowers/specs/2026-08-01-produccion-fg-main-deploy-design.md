# Diseño: deploy reproducible de `produccion_fg` desde `main`

## Objetivo

Definir un único procedimiento operativo para que una persona autorizada pueda
desplegar `produccion_fg` en `fasa_195` desde `origin/main`, con comandos
copiables, evidencia verificable y rollback automático, sin depender de
conocimiento previo de la arquitectura.

## Decisiones de alcance

- La única fuente desplegable es `origin/main`.
- La única instancia que se modifica es `produccion_fg`.
- Backend y frontend se publican como una misma revisión.
- No se modifican `indufor`, `indufor_demo`, Nginx, archivos `.env` ni bases de
  datos.
- El procedimiento no requiere `sudo`; requiere el usuario SSH autorizado con
  acceso al repositorio, Docker y al directorio del frontend.
- Las migraciones de base de datos quedan fuera del deploy normal. Si hay
  migraciones entre la revisión actualmente publicada y el objetivo, el
  preflight aborta y exige un procedimiento de migración separado.

## Enfoque elegido

Se agregará un script dedicado a `produccion_fg` y se convertirá `DEPLOY.md` en
la guía canónica. No se reutilizará el script multiinstancia como entrada
principal porque actualiza también `indufor` y no publica el frontend estático.

El flujo reutilizará el empaquetado existente para producir un artefacto con:

- aplicación backend;
- frontend compilado;
- manifiesto con rama y commit;
- ausencia verificada de archivos `.env`.

El script remoto validará el artefacto, comparará su commit con `origin/main` y
actualizará exclusivamente el contenedor y el frontend de `produccion_fg`.

La entrada remota será `scripts/deploy_produccion_fg_main_fasa195.sh`, con una
interfaz cerrada:

```bash
bash scripts/deploy_produccion_fg_main_fasa195.sh --check /ruta/al/paquete.tar.gz
bash scripts/deploy_produccion_fg_main_fasa195.sh --deploy /ruta/al/paquete.tar.gz
bash scripts/deploy_produccion_fg_main_fasa195.sh --deploy --yes /ruta/al/paquete.tar.gz
```

`--yes` sólo habilita ejecución no interactiva después de un `--check`
exitoso; no permite cambiar rama, host, servicio ni commit objetivo.

## Flujo operativo

### 1. Preparación local

La persona operadora parte de un checkout limpio en `main`, actualiza
referencias y confirma que `HEAD == origin/main`. Ejecuta las validaciones del
backend y frontend y genera el paquete con el script de build existente.

El paquete declara el commit completo en `RELEASE_MANIFEST.txt`. No se permite
usar `-AllowAnyBranch` en el procedimiento oficial.

### 2. Preflight remoto

Antes de modificar producción, el script:

1. confirma hostname `fg-ubuntu`;
2. confirma acceso a Git, Docker y `curl`;
3. confirma checkout remoto limpio;
4. ejecuta `git fetch --prune origin`;
5. confirma que el commit del paquete coincide exactamente con `origin/main`;
6. valida estructura, hash y manifiesto del paquete;
7. rechaza archivos `.env`;
8. confirma que existen el contenedor, el health interno y el frontend actual;
9. detecta cambios bajo `db_migrations/` y aborta si existen;
10. registra IDs del contenedor y de las imágenes de `indufor` e
    `indufor_demo` para comprobar que no cambian.

El modo `--check` no cambia ramas, imágenes, contenedores ni archivos
publicados.

### 3. Deploy

Con confirmación explícita, el script:

1. crea un backup en el home del usuario autorizado;
2. etiqueta la imagen activa para rollback;
3. construye una imagen inmutable etiquetada con el SHA completo objetivo;
4. valida `compileall` e importación de `app.main` dentro de la imagen;
5. recrea sólo `produccion_fg` con `--no-deps`;
6. espera estado Docker `healthy` y HTTP 200 en `127.0.0.1:18005/health`;
7. publica el frontend mediante intercambio atómico `frontend.next` →
   `frontend`, conservando `frontend.previous` durante la validación;
8. escribe el nuevo `RELEASE_MANIFEST.txt`;
9. verifica que `indufor` e `indufor_demo` mantengan sus IDs originales.

No se ejecutan migraciones ni comandos contra MySQL.

### 4. Evidencia posterior

La salida final informa:

- commit objetivo;
- ID real de la imagen activa;
- estado y health de `produccion_fg`;
- asset principal del frontend;
- ubicación del backup y manifiesto;
- confirmación de que `indufor` e `indufor_demo` no cambiaron.

Desde una máquina externa a la LAN se valida además HTTP 200 del sitio público
y que el HTML referencia el mismo asset generado por el paquete.

## Rollback

Ante cualquier fallo posterior al inicio del cambio, el script restaura:

- la imagen anterior de `produccion_fg`;
- el frontend anterior;
- el manifiesto anterior.

Después vuelve a comprobar el health interno. El manifiesto registra
`status=rolled_back` o `status=rollback_failed`. Si el rollback falla, el
script termina con error y conserva todos los artefactos para diagnóstico; no
intenta modificar Nginx, `.env`, bases ni las otras instancias.

## Documentación canónica

`DEPLOY.md` será el punto de entrada y contendrá:

- alcance y arquitectura mínima;
- requisitos de acceso y herramientas;
- checklist previa;
- comandos locales y remotos copiables;
- ejemplos de `--check` y `--deploy`;
- evidencia esperada;
- rollback y diagnóstico;
- actualización de PWA/Service Worker;
- advertencia de que `docs/DEPLOY_GITHUB_MAIN_RUNBOOK.md` corresponde al flujo
  multiinstancia y no debe usarse para desplegar sólo `produccion_fg`.

## Validación y tests

Se agregarán tests de contrato para verificar que el script:

- fija la fuente en `origin/main`;
- rechaza ramas y commits distintos;
- sólo recrea `produccion_fg` con `--no-deps`;
- no contiene comandos de Nginx, MySQL ni cambios de `.env`;
- aborta ante migraciones;
- crea backup y rollback de imagen, frontend y manifiesto;
- comprueba invariantes de `indufor` e `indufor_demo`;
- produce evidencia del commit, imagen, health, asset y backup.

Validaciones finales mínimas:

```text
git diff --check
tests de contrato del deploy
python -m compileall backend/app
npm test
npm run build
bash -n del script en fasa_195
ejecución de --check en fasa_195
```

La implementación termina en un PR draft separado del fix funcional #109.
