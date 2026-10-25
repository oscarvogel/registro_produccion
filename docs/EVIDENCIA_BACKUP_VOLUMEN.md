# Respaldo y restauracion del volumen de evidencia fotografica

Las fotos de evidencia (horometro y pantalla del procesador) **no viven en
MySQL**: viven en disco, dentro de un volumen Docker. El backend guarda en la
tabla `produccion_evidencia` los datos de cada foto (ruta, hash, estado), pero
los bytes estan en el volumen.

Por eso hay que respaldar **las dos cosas**: la base y el volumen. Si se
restaura la base sin el volumen, el listado de evidencia sigue apareciendo
pero las fotos dan error al abrirlas.

---

## 1. Que hay que respaldar

| Que | Donde | Como |
|---|---|---|
| Datos de la evidencia (ruta, hash, estado, verificado por) | MySQL, tabla `produccion_evidencia` | El respaldo de la base que ya se hace |
| Los archivos de las fotos | Volumen Docker `evidencia` (el `name:` del compose es `registro_produccion_evidencia`, pero en el servidor queda con el prefijo de Coolify: ver sección 2) | Este documento |

El volumen es **uno solo** para las dos instancias (`produccion_fg` e
`indufor`): las dos comparten la base `fg`, asi que una foto subida por una
tiene que poder leerse desde la otra.

Dentro del contenedor, el volumen esta montado en `/app/media` y las fotos en
`/app/media/evidencias`, ordenadas por mes:

```
/app/media/evidencias/2026/10/e2e-evidencia-1792889069_procesador_68b826fd.jpg
```

## 2. Donde esta el volumen en el servidor

El `docker-compose.yml` lo declara con nombre explicito, para que no dependa
del nombre del proyecto de compose:

```yaml
volumes:
  evidencia:
    name: registro_produccion_evidencia
```

<div class="warning">
<b>Ojo: en el deploy por Coolify ese <code>name:</code> no es el que queda.</b>
Coolify pisa el nombre de los volúmenes con el prefijo de su proyecto de
compose. En <code>fasa_189</code> el volumen real se llama
<code>4hcjxromkdmdylfjbw0fgvs4_evidencia</code> (el prefijo es el UUID de la
app de Coolify, <code>4hcjxromkdmdylfjbw0fgvs4</code>).
<br><br>
Por eso <b>ningún comando de este documento debe escribir el nombre a mano</b>:
hay que resolverlo con <code>docker volume ls</code>. Un nombre escrito a mano
da <i>no such volume</i> y el respaldo sale vacío sin avisar.
</div>

Los comandos de abajo usan una variable `VOL` que se resuelve una vez:

```bash
VOL=$(docker volume ls -q | grep evidencia)
echo "volumen de evidencia: $VOL"
docker volume inspect "$VOL"
docker run --rm -v "$VOL:/data:ro" alpine \
  sh -c 'du -sh /data; find /data -type f | wc -l'
```

Si `echo` no muestra nada, el volumen no existe todavia: lo crea el
`docker compose up` del deploy.

## 3. Respaldo (sin bajar la aplicacion)

El respaldo es de **solo lectura**: la aplicacion sigue funcionando y
siguiendo subiendo fotos mientras se arma el `.tar.gz`.

```bash
mkdir -p /srv/backups/registro_produccion
VOL=$(docker volume ls -q | grep evidencia)

docker run --rm \
  -v "$VOL:/data:ro" \
  -v /srv/backups/registro_produccion:/backup \
  alpine sh -c 'cd /data && tar czf /backup/evidencia-$(date +%F-%H%M).tar.gz .'
```

Eso deja un archivo tipo `/srv/backups/registro_produccion/evidencia-2026-10-25-0030.tar.gz`.

### Verificar que el respaldo sirve

Un `.tar.gz` que no se abrio es un respaldo que no existe. Hay que mirar el
contenido y, sobre todo, **comparar la cantidad de archivos con la cantidad de
filas de la base**:

```bash
# 1. Ver el contenido
docker run --rm -v /srv/backups/registro_produccion:/backup:ro alpine \
  sh -c 'tar tzf /backup/evidencia-2026-10-25-0030.tar.gz | head -20'

# 2. Contar los archivos del respaldo
docker run --rm -v /srv/backups/registro_produccion:/backup:ro alpine \
  sh -c 'tar tzf /backup/evidencia-2026-10-25-0030.tar.gz | grep -c "\."'

# 3. Contar los archivos que hay ahora en el volumen
docker run --rm -v "$VOL:/data:ro" alpine \
  sh -c 'find /data -type f | wc -l'

# 4. Comparar con las filas de la base
#    (mysql -h <host> -u <usuario> -p <base>)
SELECT COUNT(*) FROM produccion_evidencia;
```

El numero del punto 2 tiene que ser igual al del punto 3 (salvo fotos que se
subieron entre el respaldo y la cuenta, que es normal y no es un problema).

### Cada cuanto

| Frecuencia | Motivo |
|---|---|
| **Diario** (con el respaldo de la base) | Es lo que evita perder el dia de evidencia. |
| Antes de cualquier deploy | Por si el deploy toca el volumen. |
| Antes de purgar la evidencia huerfana | El purge borra archivos de verdad. |

El respaldo de la base y el del volumen tienen que ser **del mismo momento**:
si se restaura la base de ayer con las fotos de hoy, quedan filas sin archivo.

## 4. Restauracion

Restaurar el volumen **borra lo que hay ahora**. Por eso hay que confirmar el
archivo antes de empezar.

```bash
VOL=$(docker volume ls -q | grep evidencia)

# 0. Confirmar que el archivo existe y se puede leer
docker run --rm -v /srv/backups/registro_produccion:/backup:ro alpine \
  sh -c 'tar tzf /backup/evidencia-2026-10-25-0030.tar.gz | head'

# 1. Parar los dos backends: si se restaura escribiendo encima, se mezclan
#    los archivos viejos con los nuevos
docker compose stop produccion_fg indufor

# 2. Reemplazar el contenido del volumen
docker run --rm \
  -v "$VOL:/data" \
  -v /srv/backups/registro_produccion:/backup:ro \
  alpine sh -c 'cd /data && rm -rf ./* && tar xzf /backup/evidencia-2026-10-25-0030.tar.gz'

# 3. Levantar los backends
docker compose up -d produccion_fg indufor

# 4. Verificar
docker run --rm -v "$VOL:/data:ro" alpine \
  sh -c 'find /data -type f | wc -l'
```

Y despues, **desde la aplicacion**: abrir un registro que tenga evidencia
pendiente o verificada y confirmar que la foto se ve. La foto se descarga con
el token del usuario, asi que conviene probarla con un usuario real.

<div class="warning">
El paso 2 borra el contenido del volumen. Si el respaldo no es del momento que se quiere, se pierden las fotos que se hayan subido despues. Por eso el paso 0 no es opcional.
</div>

## 5. Evidencia huerfana (que se limpia sola)

Hay dos clases de basura:

- **Filas sin parte**: el operador subio la foto pero nunca completo el parte.
- **Archivos sin fila**: la foto se escribio pero la fila no llego a la base.

Las dos se barren con el script del backend:

```bash
# Dentro del contenedor
docker compose exec produccion_fg python scripts/purge_evidencia_huerfana.py

# Para borrar de verdad (por defecto SOLO informa)
docker compose exec produccion_fg python scripts/purge_evidencia_huerfana.py --si

# Con mas margen (no borra nada de los ultimos 30 dias)
docker compose exec produccion_fg python scripts/purge_evidencia_huerfana.py --dias 30 --si
```

El margen por defecto es de 7 dias, para no tocar una foto que todavia esta
encolada en el telefono de un operador sin conexion.

Antes de correrlo con `--si`, correrlo sin flag y **leer la lista**: el script
informa que va a borrar y con que motivo.

Conviene correrlo cada mes, y **siempre despues de un respaldo**: si el purge
borra algo que despues hay que recuperar, el respaldo tiene que estar previo.

## 6. Cuando algo sale mal

| Sintoma | Que revisar |
|---|---|
| La foto da error al abrirla | El archivo no esta en el volumen. Comparar `find /data -type f \| wc -l` con `SELECT COUNT(*) FROM produccion_evidencia`. |
| El listado muestra evidencia y la foto no se ve | La fila existe pero el archivo se borro (purge) o nunca subio (subida a medias). |
| El volumen no existe | `docker volume ls \| grep evidencia`. El deploy lo crea: `docker compose up -d` lo levanta. |
| `no such volume` al respaldar | El nombre esta escrito a mano y no es el real. Resolverlo con `VOL=$(docker volume ls -q \| grep evidencia)`. |
| El respaldo sale vacio | El volumen estaba vacio (nadie subio fotos) o el `tar` se corrio con otra ruta. Repetir con el path explicito. |
| La restauracion no trae las fotos | El `.tar.gz` estaba corrupto: por eso el paso 0 de la restauracion abre el archivo antes de borrar nada. |
