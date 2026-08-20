# Motivos no operativos por unidad de negocio

El catálogo de motivos no operativos se administra desde `/admin/gestion`, opción **Motivos no operativos**.

- Los motivos se crean una sola vez y se asignan a una o varias unidades de negocio.
- Un motivo puede activarse o desactivarse globalmente.
- La asignación por unidad también puede cambiarse sin borrar el motivo.
- El formulario de producción sigue aceptando texto libre en `motivo_no_op`.
- El frontend consulta `/api/catalogos/motivos-no-operativos?un_id=<ID>` al cambiar de unidad y conserva una copia en IndexedDB para uso offline.
- Si el endpoint todavía no está disponible durante un despliegue escalonado, se conservan como fallback los 11 motivos históricos incluidos en el frontend.

La migración `db_migrations/20260820_motivos_no_operativos.sql` crea las tablas y asigna inicialmente los 11 motivos históricos a todas las unidades existentes.
