-- Issue #124 (parte 2): normalizar remitos hifenados (formato PPPP-DDDDDDDD).
--
-- Despues de la primera parte de la migracion (LPAD de numericos cortos,
-- archivo 20260805_normalize_remito_lpad.sql) quedaron algunas filas con
-- formato hifenado: "02-1335", "0000002-1335", "0000002-1344". El reporte
-- "Control de combustible" los cuenta como remitos distintos porque el
-- guion no es eliminado.
--
-- Reglas aplicadas (identicas a `app.core.remito.normalize_remito`):
--   * Si el remito tiene exactamente un guion y ambas partes son
--     numericas, se reemplaza por la concatenacion con la primera
--     parte paddeada a 4 digitos y la segunda a 8 digitos.
--   * Ejemplos:
--       "02-1335"     -> "000200001335"
--       "0000002-1335" -> "000200001335"  (mismo remito, otra variante)
--       "99-99999"    -> "009900099999"
--
-- Aplica sobre `cargacomb.remito` y `tablero_produccion.remito`.
-- La migracion es idempotente: solo modifica filas que matchean la
-- condicion y cuyo valor canonicado es distinto del actual.

SET @schema_name = DATABASE();

-- ─── cargacomb.remito: detectar y normalizar hifenados ───────────────────
-- Limpiamos ceros a la izquierda en cada parte antes de validar el ancho
-- (asi "02-1335" y "0000002-1335" se canonical al mismo valor).
UPDATE cargacomb
SET remito = CONCAT(
        LPAD(
          CASE WHEN TRIM(LEADING '0' FROM SUBSTRING_INDEX(remito, '-', 1)) = ''
               THEN '0'
               ELSE TRIM(LEADING '0' FROM SUBSTRING_INDEX(remito, '-', 1))
          END,
          4, '0'
        ),
        LPAD(
          CASE WHEN TRIM(LEADING '0' FROM SUBSTRING_INDEX(remito, '-', -1)) = ''
               THEN '0'
               ELSE TRIM(LEADING '0' FROM SUBSTRING_INDEX(remito, '-', -1))
          END,
          8, '0'
        )
      )
WHERE remito LIKE '%-%'
  AND remito NOT LIKE '%-%-%'  -- exactamente un guion
  AND SUBSTRING_INDEX(remito, '-', 1) REGEXP '^[0-9]+$'
  AND SUBSTRING_INDEX(remito, '-', -1) REGEXP '^[0-9]+$';

-- ─── tablero_produccion.remito: mismo tratamiento ───────────────────────
UPDATE tablero_produccion
SET remito = CONCAT(
        LPAD(
          CASE WHEN TRIM(LEADING '0' FROM SUBSTRING_INDEX(remito, '-', 1)) = ''
               THEN '0'
               ELSE TRIM(LEADING '0' FROM SUBSTRING_INDEX(remito, '-', 1))
          END,
          4, '0'
        ),
        LPAD(
          CASE WHEN TRIM(LEADING '0' FROM SUBSTRING_INDEX(remito, '-', -1)) = ''
               THEN '0'
               ELSE TRIM(LEADING '0' FROM SUBSTRING_INDEX(remito, '-', -1))
          END,
          8, '0'
        )
      )
WHERE remito LIKE '%-%'
  AND remito NOT LIKE '%-%-%'
  AND SUBSTRING_INDEX(remito, '-', 1) REGEXP '^[0-9]+$'
  AND SUBSTRING_INDEX(remito, '-', -1) REGEXP '^[0-9]+$';

-- ─── Verificacion posterior a la migracion ──────────────────────────────
-- Devuelve la cantidad de remitos hifenados numericos que aun quedan
-- (deberia ser 0 si la migracion corrio bien).
SELECT 'cargacomb.remito hifenados restantes' AS chequeo,
       COUNT(*) AS total
FROM cargacomb
WHERE remito LIKE '%-%'
  AND remito NOT LIKE '%-%-%'
  AND SUBSTRING_INDEX(remito, '-', 1) REGEXP '^[0-9]+$'
  AND SUBSTRING_INDEX(remito, '-', -1) REGEXP '^[0-9]+$'
UNION ALL
SELECT 'tablero_produccion.remito hifenados restantes',
       COUNT(*)
FROM tablero_produccion
WHERE remito LIKE '%-%'
  AND remito NOT LIKE '%-%-%'
  AND SUBSTRING_INDEX(remito, '-', 1) REGEXP '^[0-9]+$'
  AND SUBSTRING_INDEX(remito, '-', -1) REGEXP '^[0-9]+$';
