# Despliegue de la evidencia fotografica

Como publicar la evidencia fotografica (y el aviso por WhatsApp) en
produccion, con el deploy por Coolify sobre `fasa_189`.

La guia general del deploy es [`DEPLOY.md`](../DEPLOY.md): este documento solo
agrega lo que es especifico de la evidencia.

---

## 1. Frontend y backend van juntos

**No se puede publicar solo el backend.** El frontend nuevo sube la foto al
guardar el parte; el backend nuevo exige la foto en los tipos de proceso que
la piden. Publicar uno sin el otro rompe el circuito:

| Se publica | Que pasa |
|---|---|
| Solo el frontend | La foto se sube a un endpoint que no existe: error al guardar. |
| Solo el backend | El alta de `PROCESO`, `VOLTEO` y `HORAS MAQUINAS` pide una foto que el formulario viejo no tiene: **el operador no puede guardar el parte**. |

El compose es uno solo y `docker compose up` reconstruye las cuatro imagenes,
 asi que un solo deploy publica las dos cosas. Lo unico que hay que evitar es
un deploy parcial (por ejemplo, reconstruir solo el backend).

## 2. Antes de desplegar: la gateway de WhatsApp

El aviso al encargado (issue #206) sale por la gateway de Vogel. Sin API key o
sin instancia **el aviso no sale, pero la app funciona igual**: el registro se
guarda y el log dice por que.

O sea: si todavia no hay credenciales, se puede deployar igual. El aviso se
activa despues, sin otro deploy (ver §4.2).

La API key de Forestal vive cifrada en la base del sistema Forestal
(tabla `informes_whatsapp_credenciales`, cifrado Fernet). La instancia de
Forestal es `oscar_claro_2`.

### Ojo con la trampa de Coolify

El compose declara las variables con `${VAR:-default}`. Coolify **materializa
esas filas en la app** con el valor por defecto, y hay que ponerles el valor
real **a mano**. Ademas Coolify guarda **dos juegos** de variables (produccion
`is_preview = false` y preview `is_preview = true`): si se cambia solo el de
produccion, el de preview lo resucita con el valor viejo.

Es exactamente la misma trampa que con `SOURCE_COMMIT`, documentada en
[`DEPLOY.md` §4](../DEPLOY.md#4-sobre-las-etiquetas-de-versión).

## 3. Desplegar

El procedimiento es el de [`DEPLOY.md`](../DEPLOY.md), sin cambios:

```powershell
git fetch --prune origin
git log --oneline origin/main -3
gh pr checks <pr>          # tiene que estar verde
powershell -ExecutionPolicy Bypass -File scripts\deploy_produccion_fg.ps1
```

El script actualiza las variables de version, dispara el deploy, lo espera y
verifica `/api/health` en las dos instancias.

## 4. Verificar (obligatorio)

### 4.1 La migracion y el volumen

La migracion se aplica **sola al arrancar el backend** (`RUN_MIGRATIONS=1`).

```bash
ssh fasa_189 "docker logs <contenedor-produccion_fg> 2>&1 | grep -i migracion"
```

En el log tiene que estar `migraciones aplicadas OK`.

La tabla de la evidencia tiene que existir:

```sql
SELECT COUNT(*) FROM produccion_evidencia;
```

Y el volumen, montado en los dos backends:

```bash
ssh fasa_189 "docker volume ls | grep evidencia"
ssh fasa_189 "docker run --rm -v \$(docker volume ls -q | grep evidencia):/data:ro alpine sh -c 'ls -la /data'"
```

El volumen lo crea el `docker compose up` del deploy. El `name:` del compose
(`registro_produccion_evidencia`) **no es el que queda en el servidor**: Coolify
pisa el nombre de los volúmenes con el prefijo de su proyecto, y en
`fasa_189` el volumen real se llama `4hcjxromkdmdylfjbw0fgvs4_evidencia`. Por
eso los comandos lo resuelven con `docker volume ls` y nunca lo escriben a
mano.

### 4.2 El circuito de la foto, de punta a punta

Con un operador real (o con el login de prueba del ambiente):

1. Cargar un parte de `PROCESO` (exige foto de horometro y de procesador).
2. Confirmar que aparece el paso `Evidencia` y que **no deja avanzar sin foto**.
3. Tomar la foto y guardar.
4. En `Seguimiento > Operacion > Detalle de registros`, con el filtro
   `Esperando verificacion`, el registro tiene que aparecer con la marca
   `Sin verificar`.
5. Abrir el detalle: la seccion `Evidencia fotografica` tiene que mostrar la
   **foto** (no un error) y los botones `Verificar` / `Rechazar`.
6. Verificar la foto: la marca desaparece y queda `Verificada por ...`.

Si el paso 5 muestra la foto rota, el archivo no esta en el volumen: ver
[`EVIDENCIA_BACKUP_VOLUMEN.md`](EVIDENCIA_BACKUP_VOLUMEN.md) y §5 de este
documento.

### 4.3 El aviso por WhatsApp

Con un encargado que tenga `telefono` cargado en `personal`:

```sql
SELECT idPersonal, Nombre, telefono, unidad_negocio
FROM personal WHERE encargado = 1 AND activo = 1;
```

Si el `telefono` esta vacio, **el aviso no sale**: queda en el log
(`El encargado <id> no tiene un telefono valido cargado`) y el registro se
guarda igual. Hay que cargar el numero del encargado en el alta de personal.

Con el numero cargado, el log del backend tiene que mostrar:

```
Aviso de WhatsApp encolado para <ultimos 4 digitos> (messageId=..., externalRef=registro-produccion:registro:<id>)
```

`encolado` es lo que devuelve la gateway (HTTP 202): la gateway **acepta** el
mensaje, no confirma que haya llegado. Un `HTTP 403` significa key e instancia
de empresas distintas.

### 4.4 Los dos servicios

El compose levanta los cuatro servicios. Los dos backends tienen que estar
healthy y los dos frontends sirviendo:

```bash
ssh fasa_189 "docker ps --format '{{.Names}} | {{.Status}}' | grep registro_produccion"
```

```powershell
Invoke-WebRequest https://produccion.servinlgsm.com.ar/api/health -UseBasicParsing | Select-Object -ExpandProperty Content
Invoke-WebRequest https://produccion.indufor.com.ar/api/health -UseBasicParsing | Select-Object -ExpandProperty Content
```

## 5. Cargar la API key despues (sin otro deploy)

Si se desplego sin credenciales y despues se consiguen, no hace falta volver
a desplegar: basta con setear las variables en Coolify y **reiniciar** los
backends.

```powershell
$token = (Get-Content "$env:USERPROFILE\.coolify-token" -Raw).Trim()

# OJO: hay que hacerlo en los DOS juegos de variables (is_preview false y true)
foreach ($preview in @($false, $true)) {
  $body = @{ key = 'WHATSAPP_API_KEY'; value = '<la-key>'; is_preview = $preview } | ConvertTo-Json
  Invoke-RestMethod -Uri 'https://coolify.vogelconsultoria.com.ar/api/v1/applications/4hcjxromkdmdylfjbw0fgvs4/envs' `
    -Method PATCH -Headers @{ Authorization = "Bearer $token" } `
    -ContentType 'application/json' -Body $body

  $body = @{ key = 'WHATSAPP_INSTANCE'; value = 'oscar_claro_2'; is_preview = $preview } | ConvertTo-Json
  Invoke-RestMethod -Uri 'https://coolify.vogelconsultoria.com.ar/api/v1/applications/4hcjxromkdmdylfjbw0fgvs4/envs' `
    -Method PATCH -Headers @{ Authorization = "Bearer $token" } `
    -ContentType 'application/json' -Body $body
}
```

Y despues reiniciar los contenedores de los backends (en el panel: la app ->
Deploy, o `docker compose restart produccion_fg indufor` en el host).

Comprobar que quedaron cargadas:

```powershell
Invoke-RestMethod -Uri 'https://coolify.vogelconsultoria.com.ar/api/v1/applications/4hcjxromkdmdylfjbw0fgvs4/envs' `
  -Headers @{ Authorization = "Bearer $token" } |
  Where-Object { $_.key -like 'WHATSAPP*' } |
  Select-Object key, value, is_preview
```

`value` de `WHATSAPP_API_KEY` no se muestra entero en esta vista: lo que
importa es que **no esté vacío**.

## 6. Rollback

El compose no tiene rollback automatico: la forma segura de volver atras es
**revertir en `main` y redesplegar** (commit revert + deploy), que deja el
historial auditado.

Si lo que se quiere es volver atras solo en la parte de evidencia, alcanza con
desactivar los flags `Requiere Foto Horometro` y `Requiere Foto Procesador`
de los tipos de proceso afectados (en Admin > Tipos de Proceso). Con los dos
flags apagados, el paso `Evidencia` desaparece y el proceso se carga como
antes. **Las fotos ya subidas no se borran**: quedan en el volumen y en la
tabla `produccion_evidencia`, y se pueden volver a activar los flags despues.

<div class="warning">
Revertir el deploy no borra la tabla <code>produccion_evidencia</code> ni el volumen: las migraciones son idempotentes y la tabla queda, vacia o no. Eso es a proposito: un rollback de codigo no tiene por que perder evidencia ya tomada.
</div>

## 7. Antes de tocar nada en produccion

| Chequeo | Como |
|---|---|
| `main` tiene el commit | `git log --oneline origin/main -3` |
| El CI esta verde | `gh pr checks <pr>` |
| Hay respaldo del volumen | Ver [`EVIDENCIA_BACKUP_VOLUMEN.md`](EVIDENCIA_BACKUP_VOLUMEN.md) |
| Hay respaldo de la base | El respaldo de la base que ya se hace |
| Las variables de version van a ser correctas | El script `deploy_produccion_fg.ps1` las setea |
