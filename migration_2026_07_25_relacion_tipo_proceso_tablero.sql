-- =================================================================
-- Migracion: 2026-07-25
-- Relacion formal tipo_proceso <-> tablero_produccion
--
-- Agrega la columna tipo_proceso_id con FK a tipo_de_proceso(id) en
-- tablero_produccion, y backfilea los registros existentes desde la
-- columna `operacion` (texto) que matchea 1-a-1 con tipo_de_proceso.nombre.
--
-- Patron de idempotencia: INFORMATION_SCHEMA + PREPARE/EXECUTE
-- porque MySQL 8 no soporta `ADD COLUMN IF NOT EXISTS`. El script se
-- puede correr multiples veces sin error.
--
-- Orden de ejecucion en prod (despues del dump):
--   1. Este archivo (migration_2026_07_25_relacion_tipo_proceso_tablero.sql)
--   2. migrations.sql (idempotente, lo cubre la convencion del proyecto)
--
-- Dump pre-migracion: /home/ferreteria/fg_pre_relacion_tipo_proceso_20260725_113225Z.sql
-- =================================================================

-- 0. Validacion previa (solo lectura): muestra cuantos registros matchean
SELECT 'PRE-MIGRACION' AS fase,
       COUNT(*) AS total,
       SUM(CASE WHEN t.operacion IS NOT NULL AND TRIM(t.operacion) != ''
                AND EXISTS (
                  SELECT 1 FROM tipo_de_proceso tp
                  JOIN unidadnegocio_tipo_proceso un
                    ON un.tipo_proceso_id = tp.id AND un.un_id = t.cod_un
                  WHERE UPPER(tp.nombre COLLATE utf8mb4_general_ci)
                      = UPPER(TRIM(t.operacion) COLLATE utf8mb4_general_ci)
                ) THEN 1 ELSE 0 END) AS match_1a1,
       SUM(CASE WHEN t.operacion IS NOT NULL AND TRIM(t.operacion) != ''
                AND UPPER(TRIM(t.operacion) COLLATE utf8mb4_general_ci) IN
                    ('HORAS MAQUINA','ETRACCION','EXTRACION','KM',
                     'EMPUJE PESADO ESPECIAL')
                AND EXISTS (
                  SELECT 1 FROM unidadnegocio_tipo_proceso un
                  WHERE un.un_id = t.cod_un
                    AND un.tipo_proceso_id IN (5, 2, 16, 7)
                ) THEN 1 ELSE 0 END) AS match_typos
FROM tablero_produccion t;

-- 1. Agregar columna tipo_proceso_id (idempotente)
SET @col_exists := (
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'tablero_produccion'
    AND COLUMN_NAME = 'tipo_proceso_id'
);
SET @sql := IF(@col_exists = 0,
  'ALTER TABLE tablero_produccion ADD COLUMN tipo_proceso_id INT UNSIGNED NULL AFTER codigo_tabla',
  'SELECT "columna tipo_proceso_id ya existe, ALTER omitido" AS note'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2. Agregar indice (idempotente)
SET @idx_exists := (
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.STATISTICS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'tablero_produccion'
    AND INDEX_NAME = 'ix_tablero_produccion_tipo_proceso_id'
);
SET @sql := IF(@idx_exists = 0,
  'CREATE INDEX ix_tablero_produccion_tipo_proceso_id ON tablero_produccion (tipo_proceso_id)',
  'SELECT "indice ya existe, CREATE INDEX omitido" AS note'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 3. Agregar foreign key (idempotente)
--    Cambia sql_mode de la sesion para evitar 1292 en fechas 0000-00-00
--    que existen en ~8 registros legacy. Solo afecta esta sesion.
SET @fk_exists := (
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'tablero_produccion'
    AND CONSTRAINT_NAME = 'fk_tablero_produccion_tipo_proceso'
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
);
SET @old_sql_mode := @@SESSION.sql_mode;
SET SESSION sql_mode = '';
SET @sql := IF(@fk_exists = 0,
  'ALTER TABLE tablero_produccion ADD CONSTRAINT fk_tablero_produccion_tipo_proceso FOREIGN KEY (tipo_proceso_id) REFERENCES tipo_de_proceso(id) ON DELETE SET NULL ON UPDATE CASCADE',
  'SELECT "FK ya existe, ADD CONSTRAINT omitido" AS note'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
SET SESSION sql_mode = @old_sql_mode;

-- 4. Backfill match 1-a-1 (operacion == tipo_de_proceso.nombre del catalogo de la UN)
UPDATE tablero_produccion t
JOIN tipo_de_proceso tp
  ON UPPER(tp.nombre COLLATE utf8mb4_general_ci)
   = UPPER(TRIM(t.operacion) COLLATE utf8mb4_general_ci)
JOIN unidadnegocio_tipo_proceso un
  ON un.tipo_proceso_id = tp.id AND un.un_id = t.cod_un
SET t.tipo_proceso_id = tp.id
WHERE t.operacion IS NOT NULL
  AND TRIM(t.operacion) != ''
  AND t.tipo_proceso_id IS NULL
  AND (t.fecha IS NULL OR t.fecha > '1000-01-01');

-- 5. Backfill mapping de typos (Categoria A aprobada)
--    Solo aplica a UNes que tienen el tipo de proceso en su catalogo.
UPDATE tablero_produccion t
JOIN unidadnegocio_tipo_proceso un
  ON un.un_id = t.cod_un
SET t.tipo_proceso_id = CASE
       WHEN UPPER(TRIM(t.operacion) COLLATE utf8mb4_general_ci) = 'HORAS MAQUINA'
            AND un.tipo_proceso_id = 5 THEN 5
       WHEN UPPER(TRIM(t.operacion) COLLATE utf8mb4_general_ci) IN ('ETRACCION','EXTRACION')
            AND un.tipo_proceso_id = 2 THEN 2
       WHEN UPPER(TRIM(t.operacion) COLLATE utf8mb4_general_ci) = 'KM'
            AND un.tipo_proceso_id = 16 THEN 16
       WHEN UPPER(TRIM(t.operacion) COLLATE utf8mb4_general_ci) = 'EMPUJE PESADO ESPECIAL'
            AND un.tipo_proceso_id = 7 THEN 7
     END
WHERE t.tipo_proceso_id IS NULL
  AND t.operacion IS NOT NULL
  AND (t.fecha IS NULL OR t.fecha > '1000-01-01')
  AND UPPER(TRIM(t.operacion) COLLATE utf8mb4_general_ci) IN
      ('HORAS MAQUINA','ETRACCION','EXTRACION','KM','EMPUJE PESADO ESPECIAL');

-- 6. Validacion post-migracion
SELECT 'POST-MIGRACION' AS fase,
       COUNT(*) AS total,
       SUM(CASE WHEN t.tipo_proceso_id IS NOT NULL THEN 1 ELSE 0 END) AS con_tipo_proceso,
       SUM(CASE WHEN t.tipo_proceso_id IS NULL THEN 1 ELSE 0 END) AS sin_tipo_proceso,
       SUM(CASE WHEN t.tipo_proceso_id IS NOT NULL AND t.tabla = 'kobo' THEN 1 ELSE 0 END) AS kobo_backfileados
FROM tablero_produccion t;
