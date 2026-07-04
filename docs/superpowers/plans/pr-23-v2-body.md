## Objetivo

Sigue sobre la issue #23. El PR #60 (https://github.com/oscarvogel/registro_produccion/pull/60) arreglo el header y el bloque dashed de la Home, pero quedaron hardcoded "Produccion hoy" y "Cargas del dia" en las cards de resumen del operador. Eso seguia mintiendo cuando el rango no era Hoy.

## Cambios

`frontend/src/views/HomeView.vue`:
- `rangeShortLabel` (computed helper): mapea `selectedDatePreset` a `"hoy"` / `"ayer"` / `"ultimos 7 dias"` / `"semana pasada"` / `"este periodo"` (para custom).
- `rangeLongLabel`: para rango custom devuelve `"del {rango}"`.
- `operatorSummaryCards`: las cards ahora usan el rango:
  - `"Produccion"` con detail `"{metrica} ({rango})"`
  - `"Registros"` con detail `"Cargas {rango}"`
  - Sin hardcodear "hoy" ni "dia".
- `adminSummaryCards` ya estaba correcto (decia "total periodo", "Cargas del sistema"), no se toca.

## Tests / Validaciones

- [x] `git diff --check`
- [x] `npx vitest run` -> **98/98** tests (sin regresion)
- [x] `npx vite build` -> OK, SW + manifest regenerados

## Comportamiento

| Rango | label `Produccion` | detail `Registros` |
|---|---|---|
| Hoy | "Produccion" | "Cargas hoy" |
| Ayer | "Produccion" | "Cargas ayer" |
| 7 dias | "Produccion" | "Cargas ultimos 7 dias" |
| Semana pasada | "Produccion" | "Cargas semana pasada" |
| Custom (rango arbitrario) | "Produccion" | "Cargas este periodo" |

(El detail de Produccion es la metrica puntual + "({rango})", por ejemplo "TN (ayer)".)

## Fuera de alcance

- adminSummaryCards ya estaba bien, no se toca.
- El bloque admin de unidades ya estaba bien, no se toca.
- El operador de admin usa los mismos cards. Si querés que el admin tambien vea cards mas descriptivas, lo hacemos en PR aparte.
