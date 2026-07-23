# Deploy en produccion (fasa_195)

Documento de referencia para deployar `registro_produccion` en el server
`fasa_195` (192.168.0.195, user `ferreteria`, ssh key `~/.ssh/fasa_195`).

> Mantener este archivo vivo. Si el flujo cambia, actualizar.

---

## Arquitectura del server

`produccion.servinlgsm.com.ar` corre con **dos backends en paralelo**:

| Componente | Ruta / puerto | Como se levanta | Quien lo usa |
|---|---|---|---|
| **Frontend** (HTML/JS/CSS) | `/var/www/html/django/produccion_fg/frontend/` | Copia desde el tarball | nginx sirve los assets estaticos |
| **Backend container** | `127.0.0.1:18005` (Docker) | `docker compose -f /srv/apps/registro_produccion/docker-compose.yml up -d` | nginx hace proxy_pass a este |
| **Backend host** (legacy) | `0.0.0.0:8005` (gunicorn) | `/var/www/html/django/produccion_fg/restart.sh` | **NO se usa** (queda como fallback) |

El **container Docker es el que sirve a produccion**. El backend del host
(puerto 8005) es un vestigio: el `restart.sh` lo reinicia, pero el nginx
apunta al container en `:18005`. Si deployas solo el host, los usuarios
siguen viendo el codigo viejo porque el container no se toca.

### Diagrama

```
Browser
   |
   v
nginx (443) -- /api/* --> 127.0.0.1:18005 (container Docker, produccion_fg)
        \-- /*       --> /var/www/html/django/produccion_fg/frontend/
```

El `docker-compose.yml` en `/srv/apps/registro_produccion/docker-compose.yml`
define el container. El `Dockerfile` copia `backend/` al container y arranca
gunicorn en :8000. Docker mapea el :8000 del container al :18005 del host.

---

## Pre-flight checks

Antes de tocar nada, verificar:

```bash
ssh -i ~/.ssh/fasa_195 ferreteria@fasa_195

# 1. Estado actual del container
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}' \
  | grep produccion_fg

# 2. Commit que esta corriendo realmente
docker inspect registro_produccion_produccion_fg --format '{{.Config.Image}}'

# 3. Que el repo del server este sincronizado
cd /srv/apps/registro_produccion
git status -sb
git log --oneline -3

# 4. Health del backend actual
curl -fsS http://127.0.0.1:18005/health
```

Si el commit del container no coincide con `origin/main` de GitHub, el
container esta desactualizado. Hay que rebuild.

---

## Flujo de deploy paso a paso

### 1. Validar localmente

Desde tu maquina local, en la rama `main` con el commit que queres deployar:

```powershell
cd D:\notebook\active\registro_produccion

# Validar que el codigo compila y los tests pasan
cd backend; py -3.12 -m pytest ; py -3.12 -m compileall app ; cd ..
cd frontend; npx.cmd vitest run ; npx.cmd vite build ; cd ..

# Armar el paquete de deploy
powershell -ExecutionPolicy Bypass -File scripts\build_deploy_package.ps1
# Output: dist_deploy/registro_produccion_deploy_<sha>.tar.gz
```

### 2. Subir el paquete al server

```powershell
scp -i $env:USERPROFILE\.ssh\fasa_195 `
  dist_deploy\registro_produccion_deploy_<sha>.tar.gz `
  ferreteria@fasa_195:/home/ferreteria/
```

### 3. Conectarse al server y hacer el deploy

```powershell
ssh -i $env:USERPROFILE\.ssh\fasa_195 -t ferreteria@fasa_195
```

Adentro del server:

```bash
# 3a. Sincronizar el codigo fuente (esto trae TODO: backend, frontend, db_migrations)
cd /srv/apps/registro_produccion
git fetch origin
git reset --hard origin/main
git log --oneline -1   # confirmar que estamos en el commit deseado

# 3b. Aplicar migraciones DB (idempotentes, se pueden correr varias veces)
#     El script apply_db_migrations del deploy_produccion_fg.sh lee las
#     credenciales del .env del host y aplica los SQL de db_migrations.
#     Lo corremos manualmente para tener control fino:
DB="$(python3 -c "
from urllib.parse import urlparse
import re
content = open('/var/www/html/django/produccion_fg/backend/.env').read()
for line in content.splitlines():
    m = re.match(r'^DATABASE_URL=(.*)', line.strip())
    if m:
        u = urlparse(m.group(1))
        print(f'mysql -h{u.hostname} -P{u.port or 3306} -u{u.username} -p{u.password} {u.path.lstrip(\"/\")}')
        break
")"
echo "Comando mysql: $DB"

# Backup antes de migrar
mysqldump $(echo $DB | sed 's/-p\([^ ]*\) /-p\1 /' | awk '{for(i=1;i<=NF;i++){if($i=="-p"){i++;continue}print $i}}') \
  | gzip > /var/backups/registro_produccion/pre_migration_$(date +%Y%m%d_%H%M%S).sql.gz

# Aplicar migraciones nuevas (revisar que no se aplicaron antes)
for sql in /srv/apps/registro_produccion/db_migrations/*.sql; do
  echo "==> Aplicando $(basename $sql)"
  eval "$DB" < "$sql"
done

# 3c. Rebuild del container con el codigo nuevo
cd /srv/apps/registro_produccion
docker compose -f docker-compose.yml build produccion_fg

# 3d. Re-deploy del container (sin dependencias para no tocar indufor)
docker compose -f docker-compose.yml up -d --no-deps produccion_fg

# 3e. Validar
sleep 5
curl -fsS http://127.0.0.1:18005/health
echo
echo "Commit del container:"
docker inspect registro_produccion_produccion_fg --format '{{.Config.Image}}'
```

### 4. Verificar en el browser

1. Hard refresh en `https://produccion.servinlgsm.com.ar/` (Ctrl+Shift+R)
2. Si el Service Worker del PWA tiene la version vieja cacheada, ir a
   DevTools > Application > Service Workers > Unregister, despues
   Storage > Clear site data.
3. Probar el flujo nuevo (ej: Admin > Lugares de carga > Editar un lugar).

---

## Troubleshooting

### "Deployo pero los usuarios siguen viendo el codigo viejo"

El deploy actualizo el backend del host (puerto 8005) pero NO el container
Docker (puerto 18005). Verificar:

```bash
# Que el container este con la imagen nueva
docker inspect registro_produccion_produccion_fg --format '{{.Config.Image}}'

# Si la imagen no es la nueva, hacer rebuild + up
cd /srv/apps/registro_produccion
docker compose -f docker-compose.yml build produccion_fg
docker compose -f docker-compose.yml up -d --no-deps produccion_fg
```

### "El frontend no se actualiza en el browser"

1. Hard refresh (Ctrl+Shift+R).
2. Si sigue igual, DevTools > Application > Service Workers > Unregister
   + Storage > Clear site data.
3. Verificar que el server este sirviendo la version nueva:

```bash
curl -fsS http://127.0.0.1/ | grep -oE 'assets/index-[A-Za-z0-9_-]+\.js' | head -1
# Comparar con el index.html que se genero en el build local
```

### "Login tira 500 o la app no responde"

Probar el backend directo:

```bash
curl -fsS http://127.0.0.1:18005/health
curl -fsS http://127.0.0.1:8005/health
```

- Si `:18005` falla: container caido o codigo roto. Ver logs:
  `docker logs registro_produccion_produccion_fg --tail 100`
- Si `:8005` falla: irrelevante para produccion (no se usa), pero si
  queres: `/var/www/html/django/produccion_fg/restart.sh`

### "El query a la DB falla con 'Unknown column'"

Los `__tablename__` de los modelos SQLAlchemy no coinciden con los nombres
reales de las tablas en la DB. Es un problema de alineacion, no del deploy.

- Verificar con `DESCRIBE <tabla>` en la DB.
- Si el modelo usa PascalCase pegado (`tableroproduccion`) y la DB tiene
  snake_case (`tablero_produccion`), hay que actualizar el `__tablename__`
  del modelo. No es parte del deploy, es un fix de modelo.

### "El deploy script tira 'JSON decode error' en PowerShell"

Cuando probas endpoints con `Invoke-RestMethod -Body @{...} -ContentType
'application/json'` desde PowerShell, a veces no serializa bien. Workaround:

```powershell
$body = @{dni='12345678'; password='mipass'} | ConvertTo-Json -Compress
Invoke-RestMethod -Method Post -Uri 'http://localhost:8000/api/auth/login' `
  -Body $body -ContentType 'application/json'
```

### "El deploy script reinicia el backend equivocado"

El `deploy_produccion_fg.sh` actual reinicia el backend del **host**
(puerto 8005), no el container (puerto 18005). Esto es un bug conocido.
Workaround: hacer el rebuild + up del container manualmente, como se
documenta arriba. Fix permanente pendiente en otro PR.

---

## Comandos utiles de diagnostico

```bash
# Ver que container esta corriendo y con que imagen
docker ps | grep produccion

# Logs del container
docker logs registro_produccion_produccion_fg --tail 100 -f

# Ejecutar comando adentro del container
docker exec -it registro_produccion_produccion_fg bash

# Probar API desde el server
curl -fsS http://127.0.0.1:18005/health
curl -fsS http://127.0.0.1:8005/health

# Probar API publica (sin hairpin NAT, falla por la red local)
curl -fsS https://produccion.servinlgsm.com.ar/api/produccion/lugares-carga?un_id=1

# Inspeccionar la respuesta del admin lugares-carga
TOKEN=$(curl -fsS -H "Content-Type: application/json" \
  -d '{"dni":"23347203","password":"7203"}' \
  http://127.0.0.1:18005/api/auth/login \
  | python3 -c 'import sys, json; print(json.load(sys.stdin)["access_token"])')
curl -fsS -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:18005/api/admin/lugares-carga | python3 -m json.tool

# Ver el nginx config del dominio
cat /etc/nginx/sites-enabled/produccion.servinlgsm.com.ar

# Ver la migracion que esta pendiente
ls -la /srv/apps/registro_produccion/db_migrations/
```

---

## Hairpin NAT

El router de la red local **no tiene hairpin NAT** configurado. Esto
significa que desde el server no podes hacer `curl
https://produccion.servinlgsm.com.ar/` (la IP publica no resuelve de
vuelta al server). Por eso todos los curls de este doc apuntan a
`127.0.0.1` o a los puertos internos. La validacion de la URL publica
la hace alguien desde fuera de la LAN.

---

## Pendiente

- [ ] Fixear `deploy_produccion_fg.sh` para que detecte el modo Docker
      y haga `git pull` + `docker compose build` + `docker compose up -d`
      en vez de tocar el host. Asi el deploy se hace en un solo paso.
- [ ] Alinear los `__tablename__` de los modelos legacy con la DB real
      (snake_case). Es un PR aparte, no urgente.
- [ ] Eliminar el backend legacy en :8005 si ya no se necesita.
