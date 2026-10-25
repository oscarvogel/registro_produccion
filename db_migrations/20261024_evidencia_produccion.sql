-- =================================================================
-- Migracion: 2026-10-24 - Evidencia de horas y produccion (issue #194)
--
-- Agrega a tipo_de_proceso los flags de exigencia de evidencia y crea la
-- tabla produccion_evidencia (la foto, su rol y su estado de verificacion).
--
-- Idempotente: backend/app/migrate.py aplica TODOS los .sql de este
-- directorio en cada deploy, sin registro de migraciones aplicadas. Por eso
-- esta migracion se puede correr N veces sin romper nada.
--
-- Los flags usan NULL como centinela de "sin configurar":
--
--   NULL = sin configurar  -> la API lo expone como False (no exige evidencia)
--   0    = configurado, no exige evidencia
--   1    = configurado, exige evidencia
--
-- La configuracion inicial (punto 4) solo toca filas cuyo flag esta en NULL.
-- Asi un deploy posterior NO pisa lo que el administrador haya cambiado en
-- Admin: es el unico jeito de que un UPDATE en una migracion idempotente
-- no rompa la configuracion.
--
-- OJO: requiere_horometro (que ya existia) es OTRO concepto: define si el
-- parte pide horometro inicial/final (el paso "Control de Tiempo" del
-- formulario). Este NO es el flag de evidencia.
-- =================================================================

SET @schema_name = DATABASE();

-- -----------------------------------------------------------------
-- 1. Flag: exige foto del horometro
-- -----------------------------------------------------------------
SET @col_foto_horometro := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = @schema_name
    AND TABLE_NAME = 'tipo_de_proceso'
    AND COLUMN_NAME = 'requiere_foto_horometro'
);

SET @sql_foto_horometro := IF(
  @col_foto_horometro = 0,
  'ALTER TABLE tipo_de_proceso ADD COLUMN requiere_foto_horometro TINYINT(1) NULL DEFAULT NULL AFTER requiere_horometro',
  'SELECT "columna requiere_foto_horometro ya existe, ALTER omitido" AS note'
);
PREPARE stmt_foto_horometro FROM @sql_foto_horometro;
EXECUTE stmt_foto_horometro;
DEALLOCATE PREPARE stmt_foto_horometro;

-- -----------------------------------------------------------------
-- 2. Flag: exige foto de la pantalla del procesador
-- -----------------------------------------------------------------
SET @col_foto_procesador := (
  SELECT COUNT(*)
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = @schema_name
    AND TABLE_NAME = 'tipo_de_proceso'
    AND COLUMN_NAME = 'requiere_foto_procesador'
);

SET @sql_foto_procesador := IF(
  @col_foto_procesador = 0,
  'ALTER TABLE tipo_de_proceso ADD COLUMN requiere_foto_procesador TINYINT(1) NULL DEFAULT NULL AFTER requiere_foto_horometro',
  'SELECT "columna requiere_foto_procesador ya existe, ALTER omitido" AS note'
);
PREPARE stmt_foto_procesador FROM @sql_foto_procesador;
EXECUTE stmt_foto_procesador;
DEALLOCATE PREPARE stmt_foto_procesador;

-- -----------------------------------------------------------------
-- 3. Tabla de evidencia
--
-- Una fila es una foto. `tipo` es el rol principal de la foto
-- ('procesador' u 'horometro') y `incluye_horometro` cubre el caso de D7:
-- cuando el operador declara que el horometro se ve en la misma pantalla
-- del procesador, esa sola foto cubre los dos roles.
--
-- `form_uuid` es el vinculo estable con el formulario: permite subir la
-- foto ANTES de que exista el registro de produccion (modo offline) y
-- deduplica los reintentos. `registro_id` se completa al crear el registro.
--
-- UNIQUE (form_uuid, tipo): como maximo una foto de procesador y una de
-- horometro por formulario.
-- -----------------------------------------------------------------
CREATE TABLE IF NOT EXISTS produccion_evidencia (
  id                INT NOT NULL AUTO_INCREMENT,
  registro_id       INT NULL,
  form_uuid         VARCHAR(36) NOT NULL,
  tipo              VARCHAR(20) NOT NULL,
  incluye_horometro TINYINT(1) NOT NULL DEFAULT 0,
  archivo           VARCHAR(255) NOT NULL,
  mime              VARCHAR(100) NOT NULL DEFAULT '',
  tamano            INT NOT NULL DEFAULT 0,
  hash_sha256       VARCHAR(64) NOT NULL DEFAULT '',
  estado            SMALLINT NOT NULL DEFAULT 0,
  cargado_por       VARCHAR(80) NOT NULL DEFAULT '',
  verificado_por    VARCHAR(80) NOT NULL DEFAULT '',
  verificado_at     DATETIME NULL,
  comentario        VARCHAR(255) NOT NULL DEFAULT '',
  created_at        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_evidencia_form_tipo (form_uuid, tipo),
  KEY idx_evidencia_registro (registro_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- -----------------------------------------------------------------
-- 4. Configuracion inicial: NINGUNA (decision D8, revisada el 25/10/2026)
--
-- La evidencia NO se exige por defecto. Los flags quedan en 0 (configurado:
-- no exige evidencia) y el administrador los activa en
-- Admin > Tipos de Proceso, proceso por proceso, cuando corresponda.
--
-- Que se reviso: esta migracion activaba los tres procesos de abajo
-- (HORAS MAQUINAS, PROCESO y VOLTEO). Con eso, el deploy de la evidencia
-- encendia la exigencia para todos los operadores de una, sin que nadie
-- hubiera decidido, proceso por proceso, si el proceso la necesita.
--
--   HORAS MAQUINAS -> foto del horometro        (lo decide el admin)
--   PROCESO        -> horometro + pantalla      (lo decide el admin)
--   VOLTEO         -> foto de la pantalla       (lo decide el admin)
--
-- Los UPDATE de abajo solo tocan filas cuyo flag esta en NULL. Por eso, una
-- vez que el administrador encienda o apague un flag (queda en 1 o en 0), un
-- deploy posterior NO lo pisa: la decision es del administrador y la
-- migracion no la pisa.
-- -----------------------------------------------------------------
UPDATE tipo_de_proceso
   SET requiere_foto_horometro = 0
 WHERE UPPER(TRIM(nombre)) IN ('HORAS MAQUINAS', 'PROCESO')
   AND requiere_foto_horometro IS NULL;

UPDATE tipo_de_proceso
   SET requiere_foto_procesador = 0
 WHERE UPPER(TRIM(nombre)) IN ('PROCESO', 'VOLTEO')
   AND requiere_foto_procesador IS NULL;

COMMIT;
