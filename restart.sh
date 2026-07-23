#!/bin/bash
# ---------------------------------------------------------------------------
# DEPRECATED: este script reinicia el backend legacy del host (:8005).
# El server de produccion usa Docker container en :18005, no este.
# No se usa mas; queda aca solo para rollback de emergencia.
# Si lo estas corriendo, seguro no es lo que queres.
# El deploy correcto usa deploy_produccion_fg.sh, que detecta Docker auto.
# ---------------------------------------------------------------------------

echo "================================================================"
echo "DEPRECATED: restart.sh ya no reinicia el backend de produccion."
echo "================================================================"
echo
echo "El server de produccion corre el backend en un container Docker"
echo "(registro_produccion_produccion_fg) en el puerto 18005, no en el"
echo "puerto 8005 del host."
echo
echo "Para re-deployar el container, usá el flujo Docker de"
echo "deploy_produccion_fg.sh, o manualmente:"
echo
echo "  cd /srv/apps/registro_produccion"
echo "  git fetch origin && git reset --hard origin/main"
echo "  docker compose -f docker-compose.yml build produccion_fg"
echo "  docker compose -f docker-compose.yml up -d --no-deps produccion_fg"
echo
echo "Si REALMENTE queres levantar el backend legacy del host (puerto"
echo "8005), restaurá este script desde git history con:"
echo
echo "  git log --all --oneline -- restart.sh | head -5"
echo "  git show <commit-anterior>:restart.sh > /tmp/restart.sh.legacy"
echo
echo "Y entonces ejecutá:"
echo "  bash /tmp/restart.sh.legacy"
echo
exit 1
