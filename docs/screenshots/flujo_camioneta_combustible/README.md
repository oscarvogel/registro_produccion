# Flujo camioneta: combustible y KM por parte de producción

Evidencia visual de la validación punta a punta (2026-10-14) de que una camioneta
carga **combustible + KM** desde el parte de producción, sin cambios de código:
solo configuración (tipo de proceso habilitado para la UN).

Navegador: Microsoft Edge (headless) vía Playwright. Backend local
(`127.0.0.1:8000`, base demo local `registro_demo` en WSL MariaDB) + frontend
Vite (`127.0.0.1:5174`).

## Configuración (rol administrador)

| Captura | Qué muestra |
|---|---|
| `01-admin-tipos-proceso-lista-inicial.png` | Admin demo en Administración → Tipos de Proceso |
| `02-admin-tipos-proceso-form.png` | Modal "Nuevo tipo de proceso" con nombre "Camioneta Demo" |
| `02b-admin-tipos-proceso-form-completo.png` | Pestaña Relaciones con la UN demo habilitada |
| `03-admin-tipos-proceso-creado.png` | Listado con "Camioneta Demo" creado |

## Parte de producción (rol operador)

| Captura | Qué muestra |
|---|---|
| `04-parte-contexto-un.png` | Paso 1 Contexto: UN precargada de la asignación |
| `05-parte-operador.png` | Paso 2 Operador: bloqueado al usuario logueado |
| `06-parte-equipo.png` | Paso 3 Equipo: movil seleccionado desde asignaciones |
| `07-parte-proceso.png` | Paso 4 Proceso: "Camioneta Demo" elegido |
| `08-parte-tiempo.png` | Paso 5 Tiempo: horómetro inicial/final |
| `09-parte-produccion-sin-campos.png` | Paso 6 Producción sin campos definidos (válido) |
| `10-parte-combustible.png` | Paso 7 Consumos: toggle activado, 45 L, KM 125000, remito |
| `11-parte-ubicacion.png` | Paso 8 Ubicación: lugar de carga + observaciones |
| `12-parte-revision.png` | Paso 9 Revisión y confirmación |
| `13-parte-guardado.png` | "Registro guardado" — 9/9 pasos validados |
| `14-mis-registros.png` | Mis Registros: "CAMIONETA DEMO 14/10/2026 — 45 lts" |

El reporte completo con verificación en base, idempotencia y hallazgos está en
[`docs/FLUJO_CAMIONETA_COMBUSTIBLE_VISUAL_REVIEW.md](../../FLUJO_CAMIONETA_COMBUSTIBLE_VISUAL_REVIEW.md).
