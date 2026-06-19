# Docker Migration Runbook

Plantilla reusable para migrar una app existente a Docker con un contenedor paralelo y switch controlado de Nginx.

Indufor fue el primer caso exitoso de este procedimiento: `produccion.indufor.com.ar` quedo sirviendo desde `registro_produccion_indufor` en `127.0.0.1:18004`.

## Variables

Reemplazar antes de usar:

```text
APP_NAME=<nombre_app>
DOMAIN=<dominio_publico>
OLD_SERVICE=<servicio_systemd_viejo>
OLD_PORT=<puerto_viejo>
NEW_SERVICE=<servicio_docker_compose>
NEW_CONTAINER=<nombre_contenedor>
NEW_PORT=<puerto_paralelo>
NGINX_SITE=/etc/nginx/sites-available/<archivo_site>
```

## 1. Preflight

Solo lectura:

```bash
systemctl is-active "$OLD_SERVICE" || true
docker ps --filter "name=$NEW_CONTAINER"
ss -ltnp | grep -E ":($OLD_PORT|$NEW_PORT) " || true
grep -n "proxy_pass" "$NGINX_SITE"
curl -f "http://127.0.0.1:$OLD_PORT/" || true
```

Confirmar que no se van a ejecutar migraciones ni escrituras de base de datos salvo autorizacion explicita.

## 2. Levantar contenedor paralelo

Construir y levantar solo la instancia objetivo:

```bash
cd /srv/apps/<repo>
docker compose build "$NEW_SERVICE"
docker compose up -d "$NEW_SERVICE"
docker compose ps
docker logs --tail=100 "$NEW_CONTAINER"
```

No usar `docker compose up -d` sin servicio si el compose declara otras apps.

## 3. Validar puerto paralelo

```bash
curl -f "http://127.0.0.1:$NEW_PORT/"
curl -f "http://127.0.0.1:$NEW_PORT/docs"
curl -f "http://127.0.0.1:$NEW_PORT/openapi.json"
curl -f "http://127.0.0.1:$NEW_PORT/health"
```

Si `/health` valida DB, confirmar `database=ok`.

## 4. Backup Nginx

```bash
TS=$(date +%Y%m%d-%H%M%S)
sudo cp "$NGINX_SITE" "$NGINX_SITE.bak-$TS"
echo "$TS"
grep -n "proxy_pass" "$NGINX_SITE"
```

Guardar el path exacto del backup en el informe.

## 5. Cambiar Nginx

Reemplazo minimo:

```bash
sudo sed -i "s#proxy_pass http://127.0.0.1:$OLD_PORT;#proxy_pass http://127.0.0.1:$NEW_PORT;#" "$NGINX_SITE"
grep -n "proxy_pass" "$NGINX_SITE"
```

No tocar otros server blocks ni otros dominios.

## 6. Validar y recargar

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Si `nginx -t` falla, restaurar el backup antes de recargar.

## 7. Smoke tests publicos

```bash
curl -I "https://$DOMAIN/"
curl -f "https://$DOMAIN/api/produccion/lugares-carga" || true
curl -f "http://127.0.0.1:$NEW_PORT/health"
docker logs --tail=100 "$NEW_CONTAINER"
```

La ruta publica `/health` puede no estar expuesta si Nginx sirve frontend para rutas no `/api`. En ese caso usar health interno y una ruta `/api/...` publica para confirmar que el backend Docker recibe trafico.

## 8. Apagar servicio viejo

Solo si el dominio publico y el backend Docker validan correctamente:

```bash
sudo systemctl stop "$OLD_SERVICE"
systemctl is-active "$OLD_SERVICE" || true
ss -ltnp | grep -E ":($OLD_PORT|$NEW_PORT) " || true
curl -f "http://127.0.0.1:$NEW_PORT/health"
```

No ejecutar `disable` al principio. Mantener rollback facil durante el periodo de observacion.

## 9. Rollback

```bash
sudo cp "$NGINX_SITE.bak-$TS" "$NGINX_SITE"
sudo nginx -t
sudo systemctl reload nginx
sudo systemctl start "$OLD_SERVICE"
curl -f "http://127.0.0.1:$OLD_PORT/"
curl -I "https://$DOMAIN/"
```

Detener el contenedor nuevo solo si hace falta:

```bash
docker compose stop "$NEW_SERVICE"
```

## 10. Checklist final

```text
[ ] Nginx apunta al puerto Docker
[ ] nginx -t paso
[ ] reload Nginx sin error
[ ] dominio publico responde
[ ] ruta /api publica responde desde Docker
[ ] health interno Docker responde OK
[ ] DB check OK si aplica
[ ] contenedor healthy
[ ] servicio viejo detenido pero no deshabilitado
[ ] puerto viejo liberado
[ ] backup Nginx identificado
[ ] rollback documentado
[ ] no se imprimieron secretos
[ ] no se ejecutaron migraciones sin autorizacion
[ ] no se borraron archivos ni backups
```
