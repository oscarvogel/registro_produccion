# Plan de implementación — Evidencia de horas y producción

> **Estado:** plan propuesto, pendiente de aprobación.
> **Fecha:** 2026-10-24
> **Rama base:** `main`
> **Alcance:** registro de evidencia fotográfica obligatoria (foto del horómetro y foto de la
> pantalla del procesador), con verificación posterior por el encargado, carga posible sin
> conexión y almacenamiento en disco del servidor con volumen Docker persistente.

---

## 1. Objetivo

Hoy el operador declara las horas y la producción **de memoria**: escribe el horómetro inicial y
final, y los m³ o las plantas, y nada en el sistema deja constancia de que ese número salió de la
máquina. El plan agrega un **registro de evidencia**:

1. **Fotos obligatorias cuando aplican.** Foto del **horómetro** para los procesos que usan
   horómetro; foto de la **pantalla del procesador** para los procesos que reportan **m³** o
   **plantas**. En `PROCESO` hacen falta las dos, salvo que el horómetro figure en esa misma
   pantalla: lo declara el operador y lo contrasta el encargado al verificar.
2. **Verificables.** La foto queda *pendiente de verificación* y un **encargado o admin** la
   marca como *verificada* o *rechazada* desde el detalle del registro, dejando quién y cuándo.
3. **Robusto sin señal.** La foto se puede tomar y adjuntar en el campo sin cobertura: queda
   encolada en el teléfono y se sube al reconectar, junto con el registro.
4. **Con piso de calidad.** La **hora fin (`hr_fin`) es obligatoria** en los procesos que usan
   horómetro, como mínimo exigido para dar de alta un registro.

---

## 2. Decisiones tomadas

| # | Decisión | Elección | Consecuencia técnica |
|---|---|---|---|
| D1 | Qué significa "se pueda marcarlo" | **Verificación posterior por el encargado** | La evidencia nace `pendiente`; un `encargado`/`admin` la marca `verificada` o `rechazada`. Agrega estado, actor y fecha de verificación. |
| D2 | Dónde se guardan las fotos | **Disco del servidor + volumen Docker** | Requiere volumen nombrado en `docker-compose.yml`, endpoint FastAPI que sirve los bytes, y ajuste de `client_max_body_size` en nginx. Las fotos **no** entran en el backup de MySQL. |
| D3 | Carga sin conexión | **Sí, encolada en el teléfono** | Nuevo store Dexie para blobs; el sync sube **evidencia primero, registro después**. |
| D4 | Qué procesos exigen evidencia | **Configurable por tipo de proceso en Admin** | Dos flags nuevos en `tipo_de_proceso`, editables junto a `requiere_acta`/`predio`/`rodal`. Sin heurísticas. |
| D5 | Alcance de `hr_fin` obligatorio | **Sólo en los tipos de proceso que usan horómetro** | `hr_fin` obligatoria y `> hr_inicio` en `HORAS MAQUINAS`. Los procesos sin horómetro no la exigen. |
| D6 | Cuántas fotos del horómetro | **Una, tomada al final del trabajo** | Documenta la lectura final (`hr_fin`). No se pide foto de `hr_inicio`. |
| D7 | Cómo se detecta que el horómetro figura en la pantalla del procesador | **Declaración del operador**, verificada por el encargado | Una casilla que el operador tilda al subir la foto del procesador. La afirmación queda guardada con la evidencia y el encargado la contrasta mirando la foto al verificar. |
| D8 | Configuración inicial de la foto de horómetro | **`HORAS MAQUINAS` + `PROCESO`** | `PROCESO` exige las dos fotos (pantalla + horómetro) salvo que el horómetro esté en esa pantalla. `VOLTEO` sólo la de pantalla. |

---

## 3. Relevamiento del estado actual

Verificado sobre el repo y sobre la base real (`registro_demo` en el MariaDB de WSL).

### 3.1 Catálogo real de `tipo_de_proceso`

| id | nombre | `campos` | Evidencia a activar |
|---|---|---|---|
| 1 | CARGA | `tn_despachadas` | — |
| 2 | EXTRACCION | `carros,distancia_recorrida` | — |
| 3 | **PROCESO** | **`m3,plantas`** | **foto del procesador** |
| 4 | **VOLTEO** | **`plantas`** | **foto del procesador** |
| 5 | **HORAS MAQUINAS** | **`hora_inicio,hora_fin`** | **foto del horómetro** |
| 6–13 | DESPEJE…CHIPEADO SOBRE CAMION | `has` / `km` / `tn_despachadas` | — |
| 14 | DISPOSICION | `hr_disposicion` | — |
| 15 | REMOLQUE | `hr_remolque` | — |

`campos` (CSV) es lo que hoy decide qué campos de producción se pintan. `PROCESO` ya tiene su
propio bloque extra en el formulario (Sistema de Corte: `pies_16/14/12/10`, `pulpable`).

### 3.2 Backend

- FastAPI + gunicorn (3 workers uvicorn). Modelos en `backend/app/models/`, esquemas en
  `backend/app/schemas/`, rutas en `backend/app/api/routes/`.
- `tablero_produccion` es la tabla de producción: **sin auto_increment** (ID = `MAX(id)+1`),
  protegida por un lock nombrado de MySQL (`registro_produccion:create`).
- Idempotencia de alta: par `form_uuid` + `cod_operador`.
- `python-multipart==0.0.6` **ya está** en `requirements.txt`: el multipart no cuesta nada.
- **No existe ningún endpoint de archivos** en el proyecto. `grep` de `UploadFile|File(|StaticFiles`
  en `backend/` no devuelve nada. Esto es enteramente nuevo.
- Roles disponibles en `personal`: `encargado`, `is_admin`. Ya existe la dependencia
  `get_current_admin_or_encargado` en `backend/app/api/deps.py`.

### 3.3 Frontend

- Vue 3 + Pinia + Vite + Tailwind. `ProduccionFormView.vue` deriva a `CaminosFormView.vue`
  (UN Caminos) o `ProduccionLegacyFormView.vue` (1780 líneas, todo lo demás).
- Wizard de 9 pasos. `frontend/src/services/tipoProcesoRules.js` ya expone
  `productionSteps(processType)`, que **omite** el paso "Tiempo" cuando el proceso no usa
  horómetro. Los pasos ya son condicionales: agregar el paso "Evidencia" es sumar una
  entrada al filtro, no reindexar el wizard.
- `puedeAvanzar` es un `switch` por índice de paso: es donde va la puerta de evidencia.
- Cola offline: Dexie `produccion_offline`, store `pendingRecords` (`db.js` está en **v3**).
- Admin CRUD: `AdminCrudView.vue` con `ENTITY_DEFINITIONS`; `tipos-proceso` ya tiene una sección
  `requisitos` con los tres checkboxes `requiere_*`. Las entidades pueden definir un
  `decorate(row)` para derivar columnas sin tocar `DataTable`.
- Detalle de registro: `RecordDetailModal.vue`, agrupado en secciones, con
  `dashboardRegistros.js` como store.

### 3.4 Infra y despliegue

- `docker-compose.yml`: los servicios `produccion_fg` e `indufor` montan **solo** secretos
  `.env` y el CA de MySQL, en modo `ro`. **No hay volumen de datos de aplicación.**
- El deploy recrea el contenedor con
  `docker compose up -d --no-build --no-deps --force-recreate produccion_fg` → **un volumen
  nombrado sobrevive el recreate**; un bind mount de un path del host también.
- **Las migraciones se aplican solas** al arrancar el contenedor (`RUN_MIGRATIONS=1` +
  `backend/app/migrate.py`). El deploy real es Coolify en `fasa_189`. El script
  `scripts/deploy_produccion_fg_main_fasa195.sh` es un camino legacy que todavía aborta si
  cambian los `db_migrations`: **no es el deploy en uso**.
- nginx (`frontend/nginx.conf.template`) proxea `location /api/` al backend. El `client_max_body_size`
  por defecto (**1 MB**) rechazaría las fotos con 413: hay que tocarlo.
- `produccion_fg` e `indufor` **comparten la base `fg`** y se despliegan juntas desde el mismo
  compose → el volumen de evidencia tiene que ser **uno solo**, montado en los dos servicios.

### 3.5 Base real

`192.168.0.189/fg` (usuario `central_admin`) **no está alcanzable** desde este puesto en este
momento (timeout). La copia de trabajo `registro_demo` en el MariaDB de WSL sí lo está y tiene
el esquema real de la app.

### 3.6 Re-baselining contra `origin/main` (24/10/2026)

Al arrancar el issue 1, `origin/main` estaba **17 commits adelante** de la rama de trabajo. Tres
cambios invalidan partes de este plan:

**a) `requiere_horometro` ya existe.** Lo agregó el commit `b193d40` (16/10) para los procesos
sin horómetro (la camioneta). **No** es el flag de evidencia: define si el parte pide horómetro
inicial/final, es decir si el wizard muestra el paso "Control de Tiempo". Está en `1` en los 15
procesos del catálogo real, así que **no se puede derivar de él** la exigencia de foto: harían
falta dos flags distintos, como estaba previsto.

**b) Las migraciones se aplican solas.** `backend/app/migrate.py` corre **todos** los `.sql` de
`db_migrations/` al arrancar el contenedor (`RUN_MIGRATIONS=1` en el compose). El deploy real es
Coolify en `fasa_189`; el `Pre-deployment Command` no sirve con el build pack `dockercompose`.

> **Consecuencia directa sobre el seed:** el runner **no registra** qué migraciones aplicó, así
> que **todos los `.sql` se re-aplican en cada deploy**. Un `UPDATE` de configuración inicial sin
> filtro volvería a pisar, en cada deploy, lo que el administrador ajustó en Admin. Por eso los
> flags usan **NULL como centinela de "sin configurar"** y el seed solo toca filas con el flag en
> NULL. Verificado contra MySQL real: con el admin simulating un cambio, el re-run **no** lo
> revierte.

**c) El wizard ya tiene pasos condicionales.** `frontend/src/services/tipoProcesoRules.js`
expone `productionSteps(processType)`, que saca el paso "Tiempo" cuando el proceso no usa
horómetro. Agregar el paso "Evidencia" es **agregar una entrada al filtro**, no reindexar el
wizard entero. El riesgo R-1 queda desactualizado.

**d) Las dos instancias comparten la base y se despliegan juntas.** `produccion_fg` (Servinlgsm) e
`indufor` salen del mismo `docker-compose.yml` y apuntan a la misma base `fg`. **El volumen de
evidencia tiene que ser el mismo para las dos**, montado en ambos servicios: con volúmenes
separados, una foto subida por una instancia daría 404 en la otra.

---

## 4. Diseño

### 4.1 Modelo de datos

**Migración:** `db_migrations/20261024_evidencia_produccion.sql` (issue #194)

```sql
-- 1. Flags de exigencia por tipo de proceso
--    NULL = "sin configurar". La API lo expone como False (no exige evidencia).
--    El centinela NULL es lo que permite que el seed de mas abajo no pise
--    la configuracion que el admin cambie (ver 3.6 b).
ALTER TABLE tipo_de_proceso
  ADD COLUMN requiere_foto_horometro  TINYINT(1) NULL DEFAULT NULL,
  ADD COLUMN requiere_foto_procesador TINYINT(1) NULL DEFAULT NULL;

-- 2. Tabla de evidencia
CREATE TABLE IF NOT EXISTS produccion_evidencia (
  id            INT NOT NULL AUTO_INCREMENT,
  registro_id   INT NULL,                    -- tablero_produccion.id; NULL hasta vincular
  form_uuid     VARCHAR(36) NOT NULL,        -- vinculo estable, sobrevive al modo offline
  tipo          VARCHAR(20) NOT NULL,        -- 'procesador' | 'horometro'
  incluye_horometro TINYINT(1) NOT NULL DEFAULT 0, -- la foto del procesador tambien muestra el horometro
  archivo       VARCHAR(255) NOT NULL,       -- ruta RELATIVA dentro del volumen
  mime          VARCHAR(100) NOT NULL DEFAULT '',
  tamano        INT NOT NULL DEFAULT 0,
  hash_sha256   VARCHAR(64) NOT NULL DEFAULT '',
  estado        SMALLINT NOT NULL DEFAULT 0,-- 0 pendiente, 1 verificada, 2 rechazada
  cargado_por   VARCHAR(80) NOT NULL DEFAULT '',
  verificado_por VARCHAR(80) NOT NULL DEFAULT '',
  verificado_at DATETIME NULL,
  comentario    VARCHAR(255) NOT NULL DEFAULT '',
  created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_evidencia_form_tipo (form_uuid, tipo),
  KEY idx_evidencia_registro (registro_id)
);

-- 3. Configuracion inicial coherente con el pedido (D8)
--    Solo toca filas con el flag en NULL: un deploy posterior no pisa lo
--    que el admin haya cambiado.
UPDATE tipo_de_proceso SET requiere_foto_horometro = 1
  WHERE UPPER(TRIM(nombre)) IN ('HORAS MAQUINAS', 'PROCESO')
    AND requiere_foto_horometro IS NULL;
UPDATE tipo_de_proceso SET requiere_foto_procesador = 1
  WHERE UPPER(TRIM(nombre)) IN ('PROCESO', 'VOLTEO')
    AND requiere_foto_procesador IS NULL;
```

> El `ALTER` real va guardado con `information_schema` + `PREPARE`/`EXECUTE`, como el de
> `20261016_tipo_proceso_requiere_horometro.sql`: el runner aplica todos los `.sql` en cada
> deploy, así que agregar la columna tiene que ser idempotente.

**Por qué `form_uuid` y no `registro_id` como clave:** en modo offline la foto se toma *antes*
de que exista la fila de producción, y el `form_uuid` es el único identificador estable que
viaja del teléfono al servidor. El `UNIQUE KEY (form_uuid, tipo)` además da idempotencia:
re-subir la misma foto no duplica.

**Por qué un archivo y no un BLOB:** decisión D2. El tradeoff explícito es que **las fotos no
entran en el backup de MySQL** — hay que sumar el volumen al procedimiento de backup y documentarlo.

**Por qué `incluye_horometro` y no una tabla de roles:** la evidencia cubre **roles**, no tipos.
Una foto de la pantalla del procesador puede documentar **dos** cosas a la vez: las plantas/m³ y
el horómetro, cuando el operador declara que el horómetro aparece en esa misma pantalla (D7).
En vez de una tabla `produccion_evidencia_rol` con dos filas por foto, alcanza con un booleano
en la misma fila:

| `tipo` | `incluye_horometro` | Roles que cubre la foto |
|---|---|---|
| `procesador` | `0` | `{procesador}` |
| `procesador` | `1` | `{procesador, horometro}` |
| `horometro` | `0` | `{horometro}` |

La cobertura se resuelve en una función de Python (`core/evidencia.py`), no en SQL, así que un
CSV o un booleano alcanzan y no hace falta normalizar. El `UNIQUE (form_uuid, tipo)` sigue
sirviendo: como máximo una foto de procesador y una de horómetro por registro.

### 4.2 Reglas de aplicabilidad

Las reglas viven en el **backend** (`backend/app/core/evidencia.py`), no en la pantalla.

| Regla | Contenido |
|---|---|
| **R1 — qué se exige** | El `tipo_de_proceso` del registro define los **roles** de evidencia obligatorios: `requiere_foto_horometro` → rol `horometro`; `requiere_foto_procesador` → rol `procesador`. |
| **R2 — obligatoriedad** | Al crear el registro, si el tipo de proceso exige un rol y no hay una evidencia **no rechazada** que lo cubra (ver R7), la API responde **422** con un mensaje que nombra la foto faltante. |
| **R3 — hora fin obligatoria** | `hr_fin` es obligatoria y `> 0` en todo tipo de proceso cuyo `campos` incluya `hora_inicio`/`hora_fin` (hoy: `HORAS MAQUINAS`). Además `hr_fin > hr_inicio`. **Alcance confirmado: sólo los tipos de proceso que usan horómetro** (ver D-A). |
| **R4 — sin evidencia para el resto** | Los tipos de proceso sin flags no piden foto: el formulario no muestra el paso y la API no exige nada. |
| **R5 — verificación** | Sólo `encargado` o `is_admin` puede pasar `pendiente → verificada/rechazada`. Un rechazo **no borra** la foto: queda el registro del intento y el registro de producción queda *observado*. |

| **R6 — la foto del horómetro es la lectura final** | **Una sola** foto del horómetro, tomada **al final del trabajo**: documenta la lectura final (`hr_fin`), que es justamente el dato que R3 vuelve obligatorio. El rótulo del campo es *"Foto del horómetro (lectura final)"* y la foto **no** habilita el paso si `hr_fin` viene vacía. No se pide foto de `hr_inicio`. |
| **R7 — cobertura por roles** | La evidencia cubre **roles**: `procesador` y `horometro`. Una foto cubre `procesador` si `tipo='procesador'`; cubre `horometro` si `tipo='horometro'` **o** si `tipo='procesador' AND incluye_horometro=1` (el operador declaró que el horómetro se ve en esa pantalla — D7). Un rol está cubierto si hay **alguna** evidencia **no rechazada** vinculada al registro que lo cubra. |
| **R8 — declaración auditable** | La declaración "el horómetro figura en esta pantalla" viaja con la evidencia (`incluye_horometro=1`) y se muestra al encargado **junto a la foto** en la pantalla de verificación. No es una casilla que se pierde: queda en el registro de auditoría. Si el encargado no ve el horómetro en la imagen, rechaza la foto (R5). |
| **R9 — declaración por defecto desactivada** | La casilla arranca **sin tildar**. Si el operador no está seguro, tiene que subir la segunda foto: el costo de la duda es una foto extra, mientras que el costo de una declaración falsa es un registro observado. |

**Ejemplo de resolución (PROCESO):**

| Evidencia subida | `incluye_horometro` | Rol `procesador` | Rol `horometro` | ¿Válido? |
|---|---|---|---|---|
| Sólo foto de pantalla, horómetro **no** visible | `0` | cubierto | **no cubierto** | ❌ falta la foto del horómetro (R7) |
| Sólo foto de pantalla, horómetro **visible** | `1` | cubierto | cubierto | ✅ |
| Foto de pantalla + foto del horómetro | `0` | cubierto | cubierto | ✅ |

### 4.3 API

Todo en `backend/app/api/routes/evidencia.py` (router nuevo, registrado en `app/main.py`).

| Método | Ruta | Quién | Qué hace |
|---|---|---|---|
| `POST` | `/api/produccion/evidencias` | operador | **multipart**: `form_uuid`, `tipo`, `archivo`, `incluye_horometro` (bool, por defecto `false`). Valida mime/tamaño, escribe el archivo, crea la fila `estado=0`. Devuelve `{id, form_uuid, tipo, incluye_horometro, estado, url}`. Idempotente por `(form_uuid, tipo)`. |
| `GET` | `/api/produccion/evidencias/{id}/archivo` | autenticado | Devuelve los bytes (`FileResponse`) con el mime real. |
| `GET` | `/api/produccion/{registro_id}/evidencias` | autenticado | Lista la evidencia del registro con estado y metadatos. |
| `PATCH` | `/api/produccion/evidencias/{id}` | **encargado/admin** | `{estado, comentario}` → marca verificada/rechazada. |

Cambios en el flujo existente:

- `TableroProduccionCreate` gana `evidencias: list[int] = []`.
- `POST /api/produccion/` vincula esos ids al registro (`registro_id`), y aplica **R2**:
  si falta evidencia obligatoria → **422** con detalle claro.
- La comprobación de R2 se hace **por roles** (R7), no por `tipo`: se calcula el conjunto de roles
  exigidos por el `tipo_de_proceso` del registro y se verifica que cada rol esté cubierto por
  alguna evidencia vinculada y **no rechazada**. Un mensaje de error explícito, por ejemplo:
  *"PROCESO: falta la foto del horómetro (o marcar que el horómetro se ve en la pantalla del procesador)"*.
- El alta sigue siendo idempotente por `form_uuid` + `cod_operador`: si el registro ya existe,
  se devuelve el existente y **no** se vuelve a validar la evidencia.

**Manejo de archivos (reglas duras):**

- La extensión sale del **mime validado**, nunca del nombre que manda el cliente (evita path
  traversal y falsificación de tipo).
- Mimes aceptados: `image/jpeg`, `image/png`, `image/webp`, `image/heic`.
- Tamaño máximo: 10 MB (`EVIDENCIA_MAX_UPLOAD_MB`, configurable).
- Se escribe con nombre temporal + `os.replace` (rename atómico) para que no queden archivos
  a medio escribir.
- Ruta: `<EVIDENCIA_STORAGE_DIR>/<YYYY>/<MM>/<form_uuid>_<tipo>_<hash8>.<ext>` — shardeado por
  mes para no crear un directorio con 100.000 archivos.

### 4.4 Almacenamiento en disco + volumen Docker

**Backend:**
- Nueva setting en `backend/app/core/config.py`: `EVIDENCIA_STORAGE_DIR: str = "/app/media/evidencias"`,
  `EVIDENCIA_MAX_UPLOAD_MB: int = 10`.
- El backend crea el directorio si no existe (con `mkdir -p`).

**Docker** (implementado en el issue #196):
```yaml
services:
  produccion_fg:
    volumes:
      - /srv/env/registro_produccion/produccion_fg.env:/run/secrets/registro.env:ro
      - /srv/env/registro_produccion/mysql-central-ca.pem:/run/secrets/mysql-central-ca.pem:ro
      - evidencia:/app/media          # <-- NUEVO: volumen nombrado
  indufor:
    volumes:
      ...
      - evidencia:/app/media          # <-- el MISMO volumen
volumes:
  evidencia:
    name: registro_produccion_evidencia   # <-- nombre explicito
```

Un **volumen nombrado** es lo correcto acá: sobrevive al `--force-recreate` del deploy, no depende
de que el path del host exista, y no se monta en `ro`. El nombre es explícito para que no dependa
del nombre del proyecto de compose.

> **Un SOLO volumen para las dos instancias.** `produccion_fg` e `indufor` comparten la base `fg`:
> con volúmenes separados, una foto subida por Servinlgsm daría **404** en Indufor. Es el riesgo
> R-11 del plan, y el motivo de que el volumen esté declarado una sola vez.

**nginx** (`frontend/nginx.conf.template`), en el bloque `location /api/`:
```nginx
client_max_body_size 12m;   # default es 1m -> las fotos darian 413
```
El proxy ya cubre `/api/`, así que las fotos se sirven sin tocar traefik. El límite de nginx
(12m) va **por encima** del tope del backend (10 MB) para que el multipart con sus campos quepa
entero.

**Migraciones:** se aplican **solas** al arrancar el contenedor (ver 3.6 b). No hay que hacer
nada a mano antes de desplegar.

**Higiene operativa (importante):** como las fotos viven fuera de MySQL, el backup de la base
**no las incluye**. Hay que (a) sumar el volumen al procedimiento de backup y (b) barrer los
archivos huérfanos: evidencia cuyo `form_uuid` no corresponde a ningún registro y que tiene más
de N días.

El barrido es `backend/scripts/purge_evidencia_huerfana.py` (implementado en el issue #196):

```bash
# informa (default)
python scripts/purge_evidencia_huerfana.py
# borra de verdad
python scripts/purge_evidencia_huerfana.py --si
# con mas margen
python scripts/purge_evidencia_huerfana.py --dias 30
```

Borra dos cosas: las **filas de evidencia** cuyo parte no existe (y su archivo) y los
**archivos en disco sin fila** (escrituras a medias). Tiene guarda de edad (7 días por
defecto) para no tocar una foto que todavía está encolada en un teléfono sin conexión, y
sin `--si` **sólo informa**. Dentro del contenedor:

```bash
docker compose exec produccion_fg python scripts/purge_evidencia_huerfana.py --si
```

### 4.5 Frontend

**Componente nuevo** — `frontend/src/components/produccion/EvidenciaField.vue`:
- `<input type="file" accept="image/*" capture="environment">`: en el teléfono abre **directamente
  la cámara** (es el caso de uso real: fotografiar el horómetro en la máquina).
- Preview en miniatura, botón *rehacer* y *quitar*.
- **Compresión en el navegador antes de subir**: canvas → lado mayor 1600 px, JPEG quality 0.8.
  Deja las fotos en 200–500 KB, que es lo que hace viable subirlas con señal floja.
- **Rótulos según el tipo de evidencia** (D-B cerrado):
  - `horometro` → *"Foto del horómetro (lectura final)"*. Se toma **al final del trabajo** y
    documenta `hr_fin`. Debajo del campo se muestra el `hr_fin` cargado, para que el operador
    verifique en el momento que la foto y el número coinciden.
  - `procesador` → *"Foto de la pantalla del procesador"*, con la aclaración de que debe legible
    el valor de **m³** y/o **plantas** que se está declarando.

**El caso de PROCESO: dos fotos o una (D7).** Cuando el proceso exige **los dos roles**
(`PROCESO` en la configuración inicial), el paso de evidencia queda así:

```
┌─ Evidencia ────────────────────────────────────────────────┐
│                                                              │
│  Foto de la pantalla del procesador        [ 📷 Tomar foto ] │
│  ┌──────────────┐                                          │
│  │  (miniatura) │  Debe legible plantas y/o m³.             │
│  └──────────────┘                                          │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ ☐  El horómetro se ve en esta misma pantalla          │    │
│  └──────────────────────────────────────────────────────┘    │
│  Si lo tildás, esta foto también sirve como evidencia       │
│  del horómetro y no hace falta otra foto.                   │
│                                                              │
│  ── (sólo si NO está tildado) ───────────────────────────    │
│  Foto del horómetro (lectura final)      [ 📷 Tomar foto ] │
│  Horómetro final declarado: 1850.5 h                       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

- La casilla arranca **sin tildar** (R9).
- Al tildarla, el campo *"Foto del horómetro"* **desaparece** y el paso queda con una sola foto.
- Al destildarla, el campo **aparece** y pasa a ser obligatorio.
- Al enviar, la foto del procesador se sube con `incluye_horometro=1` si la casilla está tildada.
- El texto de ayuda es explícito para que el operador no la tilde "a ojo": la casilla no es una
  opinión sobre la máquina, es una declaración sobre **la foto que está subiendo**.

**Paso nuevo en el wizard.** `pasos` pasa a `computed` para poder intercalar un paso condicional:

```js
const pasos = computed(() => {
  const base = ['Contexto', 'Operador', 'Equipo', 'Proceso', 'Tiempo', 'Producción']
  if (tiposEvidenciaRequeridos.value.length) base.push('Evidencia')
  return [...base, 'Consumos', 'Ubicación', 'Revisión']
})
```
Esto obliga a **reindexar** los `case` de `puedeAvanzar` y los `v-show="pasoActual === N"`.
Como el paso depende del tipo de proceso elegido en el paso 3, hay que revisar que al **volver
atrás** y cambiar el tipo de proceso el paso se recalcule sin desalinear el índice.

> Alternativa de menor riesgo para la primera entrega: **no** agregar un paso y pintar la evidencia
> dentro de la tarjeta "Datos de Producción" (paso 5) y de "Control de Tiempo" (paso 4). Evita
> reindexar el wizard, pero mezcla la evidencia con los datos. **Recomendación:** paso propio,
> porque el cambio de tipo de proceso es el caso de uso normal y un paso dedicado lo hace visible.

**Puertas de validación:**
- `puedeAvanzar` en el paso de evidencia: no se avanza sin la foto que el tipo de proceso exige.
- El bloque de *Revisión* (paso final) muestra un resumen de la evidencia adjunta.

**Envío online:** se subir **primero** las fotos (`POST /api/produccion/evidencias`), se
obtienen los ids, y luego se manda el registro con `evidencias: [ids]`.

**Carga de imágenes con autenticación:** las fotos **no** se pintan con `<img src="/api/...">`,
porque el navegador no puede mandar el header `Authorization` en una request de imagen. Se
descargan con axios (`responseType: 'blob'`) y se pintan con `URL.createObjectURL`. Evita además
filtrar el token en la URL (queda en los access logs).

**Estado de verificación en el detalle:** `RecordDetailModal.vue` gana una sección
"Evidencia" con las miniaturas, el tipo, el estado y quién verificó.

**Modo offline (D3):**
- `db.js` sube a **v4** con un store nuevo `pendingEvidencias: '++id, formUuid, tipo, synced'`
  que guarda el `Blob` + metadatos (no base64: menos memoria y menos copia).
- `queuePendingProductionRecord` se acompaaña de `queuePendingEvidencia`.
- El **orden de sync es la regla clave**: primero se sube la evidencia, después el registro.
  Si la evidencia no sube, el registro **no** se envía — así nunca queda un registro sin la foto
  que el tipo de proceso exige (regla R2). `syncPending` en `produccionLegacy.js` ya itera los
  pendientes: hay que processar primero los `pendingEvidencias` de cada `form_uuid`.
- `PendientesView.vue` (la pantalla de pendientes) debe mostrar el estado de cada foto: *"foto
  adjunta, esperando subir"* / *"subida"*.

**Filtro de verificación:** `DashboardRegistrosView.vue` (ruta `/dashboard/registros`, ya
restringida a `encargado`/`admin` por `meta.requiresEncargado`) gana un filtro
*"evidencia pendiente de verificación"*. Es el lugar natural para que el encargado entre a
verificar: **no se crea una pantalla nueva**.

### 4.6 Verificación por el encargado (D1)

- Backend: `PATCH /api/produccion/evidencias/{id}` con `get_current_admin_or_encargado`.
- Estados: `0 pendiente` → `1 verificada` | `2 rechazada`.
- Se guarda `verificado_por`, `verificado_at` y `comentario` (motivo del rechazo).
- Frontend: en `RecordDetailModal.vue`, los botones *Verificar* / *Rechazar* sólo aparecen si
  `authStore.user.encargado === 1 || authStore.user.is_admin === 1`.
- Un registro con evidencia rechazada queda **observado** en el listado del dashboard.

**El paso de verificación es donde se controla la declaración (D7 + R8).** En la tarjeta de
evidencia del detalle del registro, sobre cada foto de tipo `procesador` con
`incluye_horometro = 1`, se muestra un aviso junto a la miniatura:

> *"El operador declaró que el horómetro se ve en esta pantalla."*

El encargado tiene la foto delante: **comprueba con sus propios ojos** que el horómetro esté
visible. Si no lo está, rechaza la foto con el motivo *"el horómetro no se ve en la pantalla"* y
el registro queda observado. Así la declaración no es una casilla en la que hay que confiar: es
una afirmación que el flujo de verificación ya permite contrastar.

Por eso D7 no necesita OCR ni configuración por máquina: la detección la hace **la persona que
está en la máquina** al declarar, y la **persona que revisa** al verificar.

### 4.7 Configuración en Admin (D4)

- `backend/app/schemas/admin.py`: `TipoProcesoCreate` / `TipoProcesoUpdate` /
  `TipoProcesoResponse` ganan los dos flags.
- `backend/app/models/tipo_proceso.py`: dos columnas nuevas.
- `backend/app/api/routes/admin_legacy.py`: `_to_tipo_proceso_response` y el create/update.
- `frontend/src/views/admin/AdminCrudView.vue`: dos checkboxes nuevos en la sección `requisitos`
  de `tipos-proceso`, más **una** columna "Evidencia" en la grilla que resume los dos flags
  (`Ambas` / `Horómetro` / `Procesador` / `—`). El resumen se calcula con un hook `decorate`
  por entidad, sin tocar el contrato de `DataTable`.
  > **Una sola columna, no dos:** la grilla de tipos de proceso entra *justa* en 1366px
  > (0px de margen). Con dos columnas el desborde llegaba a **208px** y la columna de
  > acciones quedaba fuera de pantalla. Con una, el desborde es de **37px**, y a 1638x969
  > (la del cliente) es **0px**. Medido con `frontend/scripts/evidenciaAdminCapture.mjs`.
  > Ver `docs/EVIDENCIA_ADMIN_VISUAL_REVIEW.md`.
- `frontend/src/views/ProduccionLegacyFormView.vue`: el formulario de producción lee los flags
  desde `tipoProcesoSeleccionado` (ya disponible vía `store.tiposProceso`).

---

## 5. Plan de trabajo

Un issue, una rama, un PR. Todos desde `main`, todos en draft primero.

| # | Issue | Rama | Alcance | Depende de |
|---|---|---|---|---|
| **1** | **#194** — Esquema + flags de tipo de proceso | `codex/issue-194-esquema-evidencia` | Migración SQL (tabla `produccion_evidencia` + flags + seed D8), modelo, schemas, `admin_legacy.py`, checkboxes en Admin | — |
| **2** | **#196** — Infra: volumen + nginx | `codex/issue-196-infra-evidencia` | `docker-compose.yml` (**un** volumen para las dos instancias), `nginx.conf.template` (`client_max_body_size`), `config.py` (settings), `backend/scripts/purge_evidencia_huerfana.py` | — |
| **3** | **#198** — API de evidencia | `codex/issue-198-api-evidencia` | `routes/evidencia.py`, `core/evidencia.py` (reglas R1–R9, cobertura por roles), upload/link/serve/verify, validación R2 en el alta, tests | 1, 2 |
| **4** | Captura y envío en el formulario | `codex/issue-NN-frontend-evidencia` | `EvidenciaField.vue`, paso condicional en `tipoProcesoRules.js`, casilla *"el horómetro se ve en esta pantalla"*, compresión, gates de `puedeAvanzar`, resumen en Revisión, tests | 3 |
| **5** | Modo offline | `codex/issue-NN-offline-evidencia` | `db.js` v4, store `pendingEvidencias`, orden de sync (evidencia → registro), `PendientesView.vue` | 4 |
| **6** | Verificación por el encargado | `codex/issue-NN-verificacion-evidencia` | Sección Evidencia en `RecordDetailModal.vue` (con el aviso de la declaración), botones Verificar/Rechazar, filtro en `DashboardRegistrosView.vue` | 4 |
| **7** | Documentación y despliegue | `codex/issue-NN-docs-evidencia` | Manuales de operador/encargado, procedimiento de backup del volumen, evidencia visual | 3–6 |

**Notas de secuencia:**

- La migración del **issue 1** se aplica **sola** al arrancar el contenedor (R-5 desactualizado).
  No hay que hacer nada a mano antes de desplegar.
- El **issue 2** es independiente y se puede abrir en paralelo; si se quiere minimizar el riesgo de
  regresión, se despliega primero.
- Los issues 5 y 6 se pueden hacer en paralelo entre sí (archivos distintos).
- Los issues 4, 5 y 6 tocan `ProduccionLegacyFormView.vue` / `RecordDetailModal.vue`: **no**
  fusionar dos de esos en el mismo PR sin coordinating.

---

## 6. Validaciones

Obligatorias antes de pasar cada PR a `ready`:

```bash
git diff --check
git diff --cached --check
python -m pytest
python -m compileall app
```

En este repo, con el venv del backend:

```bash
cd backend
& venv\Scripts\python.exe -m pytest
& venv\Scripts\python.exe -m compileall app
```

Además, para este plan:

- **Tests backend nuevos** (`backend/tests/test_evidencia_produccion.py`):
  - el upload crea la fila y escribe el archivo;
  - un mime no permitido es rechazado con 422;
  - un archivo mayor al máximo es rechazado con 422;
  - crear un registro de `PROCESO` sin evidencia de procesador → **422**;
  - crear un registro de `PROCESO` con la evidencia vinculada → **201**;
  - `HORAS MAQUINAS` sin `hr_fin` > 0 → **422**;
  - subir dos veces la misma `(form_uuid, tipo)` no duplica;
  - un operador no puede verificar (403); un encargado sí (200).
  - **cobertura por roles (R7)**: un registro de `PROCESO` con una sola foto de pantalla y
    `incluye_horometro=1` → **201**; la misma foto con `incluye_horometro=0` → **422**;
    con las dos fotos → **201**;
  - una evidencia **rechazada** no cuenta para cubrir el rol (R2).
- **Tests frontend nuevos**: `EvidenciaField.test.js`, y extender `produccion.test.js` con el
  orden de sync (evidencia antes que registro).
- **Contra la base real** (no sólo SQLite): aplicar la migración en `registro_demo` (MariaDB de
  WSL) y correr la API real contra ella. Recordar que la suite corre sobre SQLite y no ve los
  bugs de MySQL.
- **Evidencia visual**: capturas reales en `docs/screenshots/evidencia_produccion/` a **1638x969**
  (pantalla del cliente) y **1366x768**, con el formulario en el paso de evidencia y el detalle
  con la foto. Sin `QScrollArea` el layout se comprime y los widgets se superponen.
- **Reporte**: `docs/EVIDENCIA_PRODUCCION_VISUAL_REVIEW.md` con fecha, rama, comandos, resultado
  de tests, flujo probado, capturas, hallazgos y veredicto.

---

## 7. Riesgos

| # | Riesgo | Impacto | Mitigación |
|---|---|---|---|
| R-1 | ~~**Reindexar el wizard**~~ | — | **Desactualizado:** `tipoProcesoRules.js` ya resuelve los pasos condicionales. Agregar "Evidencia" es una entrada más del filtro (ver 3.6 c) |
| R-2 | **El 413 de nginx** traga todas las fotos | El operador no puede adjuntar | `client_max_body_size 12m` en el mismo PR de infra (issue 2), verificado con una foto real de >1 MB |
| R-3 | **Las fotos no están en el backup de MySQL** | Pérdida de evidencia ante un restore | Sumar el volumen al procedimiento de backup y documentarlo; es el costo explícito de D2 |
| R-4 | **Orden de sync incorrecto** → registro sin foto | Registro huérfano de evidencia | El registro sólo se envía después de que su evidencia sube; test que lo cubra |
| R-5 | ~~**La migración bloquea el deploy**~~ | — | **Desactualizado:** las migraciones se aplican solas al arrancar el contenedor (ver 3.6 b) |
| R-6 | **Blobs en IndexedDB** saturan el almacenamiento del navegador | El operador no puede registrar | Comprimir a ≤1600 px / JPEG 0.8 antes de encolar; probar con 3–4 fotos |
| R-7 | **HEIC de iPhone** no se renderiza en todos los navegadores | El operador ve una miniatura rota | Aceptar `image/heic` en el upload y convertir a JPEG en el navegador antes de subir |
| R-8 | Volumen Docker en el servidor real sin crear previamente | El contenedor arranca sin writable | El deploy crea el volumen (`docker compose up` lo hace) y el backend hace `mkdir -p`; verificar permisos del usuario del contenedor |
| R-9 | **El operador tilda mal** que el horómetro está en la pantalla | El registro queda sin evidencia válida del horómetro | El flujo de verificación lo detecta (R8): el encargado ve la foto y rechaza. La casilla arranca sin tildar (R9). **El costo es un registro observado, no evidencia falsa aceptada.** Requiere que D-F defina el camino de corrección |
| R-10 | **El seed de la migración pisa la configuración del admin** en cada deploy | El admin ajusta un flag y al día siguiente vuelve al valor original, sin aviso | **Resuelto en el issue 1:** los flags usan NULL como centinela de "sin configurar" y el seed solo toca filas con el flag en NULL. Verificado contra MySQL real: con un cambio simulado del admin, el re-run de la migración **no** lo revirtió |
| R-11 | **Dos volúmenes de evidencia** (uno por instancia) | Una foto subida por `produccion_fg` da 404 en `indufor`, que comparte la base | **Un solo volumen nombrado**, montado en los dos servicios del compose (ver 3.6 d) |

---

## 8. Fuera de alcance

- No se cambia la lógica de cálculo de producción (`produccion = hr_fin - hr_inicio` en
  `HORAS MAQUINAS` ya está resuelta en backend, issue #146).
- No se toca el formulario de Caminos (`CaminosFormView.vue`) salvo que se agregue un flag de
  evidencia a sus tipos de proceso.
- No se implementa exportación a PDF de los registros con evidencia.
- No se implementa OCR ni lectura automática del horómetro: la detección de si el horómetro figura
  en la pantalla es una **declaración del operador**, contrastada por el encargado al verificar.
- No se implementa configuración por equipo (`moviles`) para la detección: si más adelante
  molesta al operador repetir la declaración, se puede agregar como atajo **recordando** la última
  respuesta por máquina **en el teléfono**, sin tocar el backend.
- No se rehace la cola offline existente: sólo se le agrega el store de evidencias.
- No se migran fotos históricos: los registros anteriores quedan sin evidencia.

---

## 9. Decisiones abiertas y pendientes

| # | Punto | Default asumido | Cómo se cierra |
|---|---|---|---|
| **D-A** | Alcance de `hr_fin` obligatorio | **RESUELTO 2026-10-24:** `hr_fin` es obligatoria **sólo en los tipos de proceso que usan horómetro**. No aplica a `CARGA`, `EXTRACCION`, `CARRETEO` ni al resto, que no tienen horómetro. | Cerrado por el usuario. |
| **D-B** | ¿La foto del horómetro es una o dos? | **RESUELTO 2026-10-24:** **una sola foto**, tomada **al final del trabajo**. Documenta la lectura final (`hr_fin`). No se pide foto de `hr_inicio`. | Cerrado por el usuario. |
| **D-C** | ¿La verificación puede rechazar y dejar el registro sin evidencia válida? | Sí: el rechazo marca la foto, el registro queda *observado*, no se borra | Si el rechazo debe **impedir** el registro, hay que agregar un estado al registro y una regla en el dashboard |
| **D-D** | ¿Quién puede **rechazar**? | `encargado` y `admin` | Si también debe poder hacerlo un supervisor de UN, cambia la dependencia del endpoint |
| **D-E** | Nombre de los tipos de evidencia | `horometro` y `procesador` | Ajustable; es el `tipo` de la columna y el valor del enum |
| **D-F** | ¿Se puede **editar** una foto cargada? | **RESUELTO 2026-10-25 (issue #198):** **sí**, se puede adjuntar una foto nueva a un registro ya creado (`POST /api/produccion/registros/{id}/evidencias`). Si el encargado rechaza la foto, el operador sube otra sin rehacer el parte entero. | Cerrado en la implementación del issue #198. La unicidad "una sola evidencia **viva** por `(form_uuid, tipo)`" la garantiza la aplicación: la foto rechazada queda como historial y la nueva la reemplaza. |

### Notas de la implementación del issue #198 (API)

- **Los estados de la evidencia pasaron de tres a cuatro.** Se agregó `3 = reemplazada`: la foto
  anterior a la que subió una posterior queda como historial, pero **no** se marca como
  "rechazada" (a nadie la evaluó). Por eso el índice único `(form_uuid, tipo)` pasó a ser un
  índice normal: puede haber más de una fila por tipo (la rechazada + la viva).
- **`cargado_por_id`**: el nombre de quien subió la foto no es unívoco y los permisos se
  deciden por id, no por texto.
- **El lock de MySQL** pasó a `backend/app/core/locks.py` (lo usan el alta del parte y la
  subida de evidencia). La subida toma `prod_evid:{form_uuid}`: dos reintentos simultáneos no
  pueden dejar dos evidencias vivas del mismo tipo.
- **R3 y el formulario legacy (pendiente para el issue 4):** el backend exige `hr_fin > hr_inicio`
  en los tipos de proceso cuyo `campos` incluye `hora_inicio`/`hora_fin`. El formulario legacy
  (`ProduccionLegacyFormView.vue`) hoy acepta `hr_fin == hr_inicio` ("la lectura final no puede
  ser *menor*"). El issue 4 tiene que alinear `horasValidas` con el backend, o el operador va a
  ver un 422 en un caso que la pantalla daba por válido.

---

## 10. Próximo paso

**D-A, D-B y D-F están resueltas** (ver sección 9). El alcance del plan está cerrado; quedan
abiertas sólo D-C a D-E, que son decisiones menores que se pueden tomar durante la implementación.

### Estado

- [x] **Issue #194** (issue 1 del plan) — esquema + flags. Hecho y mergeado (PR #195).
- [x] **Issue #196** (issue 2 del plan) — infra: volumen Docker compartido, límite de nginx,
      settings y barrido de huérfanos. Hecho y mergeado (PR #197).
- [x] **Issue #198** (issue 3 del plan) — API de evidencia: upload, servir bytes, listar,
      verificar, D-F y R2/R3 en el alta.
- [ ] **Issue 4** — captura en el formulario.
- [ ] **Issue 5** — modo offline.
- [ ] **Issue 6** — verificación por el encargado.
- [ ] **Issue 7** — manuales y procedimientos.

### Antes de abrir el issue 4

1. Alinear `horasValidas` del formulario legacy con la regla del backend (`hr_fin > hr_inicio`).
2. Confirmar que el volumen de evidencia quede **creado** en el servidor antes del primer
   deploy con fotos: `docker volume create registro_produccion_evidencia` (o lo crea el propio
   `docker compose up`).

### Cómo se working

1. Abrir el issue siguiendo el loop de `AGENTS.md`:
   rama desde `main` → migración → modelo → esquema → Admin → validaciones → PR draft.
2. Validar la migración contra la base real (MariaDB de WSL, base `registro_demo`) con el runner
   del proyecto (`python -m app.migrate`), **dos veces seguidas** para probar la idempotencia.
3. Seguir con los issues 4 (frontend), 5 (offline) y 6 (verificación).
