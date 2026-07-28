## Objetivo

Closes #95

Capturar hasta 3 remitos de combustible en el parte de producción. Cuando el operador activa "¿Se cargó combustible?" en el paso 7, el formulario muestra 3 inputs de remito (Remito 1 obligatorio, Remito 2 y 3 opcionales). Al guardar, esos valores se persisten en `tablero_produccion.remito/remito2/remito3` y en el `cargacomb` que se crea como movimiento relacionado, manteniendo consistencia entre ambas tablas.

## Cambios

- **Backend**
  - `backend/app/schemas/produccion.py`: `TableroProduccionCreate` ahora acepta `remito`, `remito2`, `remito3` (str, max 12, default `""`).
  - `backend/app/api/routes/produccion.py`: `create_produccion` persiste los 3 remitos tanto en el `TableroProduccion` como en el `CargaComb` que se crea cuando hay combustible (`Litros > 0`).
- **Backend tests**
  - `backend/tests/test_produccion_combustible_remitos.py` (nuevo, 8 tests): cubre schema, validación de longitud, persistencia en ambas tablas, y el caso sin combustible.
- **Frontend**
  - `frontend/src/components/InputField.vue`: nueva prop opcional `maxlength` que se pasa al `<input>`. Reutilizable.
  - `frontend/src/views/ProduccionFormView.vue`:
    - 3 inputs nuevos visibles solo si `cargoCombustible = true`, agrupados en una grilla 3 columnas en pantallas >= `sm`.
    - Estado `form.remito/remito2/remito3` (default `""`).
    - Reset de los 3 al desactivar el toggle (junto con `form.combustible`).
    - `combustibleValido` exige Remito 1 no vacío si hay combustible y litros > 0.
    - Mensaje de error específico: "ingresá al menos el Remito 1 para poder continuar".
    - Payload del submit incluye los 3 remitos (vacíos si el toggle está apagado).
    - `remitoInvalido` (computed) marca el input con estado de error visual.

## Archivos modificados

- `backend/app/schemas/produccion.py`
- `backend/app/api/routes/produccion.py`
- `backend/tests/test_produccion_combustible_remitos.py` (nuevo)
- `frontend/src/components/InputField.vue`
- `frontend/src/views/ProduccionFormView.vue`

## Tests / Validaciones

- [x] `git diff --check`
- [x] `git diff --cached --check`
- [x] `py -3.12 -m pytest` — 79 tests (8 nuevos para remitos)
- [x] `py -3.12 -m compileall -q backend/app`
- [x] `npm test` — 152 tests
- [x] `npm run build` — bundle generado OK
- [x] Validación visual: pendiente de prueba manual en UI (no hay Computer Use automatizado para esta pantalla todavía)

## Evidencia visual

Pendiente. La validación manual de la pantalla con toggle ON + remito requerido se probará en demo local o en `fasa_195` antes del merge. Sugiero screenshot del paso 7 con:
1. Toggle ON, Remito 1 vacío, litros > 0 → debe bloquear.
2. Toggle ON, Remito 1 cargado → habilita "Siguiente".

## Fuera de alcance

- No tocar la pantalla independiente de Carga de Combustible (`CombustibleFormView.vue`).
- No validar unicidad de remitos entre partes.
- No mostrar remitos en la pantalla de revisión (paso 9) por ahora.
- No se tocan las pantallas de admin.
- No se modifican registros históricos.

## Riesgos / pendientes

- Ningún riesgo funcional: las columnas `remito/remito2/remito3` ya existen en `tablero_produccion` y `cargacomb` desde la estructura legacy (ver `fg_structure.sql` y los modelos en `app/models/produccion.py` y `app/models/carga_comb.py`). El cambio solo completa el wiring que faltaba.
- El bundle principal mantiene el warning existente de 535 KB (preexistente, no introducido por este PR).
- Validación visual final en UI queda pendiente hasta que se ejecute en un entorno con la pantalla accesible.

## Notas

- Complementario al PR #70 (draft) que corrige `tipo_mov="E"` en el `cargacomb` relacionado. Este PR no se pisa con #70: #70 corrige el `tipo_mov` que se persiste, este agrega remitos. Si #70 se mergea primero, este PR sigue funcionando; si se mergea este primero, #70 sigue siendo necesario porque remitos y `tipo_mov` son ortogonales.
