-- Issue #105: idempotencia explicita para cada egreso de combustible.
--
-- Los movimientos historicos quedan con form_uuid NULL. Los nuevos registros
-- creados desde Produccion o desde Carga de Combustible reciben una identidad
-- por formulario. La unicidad se limita al operador para aceptar dos cargas
-- reales con los mismos movil, fecha y litros cuando sus identidades difieren.

SET @schema_name = DATABASE();

SET @column_exists = (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = @schema_name
    AND TABLE_NAME = 'cargacomb'
    AND COLUMN_NAME = 'form_uuid'
);

SET @add_column_sql = IF(
  @column_exists = 0,
  'ALTER TABLE cargacomb ADD COLUMN form_uuid VARCHAR(36) NULL',
  'SELECT 1'
);
PREPARE add_column_stmt FROM @add_column_sql;
EXECUTE add_column_stmt;
DEALLOCATE PREPARE add_column_stmt;

SET @index_exists = (
  SELECT COUNT(*)
  FROM information_schema.STATISTICS
  WHERE TABLE_SCHEMA = @schema_name
    AND TABLE_NAME = 'cargacomb'
    AND INDEX_NAME = 'uq_cargacomb_personal_form_uuid'
);

SET @add_index_sql = IF(
  @index_exists = 0,
  'CREATE UNIQUE INDEX uq_cargacomb_personal_form_uuid ON cargacomb (personal, form_uuid)',
  'SELECT 1'
);
PREPARE add_index_stmt FROM @add_index_sql;
EXECUTE add_index_stmt;
DEALLOCATE PREPARE add_index_stmt;
