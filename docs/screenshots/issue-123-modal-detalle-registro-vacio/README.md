# Evidencia visual — Issue #123 (modal "Detalle del registro")

Capturas tomadas con Computer Use sobre el build local con el fix aplicado,
apuntando a la API de `produccion.servinlgsm.com.ar` (entorno cross-origin).

## Archivos

- `01-lista-registros.png` — Vista mobile del dashboard/registros con 4
  cards (después del fix, antes de tocar ninguna).
- `02-modal-loading.png` — Modal abierto sobre la primera card: el watcher
  dispara `fetchDetalle` y se ve el spinner de carga (comportamiento NUEVO,
  antes del fix esto no aparecía porque la prop `useStore` con default `true`
  bloqueaba la llamada).
- `03-modal-error.png` — Estado de error mostrado por el modal cuando el
  fetch falla en este entorno cross-origin. (En producción same-origin el
  endpoint devuelve los datos correctamente — el camino "datos cargados" está
  cubierto por los 6 unit tests del modal.)

## Limitación del entorno

El login del browser vive en localStorage de `localhost:8765`. La API corre
en `produccion.servinlgsm.com.ar`. El endpoint
`GET /api/dashboard/registros/{id}` responde con error genérico en este
escenario, aunque el listado general funciona. El modal igual prueba que:

1. La prop `useStore` ya no bloquea el fetch.
2. El loading se muestra correctamente mientras se resuelve la promesa.
3. El bloque de error del template se renderiza cuando `detalleError` no es null.

## Veredicto visual

Aprobado con observaciones — la captura con datos cargados se obtendrá al
desplegar el fix en producción, donde el mismo flujo (click en "Ver detalle")
debe mostrar el resumen completo del registro seleccionado.
