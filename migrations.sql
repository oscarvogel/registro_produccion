-- =============================================================
-- Script de migración para el sistema de Registro de Producción
-- Fecha: 2026-02-12
-- =============================================================

-- 1. Agregar campo 'encargado' a la tabla personal
ALTER TABLE personal
  ADD COLUMN encargado TINYINT(1) NOT NULL DEFAULT 0 AFTER activo;

-- 2. Crear tabla tipo_de_proceso (catálogo maestro)
--    Cada tipo define qué campos se deben mostrar en el formulario
CREATE TABLE IF NOT EXISTS tipo_de_proceso (
  id            INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre        VARCHAR(100) NOT NULL,
  campos        VARCHAR(255) NOT NULL DEFAULT '' COMMENT 'Campos separados por coma que aplican a este proceso',
  activo        TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 3. Insertar los tipos de proceso
INSERT INTO tipo_de_proceso (id, nombre, campos) VALUES
  (1,  'CARGA',                    'tn_despachadas'),
  (2,  'EXTRACCION',               'carros,distancia_recorrida'),
  (3,  'PROCESO',                  'm3,plantas'),
  (4,  'VOLTEO',                   'plantas'),
  (5,  'HORAS MAQUINAS',           'hora_inicio,hora_fin'),
  (6,  'DESPEJE Y SUBSOLADO',      'has'),
  (7,  'EMPUJE PESADO',            'has'),
  (8,  'DESTOCONADO Y SUBSOLADO',  'has,horas_disposicion'),
  (9,  'PERFILADO',                'km'),
  (10, 'CARRETEO',                 'km'),
  (11, 'ACOPIO BIOMASA',           'tn_despachadas'),
  (12, 'CHIPEADO EN SUELO',        'tn_despachadas'),
  (13, 'CHIPEADO SOBRE CAMION',    'tn_despachadas');

-- 4. Tabla pivot: qué tipos de proceso puede tener cada unidad de negocio
CREATE TABLE IF NOT EXISTS unidadnegocio_tipo_proceso (
  un_id             INT(10) UNSIGNED NOT NULL,
  tipo_proceso_id   INT UNSIGNED NOT NULL,
  PRIMARY KEY (un_id, tipo_proceso_id),
  CONSTRAINT FK_untp_un FOREIGN KEY (un_id)
    REFERENCES unidadnegocio (idUnidadNegocio) ON UPDATE CASCADE,
  CONSTRAINT FK_untp_tp FOREIGN KEY (tipo_proceso_id)
    REFERENCES tipo_de_proceso (id) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- 5. Agregar tipo_de_proceso_id al personal (nullable = no obligatorio)
ALTER TABLE personal
  ADD COLUMN tipo_de_proceso_id INT UNSIGNED NULL DEFAULT NULL AFTER encargado,
  ADD CONSTRAINT FK_personal_tipo_proceso FOREIGN KEY (tipo_de_proceso_id)
    REFERENCES tipo_de_proceso (id) ON UPDATE CASCADE ON DELETE SET NULL;

-- 6. NOTA: La tabla tablero_produccion ya tiene la columna 'operacion' (varchar 50)
--    que se usa para almacenar el nombre del tipo de proceso (CARGA, EXTRACCION, etc.)
--    No se necesita ALTER TABLE adicional sobre tablero_produccion.

-- ============================================================
-- EJEMPLO: Asociar tipos de proceso a una unidad de negocio
-- Reemplazar 1 con el idUnidadNegocio real
-- ============================================================
-- INSERT INTO unidadnegocio_tipo_proceso (un_id, tipo_proceso_id) VALUES
--   (1, 1),  -- UN 1 -> CARGA
--   (1, 2),  -- UN 1 -> EXTRACCION
--   (1, 3),  -- UN 1 -> PROCESO
--   (1, 5);  -- UN 1 -> HORAS MAQUINAS

CREATE TABLE `asignaciones_operativas` (
  `idAsignacion` int(10) UNSIGNED NOT NULL,
  `idMovil` int(10) UNSIGNED NOT NULL,
  `idChofer` int(10) UNSIGNED NOT NULL,
  `idProceso` int(10) UNSIGNED NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- Volcado de datos para la tabla `asignaciones_operativas`
--

INSERT INTO `asignaciones_operativas` (`idAsignacion`, `idMovil`, `idChofer`, `idProceso`) VALUES
(1, 302, 626, 3);

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `asignaciones_operativas`
--
ALTER TABLE `asignaciones_operativas`
  ADD PRIMARY KEY (`idAsignacion`),
  ADD KEY `idx_asig_movil` (`idMovil`),
  ADD KEY `idx_asig_chofer` (`idChofer`),
  ADD KEY `idx_asig_proceso` (`idProceso`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `asignaciones_operativas`
--
ALTER TABLE `asignaciones_operativas`
  MODIFY `idAsignacion` int(10) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `asignaciones_operativas`
--
ALTER TABLE `asignaciones_operativas`
  ADD CONSTRAINT `fk_chofer_op` FOREIGN KEY (`idChofer`) REFERENCES `personal` (`idPersonal`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_movil_op` FOREIGN KEY (`idMovil`) REFERENCES `moviles` (`idMovil`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_proceso_op` FOREIGN KEY (`idProceso`) REFERENCES `tipo_de_proceso` (`id`) ON UPDATE CASCADE;
COMMIT;

CREATE TABLE kpi_definicion (
  id              INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre          VARCHAR(100) NOT NULL COMMENT 'Ej: Toneladas Despachadas',
  campo_origen    VARCHAR(80)  NOT NULL COMMENT 'Columna en tablero_produccion que se agrega/promedia',
  agregacion      ENUM('SUM','AVG','COUNT','MAX','CUSTOM') NOT NULL DEFAULT 'SUM',
  unidad          VARCHAR(20)  NOT NULL DEFAULT '' COMMENT 'Ej: TN, M3, HAS, KM, HS',
  icono           VARCHAR(50)  NOT NULL DEFAULT '' COMMENT 'Nombre de ícono Lucide',
  descripcion     VARCHAR(255) NOT NULL DEFAULT '',
  activo          TINYINT(1)   NOT NULL DEFAULT 1,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;