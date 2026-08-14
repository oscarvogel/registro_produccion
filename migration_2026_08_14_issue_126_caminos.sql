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

-- 3. Catalogo minimo inicial de procesos de Caminos.
-- IMPORTANTE: tipo_de_proceso es global. Si ya existe un proceso activo con
-- el mismo nombre se reutiliza SIN cambiar campos ni flags, para no alterar
-- el comportamiento de Forestal u otras UN. Las reglas especiales de
-- ubicacion de Caminos se validan en el endpoint /produccion/caminos.
INSERT INTO tipo_de_proceso
  (nombre, campos, requiere_acta, requiere_predio, requiere_rodal, activo)
SELECT 'PERFILADO', 'km_perfilado', 1, 1, 1, 1
WHERE NOT EXISTS (
  SELECT 1
  FROM tipo_de_proceso
  WHERE UPPER(TRIM(nombre)) = 'PERFILADO' AND activo = 1
);

INSERT INTO tipo_de_proceso
  (nombre, campos, requiere_acta, requiere_predio, requiere_rodal, activo)
SELECT 'DISPOSICION', 'hr_disposicion', 0, 1, 0, 1
WHERE NOT EXISTS (
  SELECT 1
  FROM tipo_de_proceso
  WHERE UPPER(TRIM(nombre)) = 'DISPOSICION' AND activo = 1
);

INSERT INTO tipo_de_proceso
  (nombre, campos, requiere_acta, requiere_predio, requiere_rodal, activo)
SELECT 'REMOLQUE', 'hr_remolque', 0, 1, 0, 1
WHERE NOT EXISTS (
  SELECT 1
  FROM tipo_de_proceso
  WHERE UPPER(TRIM(nombre)) = 'REMOLQUE' AND activo = 1
);

-- 4. Habilitar exactamente una version activa de cada proceso para Caminos.
INSERT IGNORE INTO unidadnegocio_tipo_proceso (un_id, tipo_proceso_id)
SELECT @caminos_un_id, MIN(id)
FROM tipo_de_proceso
WHERE activo = 1
  AND UPPER(TRIM(nombre)) IN ('PERFILADO', 'DISPOSICION', 'REMOLQUE')
GROUP BY UPPER(TRIM(nombre));

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
