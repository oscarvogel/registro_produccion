# Capturas — Evidencia de horas y producción (issue #194)

Evidencia visual de los **flags de exigencia de evidencia fotográfica** agregados al
Admin de Tipos de Proceso.

## Qué se ve

- **01-admin-tipos-lista-*.png** — la grilla de *Tipos de Proceso* con la columna
  nueva **Evidencia**, que resume en un solo valor qué fotos exige cada proceso:
  `Ambas`, `Horómetro`, `Procesador` o `—` (no exige ninguna).
- **02-admin-requisitos-evidencia-*.png** — el formulario de tipo de proceso, en la
  pestaña **Requisitos**, con los dos checkboxes nuevos:
  *Requiere Foto Horómetro* y *Requiere Foto Procesador*.

## Resoluciones

Se capturó en las tres resoluciones que pide la sección 11 de `AGENTS.md`:

| Archivo | Resolución | Uso |
|---|---|---|
| `*-1638x969.png` | 1638x969 | pantalla del cliente |
| `*-1366x768.png` | 1366x768 | pantalla chica |
| `*-390x844.png` | 390x844 | celular |

En 390x844 la pantalla no usa grilla sino tarjetas, por eso la columna se ve como
pares etiqueta/valor dentro de la tarjeta.

## Cómo se generan

```bash
cd frontend
node scripts/evidenciaAdminCapture.mjs
```

El script levanta Vite, intercepta `**/api/**` con la API mockeada (mismos datos
que la base real: los tipos de proceso de producción están vinculados a la UN 144
"Caminos") y deja las capturas en esta carpeta.

Para capturar contra una aplicación real:

```bash
EVIDENCIA_CAPTURE_BASE_URL=http://127.0.0.1:5174 node scripts/evidenciaAdminCapture.mjs
```

## Ancho de la grilla

El script mide el desborde horizontal de la grilla y lo imprime:

```text
[evidencia] 1638x969: visible=1302px necesario=1302px desborde=0px
[evidencia] 1366x768: visible=1030px necesario=1067px desborde=37px
```

La grilla de tipos de proceso entra **justa** en 1366px (sin margen). Por eso la
evidencia se muestra en **una sola columna** y no en dos: con dos columnas el
desborde llegaba a 208px y la columna de acciones quedaba completamente fuera de
pantalla. Ver `docs/EVIDENCIA_ADMIN_VISUAL_REVIEW.md`.
