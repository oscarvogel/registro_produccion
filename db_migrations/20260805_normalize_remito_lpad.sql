-- Issue #124: normalizar el remito de combustible al formato canonico.
--
-- En produccion conviven dos formatos para el mismo comprobante ("011278" y
-- "000000011278", "1" y "000000000001") y eso hace que el reporte "Control de
-- combustible" muestre la misma carga dos veces.
--
-- Reglas aplicadas a los registros existentes (identicas al helper
-- `app.core.remito.normalize_remito` del backend):
--   * Si el remito es puramente numerico, se paddea a 12 digitos con ceros
--     a la izquierda.
--   * Si el remito es alfanumerico (contiene letras o guion), se conserva
--     tal cual, en mayusculas.
--   * Si el remito ya esta en formato canonico, no se modifica.
--
-- Aplica sobre `cargacomb.remito/remito2/remito3` y
-- `tablero_produccion.remito/remito2/remito3`. La migracion es idempotente
-- (UPDATE solo toca las filas que no estan en formato canonico) y no toca
-- los remitos de bitren / proveedor / fgpy porque esos viven en columnas
-- VARCHAR(20) y no son los afectados por el issue.

SET @schema_name = DATABASE();

-- ─── cargacomb.remito ────────────────────────────────────────────────────
UPDATE cargacomb
SET remito = LPAD(remito, 12, '0')
WHERE remito REGEXP '^[0-9]+$'
  AND CHAR_LENGTH(remito) < 12;

-- ─── cargacomb.remito2 ───────────────────────────────────────────────────
UPDATE cargacomb
SET remito2 = LPAD(remito2, 12, '0')
WHERE remito2 IS NOT NULL
  AND remito2 REGEXP '^[0-9]+$'
  AND CHAR_LENGTH(remito2) < 12;

-- ─── cargacomb.remito3 ───────────────────────────────────────────────────
UPDATE cargacomb
SET remito3 = LPAD(remito3, 12, '0')
WHERE remito3 IS NOT NULL
  AND remito3 REGEXP '^[0-9]+$'
  AND CHAR_LENGTH(remito3) < 12;

-- ─── tablero_produccion.remito ───────────────────────────────────────────
UPDATE tablero_produccion
SET remito = LPAD(remito, 12, '0')
WHERE remito REGEXP '^[0-9]+$'
  AND CHAR_LENGTH(remito) < 12;

-- ─── tablero_produccion.remito2 ──────────────────────────────────────────
UPDATE tablero_produccion
SET remito2 = LPAD(remito2, 12, '0')
WHERE remito2 IS NOT NULL
  AND remito2 REGEXP '^[0-9]+$'
  AND CHAR_LENGTH(remito2) < 12;

-- ─── tablero_produccion.remito3 ──────────────────────────────────────────
UPDATE tablero_produccion
SET remito3 = LPAD(remito3, 12, '0')
WHERE remito3 IS NOT NULL
  AND remito3 REGEXP '^[0-9]+$'
  AND CHAR_LENGTH(remito3) < 12;

-- ─── Verificacion posterior a la migracion ──────────────────────────────
-- Devuelve la cantidad de cargas que aun tienen remitos en formato corto
-- (deberia ser 0 si la migracion corrio bien).
SELECT 'cargacomb.remito cortos restantes' AS chequeo,
       COUNT(*) AS total
FROM cargacomb
WHERE remito REGEXP '^[0-9]+$' AND CHAR_LENGTH(remito) < 12
UNION ALL
SELECT 'tablero_produccion.remito cortos restantes',
       COUNT(*)
FROM tablero_produccion
WHERE remito REGEXP '^[0-9]+$' AND CHAR_LENGTH(remito) < 12;
