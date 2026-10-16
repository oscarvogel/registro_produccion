# Camioneta: KM y combustible sin horómetro

Evidencia visual (2026-10-16) del flujo donde una camioneta registra
**combustible y KM** desde el parte de producción **sin cargar horómetro**.

Capturas generadas con la API mockeada y Vite (`frontend/scripts/camionetaCapture.mjs`),
navegador Chromium headless vía Playwright, viewport desktop (1440x900).

## Configuración (rol administrador)

| Captura | Qué muestra |
|---|---|
| `11-admin-tipos-lista.png` | Listado de Tipos de Proceso con la columna **Horómetro = No** |
| `12-admin-tipo-principal.png` | Modal "Nuevo tipo de proceso", pestaña Principal |
| `13-admin-tipo-requisitos.png` | Pestaña Requisitos con **Requiere Horómetro desmarcado** |

## Parte de producción (rol operador)

El wizard queda en **8 pasos** (no aparece "Tiempo"):

| Captura | Qué muestra |
|---|---|
| `01-parte-contexto.png` | Paso 1 de 8: Contexto |
| `02-parte-operador.png` | Paso 2 de 8: Operador |
| `03-parte-equipo.png` | Paso 3 de 8: Equipo (la camioneta) |
| `04-parte-proceso.png` | Paso 4 de 8: Proceso "Camioneta Demo" |
| `05-parte-produccion-sin-campos.png` | Paso 5 de 8: Producción sin campos |
| `06-parte-combustible.png` | Paso 6 de 8: Consumos — 45 L, KM 125000, remito |
| `07-parte-ubicacion.png` | Paso 7 de 8: Lugar de carga |
| `08-parte-revision.png` | Paso 8 de 8: Revisión (sin fila de Horómetros) |
| `09-parte-guardado.png` | Confirmación "Registro guardado" |
| `10-mis-registros.png` | Mis Registros: "CAMIONETA DEMO — 45 lts" |

El reporte completo está en
[`docs/CAMIONETA_KM_COMBUSTIBLE_VISUAL_REVIEW.md`](../../CAMIONETA_KM_COMBUSTIBLE_VISUAL_REVIEW.md).
