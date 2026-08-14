-- =================================================================
-- Migracion: 2026-08-14 - Issue #126
-- Partes multi-proceso para la UN Caminos
-- =================================================================

-- 1. Nueva metrica de remolque en tablero_produccion (idempotente)
SET @col_exists := (
  SELECT COUNT(*)
  FROM INFORMATION_SCHEMA.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'tablero_produccion'
    AND COLUMN_NAME = 'hr_remolque'
);
SET @sql := IF(
  @col_exists = 0,
  'ALTER TABLE tablero_produccion ADD COLUMN hr_remolque DECIMAL(12,2) NOT NULL DEFAULT 0 AFTER hr_disposicion',
  'SELECT "columna hr_remolque ya existe, ALTER omitido" AS note'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2. Asegurar la UN Caminos. No se fuerza un ID concreto.
INSERT INTO unidadnegocio (Nombre, Prefijo, codigo_kobo, activo)
SELECT 'Caminos', 'CAM', '', 1
WHERE NOT EXISTS (
  SELECT 1 FROM unidadnegocio WHERE LOWER(TRIM(Nombre)) = 'caminos'
);

UPDATE unidadnegocio
SET activo = 1
WHERE LOWER(TRIM(Nombre)) = 'caminos';

SET @caminos_un_id := (
  SELECT idUnidadNegocio
  FROM unidadnegocio
  WHERE LOWER(TRIM(Nombre)) = 'caminos'
  ORDER BY idUnidadNegocio
  LIMIT 1
);

-- 3. Catálogo mínimo inicial de procesos de Caminos.
-- PERFILADO puede existir por migraciones anteriores; en ese caso se reutiliza.
INSERT INTO tipo_de_proceso
  (nombre, campos, requiere_acta, requiere_predio, requiere_rodal, activo)
SELECT 'PERFILADO', 'km_perfilado', 1, 1, 1, 1
WHERE NOT EXISTS (
  SELECT 1 FROM tipo_de_proceso WHERE UPPER(TRIM(nombre)) = 'PERFILADO'
);

INSERT INTO tipo_de_proceso
  (nombre, campos, requiere_acta, requiere_predio, requiere_rodal, activo)
SELECT 'DISPOSICION', 'hr_disposicion', 0, 1, 0, 1
WHERE NOT EXISTS (
  SELECT 1 FROM tipo_de_proceso WHERE UPPER(TRIM(nombre)) = 'DISPOSICION'
);

INSERT INTO tipo_de_proceso
  (nombre, campos, requiere_acta, requiere_predio, requiere_rodal, activo)
SELECT 'REMOLQUE', 'hr_remolque', 0, 1, 0, 1
WHERE NOT EXISTS (
  SELECT 1 FROM tipo_de_proceso WHERE UPPER(TRIM(nombre)) = 'REMOLQUE'
);

-- Ajustar requisitos del primer corte de Caminos aun si los tipos ya existian.
UPDATE tipo_de_proceso
SET campos = 'km_perfilado',
    requiere_predio = 1,
    requiere_acta = 1,
    requiere_rodal = 1,
    activo = 1
WHERE UPPER(TRIM(nombre)) = 'PERFILADO';

UPDATE tipo_de_proceso
SET campos = 'hr_disposicion',
    requiere_predio = 1,
    requiere_acta = 0,
    requiere_rodal = 0,
    activo = 1
WHERE UPPER(TRIM(nombre)) = 'DISPOSICION';

UPDATE tipo_de_proceso
SET campos = 'hr_remolque',
    requiere_predio = 1,
    requiere_acta = 0,
    requiere_rodal = 0,
    activo = 1
WHERE UPPER(TRIM(nombre)) = 'REMOLQUE';

-- 4. Habilitar esos procesos para Caminos.
INSERT IGNORE INTO unidadnegocio_tipo_proceso (un_id, tipo_proceso_id)
SELECT @caminos_un_id, id
FROM tipo_de_proceso
WHERE UPPER(TRIM(nombre)) IN ('PERFILADO', 'DISPOSICION', 'REMOLQUE');

-- 5. KPI opcional para remolque, si las tablas KPI ya existen.
SET @kpi_table_exists := (
  SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
  WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'kpi_definicion'
);
SET @sql := IF(
  @kpi_table_exists > 0,
  "INSERT INTO kpi_definicion (nombre, campo_origen, agregacion, unidad, icono, descripcion, activo) SELECT 'Horas Remolque', 'hr_remolque', 'SUM', 'hs', 'truck', 'Horas de remolque acumuladas', 1 WHERE NOT EXISTS (SELECT 1 FROM kpi_definicion WHERE campo_origen = 'hr_remolque')",
  'SELECT "tabla kpi_definicion no existe, seed KPI omitido" AS note'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

COMMIT;

SELECT @caminos_un_id AS caminos_un_id,
       (SELECT COUNT(*) FROM unidadnegocio_tipo_proceso WHERE un_id = @caminos_un_id) AS procesos_habilitados;
