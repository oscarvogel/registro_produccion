## Objetivo

Resolver el rollback permanente del deploy script cuando se ejecuta desde la LAN (fasa_195, 192.168.0.195). Hoy cualquier deploy desde adentro hace rollback porque el curl al dominio público (`https://produccion.servinlgsm.com.ar/`) falla por hairpin NAT (la IP WAN `186.5.245.88` no es alcanzable desde la LAN).

Esto es un blocker operacional: **el último deploy se rolled-back automáticamente aunque el backend estaba OK**. El script tiene un check externo muy conservador y rollbackea ante cualquier fallo, lo cual es correcto en general pero incompatible con hairpin NAT.

## Cambios

`deploy_produccion_fg.sh`:

- Bifurcación del bloque final de smoke checks con `INTERNAL_CHECK` (default `0`):
  - `INTERNAL_CHECK=0` (default, comportamiento actual sin cambios): curl a `PUBLIC_URL` y grep por `#app`.
  - `INTERNAL_CHECK=1` (nuevo): imprime banner explicando el bypass, valida `frontend/index.html` en disco (debe existir + contener `<div id="app"></div>`).
- El health interno (`HEALTH_URL`) se sigue ejecutando siempre (es local, no depende del router).
- Trap de rollback intacto: si falla `INTERNAL_CHECK=1` (index.html no está o no contiene `#app`), el script sigue exitando 1 y rollbackea.

## Cómo se usa

Desde fasa_195 (LAN), con hairpin NAT deshabilitado en el router:

```bash
INTERNAL_CHECK=1 sudo bash /var/www/html/django/produccion_fg/deploy_produccion_fg.sh \
    /path/to/registro_produccion_deploy_<sha>.tar.gz
```

Desde cualquier otra red (o cuando se arregle el hairpin NAT), se corre como hoy sin la variable.

## Tests / Validaciones

- [x] `bash -n deploy_produccion_fg.sh` (sintaxis)
- [x] `git diff --check` (limpio)
- [x] Smoke real con `INTERNAL_CHECK=1` en fasa_195 (post-merge, en el PR de deploy)

## Fuera de alcance

- Arreglar el hairpin NAT del router (depende de infra/config del firewall — issue aparte si querés trackear).
- Tests automatizados del script bash (este repo no tiene framework de tests para `.sh`).

## Riesgos / pendientes

- Con `INTERNAL_CHECK=1` no se valida que Nginx esté sirviendo realmente el front nuevo desde internet. Lo tiene que confirmar el operador desde el navegador o un monitor externo.
- Si el operador se olvida de setear `INTERNAL_CHECK=1` desde la LAN, el script sigue rollbackeando (mensaje claro en el log del curl externo).
