# Evidencia visual de la documentación (issue #208)

Capturas de la revisión visual de los manuales de usuario con la evidencia
fotográfica. El detalle está en
[`docs/EVIDENCIA_DOCUMENTACION_VISUAL_REVIEW.md`](../../EVIDENCIA_DOCUMENTACION_VISUAL_REVIEW.md).

## Qué hay acá

| Archivo | Qué muestra |
|---|---|
| `manuales-view-1638x969.png` | Vista de *Manuales* de la app, en escritorio (1638x969). |
| `manuales-view-1638x969-scroll.png` | La misma vista con las capturas del manual cargadas. |
| `manuales-view-390x844.png` | La misma vista en el teléfono (390x844). |
| `pdf/01-operador-paso-evidencia-p18.png` | PDF del operador: el paso 7 *Evidencia Fotográfica*. |
| `pdf/02-operador-offline-foto-antes-del-parte-p26.png` | PDF del operador: *La foto viaja antes que el parte*. |
| `pdf/03-encargado-filtro-evidencia-p20.png` | PDF del encargado: el filtro de evidencia del listado. |
| `pdf/04-encargado-seccion-evidencia-p21.png` | PDF del encargado: la sección de evidencia y el aviso por WhatsApp. |
| `pdf/05-admin-flags-de-foto-p10.png` | PDF del admin: los flags de foto por tipo de proceso. |

## Cómo se generaron

- Las de la app: `cd frontend && node scripts/manualesViewCapture.mjs` (Vite
  real + Chromium, con la API interceptada).
- Las del PDF: `cd frontend && npm run docs:pdf` y después el render de las
  páginas con `pypdfium2`.

Los datos de la app son ficticios (los del modo mock de la documentación). No
se usó la base de datos de producción.
