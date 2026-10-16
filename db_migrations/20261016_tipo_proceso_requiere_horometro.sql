-- =================================================================
-- Migracion: 2026-10-16 - Camioneta sin horometro
-- Agrega el flag requiere_horometro a tipo_de_proceso.
-- Idempotente: se puede ejecutar en cada deploy.
--
-- requiere_horometro = 1 (default) mantiene el comportamiento historico:
-- el parte pide horometro inicial/final. Los procesos que no usan horometro
-- (por ejemplo una camioneta, que solo carga combustible y KM) se marcan en 0
-- para que el formulario de produccion omita el paso "Control de Tiempo".
-- =================================================================

SET @schema_name = DATABASE();

SET @column_exists := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = @schema_name
    AND TABLE_NAME = 'tipo_de_proceso'
    AND COLUMN_NAME = 'requiere_horometro'
);

SET @add_column_sql := IF(
  @column_exists = 0,
  'ALTER TABLE tipo_de_proceso ADD COLUMN requiere_horometro TINYINT(1) NOT NULL DEFAULT 1 AFTER requiere_rodal',
  'SELECT "columna requiere_horometro ya existe, ALTER omitido" AS note'
);
PREPARE add_column_stmt FROM @add_column_sql;
EXECUTE add_column_stmt;
DEALLOCATE PREPARE add_column_stmt;

-- Los procesos existentes conservan el horometro (default 1); no se fuerza
-- ninguno a 0. La configuracion de cada proceso sin horometro es manual.

COMMIT;
