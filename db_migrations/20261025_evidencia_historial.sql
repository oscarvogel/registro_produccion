-- =================================================================
-- Migracion: 2026-10-25 - Evidencia: historial y autor de la carga
--
-- Issue #198 (API de evidencia). Dos cambios sobre la tabla
-- `produccion_evidencia` que creo la migracion 20261024:
--
-- 1. `cargado_por_id`: el nombre de quien subio la foto no es univoco, y
--    los permisos (ver la foto) se deciden por id, no por texto.
--
-- 2. `uq_evidencia_form_tipo` (UNIQUE) pasa a ser `idx_evidencia_form_tipo`
--    (indice normal). Con D-F puede haber MAS DE UNA fila por
--    `(form_uuid, tipo)`: la foto rechazada queda como historial del intento
--    y la foto nueva la reemplaza para cubrir el rol. La unicidad real la
--    garantiza la aplicacion: una sola evidencia VIVA por `(form_uuid, tipo)`.
--
-- Idempotente: backend/app/migrate.py aplica TODOS los .sql de este
-- directorio en cada deploy, sin registro de migraciones aplicadas.
-- =================================================================

SET @schema_name = DATABASE();

-- -----------------------------------------------------------------
-- 0. La tabla tiene que existir (la crea 20261024_evidencia_produccion.sql,
--    que corre antes por orden alfabetico).
-- -----------------------------------------------------------------
SET @tabla_existe := (
  SELECT COUNT(*)
  FROM information_schema.TABLES
  WHERE TABLE_SCHEMA = @schema_name
    AND TABLE_NAME = 'produccion_evidencia'
);

-- -----------------------------------------------------------------
-- 1. Columna `cargado_por_id`
-- -----------------------------------------------------------------
SET @col_cargado_por_id := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = @schema_name
    AND TABLE_NAME = 'produccion_evidencia'
    AND COLUMN_NAME = 'cargado_por_id'
);

SET @sql_cargado_por_id := IF(
  @tabla_existe = 0,
  'SELECT "produccion_evidencia no existe, columna omitida" AS note',
  IF(
    @col_cargado_por_id = 0,
    'ALTER TABLE produccion_evidencia ADD COLUMN cargado_por_id INT NULL DEFAULT NULL AFTER cargado_por',
    'SELECT "columna cargado_por_id ya existe, ALTER omitido" AS note'
  )
);
PREPARE stmt_cargado_por_id FROM @sql_cargado_por_id;
EXECUTE stmt_cargado_por_id;
DEALLOCATE PREPARE stmt_cargado_por_id;

-- -----------------------------------------------------------------
-- 2. Indice sobre `cargado_por_id`
-- -----------------------------------------------------------------
SET @idx_cargado_por_id := (
  SELECT COUNT(*)
  FROM information_schema.STATISTICS
  WHERE TABLE_SCHEMA = @schema_name
    AND TABLE_NAME = 'produccion_evidencia'
    AND INDEX_NAME = 'ix_produccion_evidencia_cargado_por_id'
);

SET @sql_idx_cargado_por_id := IF(
  @tabla_existe = 0,
  'SELECT "produccion_evidencia no existe, indice omitido" AS note',
  IF(
    @idx_cargado_por_id = 0,
    'ALTER TABLE produccion_evidencia ADD INDEX ix_produccion_evidencia_cargado_por_id (cargado_por_id)',
    'SELECT "indice de cargado_por_id ya existe, ALTER omitido" AS note'
  )
);
PREPARE stmt_idx_cargado_por_id FROM @sql_idx_cargado_por_id;
EXECUTE stmt_idx_cargado_por_id;
DEALLOCATE PREPARE stmt_idx_cargado_por_id;

-- -----------------------------------------------------------------
-- 3. El indice UNIQUE pasa a ser un indice normal
--
-- `information_schema.STATISTICS` tiene una fila por columna del indice, asi
-- que COUNT(*) > 0 significa "el indice existe".
-- -----------------------------------------------------------------
SET @idx_unico := (
  SELECT COUNT(*)
  FROM information_schema.STATISTICS
  WHERE TABLE_SCHEMA = @schema_name
    AND TABLE_NAME = 'produccion_evidencia'
    AND INDEX_NAME = 'uq_evidencia_form_tipo'
);

SET @sql_drop_unico := IF(
  @tabla_existe = 0 OR @idx_unico = 0,
  'SELECT "no existe el indice unico uq_evidencia_form_tipo, DROP omitido" AS note',
  'ALTER TABLE produccion_evidencia DROP INDEX uq_evidencia_form_tipo'
);
PREPARE stmt_drop_unico FROM @sql_drop_unico;
EXECUTE stmt_drop_unico;
DEALLOCATE PREPARE stmt_drop_unico;

SET @idx_normal := (
  SELECT COUNT(*)
  FROM information_schema.STATISTICS
  WHERE TABLE_SCHEMA = @schema_name
    AND TABLE_NAME = 'produccion_evidencia'
    AND INDEX_NAME = 'idx_evidencia_form_tipo'
);

SET @sql_idx_normal := IF(
  @tabla_existe = 0,
  'SELECT "produccion_evidencia no existe, indice omitido" AS note',
  IF(
    @idx_normal = 0,
    'ALTER TABLE produccion_evidencia ADD INDEX idx_evidencia_form_tipo (form_uuid, tipo)',
    'SELECT "indice idx_evidencia_form_tipo ya existe, ALTER omitido" AS note'
  )
);
PREPARE stmt_idx_normal FROM @sql_idx_normal;
EXECUTE stmt_idx_normal;
DEALLOCATE PREPARE stmt_idx_normal;

COMMIT;
