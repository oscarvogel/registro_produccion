# Evidencia fotográfica en el formulario de producción (issue #200)

Capturas reales del paso **Evidencia** del wizard de carga de producción, con
la API mockeada (`frontend/scripts/evidenciaFormCapture.mjs`) y Vite.

## Cómo se generan

```bash
cd frontend
node scripts/evidenciaFormCapture.mjs
```

Salida: `docs/screenshots/evidencia_form/`.

## Qué muestra cada captura

| Archivo | Qué se ve |
|---|---|
| `01-evidencia-paso-<viewport>.png` | El paso "Evidencia" recién llegado: los dos campos de foto vacíos, la casilla de la declaración (D7) y el error "Falta la foto de evidencia". El botón *Siguiente* está deshabilitado. |
| `02-evidencia-con-foto-<viewport>.png` | Con una foto real cargada en "Foto de la pantalla del procesador" (miniatura, *Rehacer foto* y *Quitar). El campo del horómetro sigue pidiendo su foto. |
| `03-evidencia-declaracion-<viewport>.png` | Con la casilla "En esa misma pantalla se ve el horómetro" tildada: el campo del horómetro desaparece (esa sola foto cubre los dos roles) y el botón *Siguiente* se habilita. |

## Resoluciones

| Viewport | Para qué |
|---|---|
| `1638x969` | la pantalla del cliente |
| `1366x768` | notebook de la planta |
| `390x844` | teléfono en la máquina |

En las tres el script mide el desborde horizontal del contenido y lo informa
por consola. La última corrida dio **0 px** de desborde en las tres.

## Datos de la captura

- Tipo de proceso `PROCESO`: exige foto del horómetro **y** de la pantalla del
  procesador (configuración inicial de la decisión D8).
- La foto cargada es un PNG real del repo (`01-admin-tipos-lista-1638x969.png`),
  comprimido por el navegador a JPEG (lado mayor 1600 px) como hace el
  formulario real.
- Lecturas de horómetro de la captura: 1200 → 1850.
