## Objetivo

Closes #23 (la parte de copy; la de datos historicos ya estaba cubierta por el backend)

El backend ya devuelve la ultima actividad historica por unidad (sin filtro de fecha en `last_activity_by_un` en `admin_legacy.py:612-642`). El frontend la muestra correctamente ordenada y con resumen breve. Pero el copy del header y del bloque "Sin actividad hoy" decia literalmente "del dia", independientemente del rango que el usuario hubiera seleccionado ("Hoy" / "Ayer" / "7 dias" / "Semana pasada" / custom). Eso contradice los datos y confundia al operador cuando seleccionaba un rango donde no habia registros del periodo pero sabia que hubo registros recientes.

## Cambios

`frontend/src/views/HomeView.vue`:
- `headerSubtitle` (computed nuevo): contextualiza segun rol (admin/operador) y `isTodayRange`. Ya no dice "del dia" cuando el rango es mas amplio.
- `rangeLabel`, `isTodayRange` (helpers): dan formato al rango y exponen el boolean.
- `lastRecordEyebrow`, `lastRecordTitle`: el bloque "Ultimo registro" pasa a llamarse "Ultimo registro del periodo (rango)" cuando no estamos en Hoy, y el fallback cambia a "Sin registros en el periodo".
- Bloque dashed "Sin actividad hoy" cambia a "Sin registros en {rango}" cuando corresponde. Titulo cambia a "No hay registros en el periodo seleccionado." si no es Hoy.

## Tests / Validaciones

- [x] `git diff --check`
- [x] `npx vitest run` -> **98/98** tests (sin regresion)
- [x] `npx vite build` -> OK, SW + manifest regenerados

## Comportamiento

| Rango seleccionado | Header (admin) | Bloque "Sin registros" | LastPersonalRecord |
|---|---|---|---|
| Hoy | "Resumen de hoy y accesos de administracion..." | "Sin actividad hoy" / "Todavia no cargaste registros." | "Ultimo registro del dia" / fallback "Sin actividad hoy" |
| Ayer / 7 dias / Semana pasada / custom | "Resumen de <rango> y accesos de administracion..." | "Sin registros en <rango>" / "No hay registros en el periodo seleccionado." | "Ultimo registro del periodo (<rango>)" / "Sin registros en el periodo" |

## Fuera de alcance

- El bloque admin "Ultima actividad registrada" ya estaba bien (orden + resumen). No se toca.
- El filtro del rango ya estaba bien. No se toca.
- Backend no se toca (la query historica ya estaba implementada).

## Riesgos / pendientes

- Si el operador nunca tuvo registros en su vida, el bloque dashed sigue mostrando el copy "Sin registros en <rango>" independientemente del rango. Aceptable.
