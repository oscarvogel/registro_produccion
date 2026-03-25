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

INSERT INTO kpi_definicion
  (id, nombre, campo_origen, agregacion, unidad, icono, descripcion, activo)
VALUES
  (1,  'Toneladas Despachadas', 'tn_despachadas',          'SUM',    'TN',  'truck',          'Suma total de toneladas despachadas en el período',            1),
  (2,  'Metros Cúbicos',        'm3',                      'SUM',    'M³',  'box',            'Suma total de metros cúbicos procesados',                      1),
  (3,  'Plantas Procesadas',    'plantas',                  'SUM',    'uds', 'leaf',           'Cantidad total de plantas procesadas',                         1),
  (4,  'Carros',                'carros',                   'SUM',    'uds', 'layers',         'Cantidad total de carros utilizados',                          1),
  (5,  'Metros Recorridos',     'mtrs_recorridos',          'SUM',    'mts', 'route',          'Suma de metros recorridos en extracción',                      1),
  (6,  'KM Carreteo',           'km_carreteo',              'SUM',    'km',  'map-pin',        'Kilómetros totales de carreteo',                               1),
  (7,  'KM Perfilado',          'km_perfilado',             'SUM',    'km',  'map',            'Kilómetros totales de perfilado',                              1),
  (8,  'Hectáreas',             'has',                      'SUM',    'HAS', 'grid-3x3',       'Hectáreas trabajadas en el período',                           1),
  (9,  'Horas Disposición',     'hr_disposicion',           'SUM',    'hs',  'clock',          'Horas de disposición acumuladas',                              1),
  (10, 'Combustible Consumido', 'combustible',              'SUM',    'lts', 'fuel',           'Litros de combustible consumidos',                             1),
  (11, 'Horas No Operativas',   'hrs_no_op',                'SUM',    'hs',  'alert-circle',   'Horas no operativas acumuladas',                               1),
  (12, 'Horas Trabajadas',      'CUSTOM:horas_trabajadas',  'CUSTOM', 'hs',  'timer',          'Horas trabajadas calculadas: SUM(hr_fin - hr_inicio)',         1),
  (13, 'Eficiencia Operativa',  'CUSTOM:eficiencia',        'CUSTOM', '%',   'percent',        'Eficiencia: (hrs_trabajadas - hrs_no_op) / hrs_trabajadas',    1),
  (14, 'Registros del Período', 'CUSTOM:registros',         'COUNT',  'reg', 'clipboard-list', 'Cantidad de registros en el período',                          1);

CREATE TABLE `tipo_proceso_kpi` (
  `tipo_proceso_id` int(10) UNSIGNED NOT NULL,
  `kpi_id` int(10) UNSIGNED NOT NULL,
  `orden` tinyint(3) UNSIGNED NOT NULL DEFAULT 0,
  `es_principal` tinyint(1) NOT NULL DEFAULT 0 COMMENT '1 = KPI destacado/hero card',
  PRIMARY KEY (`tipo_proceso_id`, `kpi_id`),
  CONSTRAINT `fk_tipo_proceso_kpi_tipo_proceso`
    FOREIGN KEY (`tipo_proceso_id`) REFERENCES `tipo_de_proceso` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `fk_tipo_proceso_kpi_kpi`
    FOREIGN KEY (`kpi_id`) REFERENCES `kpi_definicion` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- CARGA (1) → tn_despachadas(P), combustible, horas_trabajadas, eficiencia, registros
INSERT INTO tipo_proceso_kpi (tipo_proceso_id, kpi_id, orden, es_principal) VALUES
  (1, 1,  1, 1),
  (1, 10, 2, 0),
  (1, 12, 3, 0),
  (1, 13, 4, 0),
  (1, 14, 5, 0);

-- EXTRACCION (2) → carros(P), mtrs_recorridos, combustible, horas_trabajadas, eficiencia, registros
INSERT INTO tipo_proceso_kpi (tipo_proceso_id, kpi_id, orden, es_principal) VALUES
  (2, 4,  1, 1),
  (2, 5,  2, 0),
  (2, 10, 3, 0),
  (2, 12, 4, 0),
  (2, 13, 5, 0),
  (2, 14, 6, 0);

-- PROCESO (3) → m3(P), plantas, horas_trabajadas, eficiencia, combustible, registros
INSERT INTO tipo_proceso_kpi (tipo_proceso_id, kpi_id, orden, es_principal) VALUES
  (3, 2,  1, 1),
  (3, 3,  2, 0),
  (3, 12, 3, 0),
  (3, 13, 4, 0),
  (3, 10, 5, 0),
  (3, 14, 6, 0);

-- VOLTEO (4) → plantas(P), combustible, horas_trabajadas, eficiencia, registros
INSERT INTO tipo_proceso_kpi (tipo_proceso_id, kpi_id, orden, es_principal) VALUES
  (4, 3,  1, 1),
  (4, 10, 2, 0),
  (4, 12, 3, 0),
  (4, 13, 4, 0),
  (4, 14, 5, 0);

-- HORAS MAQUINAS (5) → horas_trabajadas(P), hrs_no_op, eficiencia, combustible, registros
INSERT INTO tipo_proceso_kpi (tipo_proceso_id, kpi_id, orden, es_principal) VALUES
  (5, 12, 1, 1),
  (5, 11, 2, 0),
  (5, 13, 3, 0),
  (5, 10, 4, 0),
  (5, 14, 5, 0);

-- DESPEJE Y SUBSOLADO (6) → has(P), combustible, horas_trabajadas, eficiencia, registros
INSERT INTO tipo_proceso_kpi (tipo_proceso_id, kpi_id, orden, es_principal) VALUES
  (6, 8,  1, 1),
  (6, 10, 2, 0),
  (6, 12, 3, 0),
  (6, 13, 4, 0),
  (6, 14, 5, 0);

-- EMPUJE PESADO (7) → has(P), combustible, horas_trabajadas, eficiencia, registros
INSERT INTO tipo_proceso_kpi (tipo_proceso_id, kpi_id, orden, es_principal) VALUES
  (7, 8,  1, 1),
  (7, 10, 2, 0),
  (7, 12, 3, 0),
  (7, 13, 4, 0),
  (7, 14, 5, 0);

-- DESTOCONADO Y SUBSOLADO (8) → has(P), hr_disposicion, combustible, horas_trabajadas, eficiencia, registros
INSERT INTO tipo_proceso_kpi (tipo_proceso_id, kpi_id, orden, es_principal) VALUES
  (8, 8,  1, 1),
  (8, 9,  2, 0),
  (8, 10, 3, 0),
  (8, 12, 4, 0),
  (8, 13, 5, 0),
  (8, 14, 6, 0);

-- PERFILADO (9) → km_perfilado(P), combustible, horas_trabajadas, eficiencia, registros
INSERT INTO tipo_proceso_kpi (tipo_proceso_id, kpi_id, orden, es_principal) VALUES
  (9, 7,  1, 1),
  (9, 10, 2, 0),
  (9, 12, 3, 0),
  (9, 13, 4, 0),
  (9, 14, 5, 0);

-- CARRETEO (10) → km_carreteo(P), combustible, horas_trabajadas, eficiencia, registros
INSERT INTO tipo_proceso_kpi (tipo_proceso_id, kpi_id, orden, es_principal) VALUES
  (10, 6,  1, 1),
  (10, 10, 2, 0),
  (10, 12, 3, 0),
  (10, 13, 4, 0),
  (10, 14, 5, 0);

-- ACOPIO BIOMASA (11) → tn_despachadas(P), combustible, horas_trabajadas, eficiencia, registros
INSERT INTO tipo_proceso_kpi (tipo_proceso_id, kpi_id, orden, es_principal) VALUES
  (11, 1,  1, 1),
  (11, 10, 2, 0),
  (11, 12, 3, 0),
  (11, 13, 4, 0),
  (11, 14, 5, 0);

-- CHIPEADO EN SUELO (12) → tn_despachadas(P), combustible, horas_trabajadas, eficiencia, registros
INSERT INTO tipo_proceso_kpi (tipo_proceso_id, kpi_id, orden, es_principal) VALUES
  (12, 1,  1, 1),
  (12, 10, 2, 0),
  (12, 12, 3, 0),
  (12, 13, 4, 0),
  (12, 14, 5, 0);

-- CHIPEADO SOBRE CAMION (13) → tn_despachadas(P), combustible, horas_trabajadas, eficiencia, registros
INSERT INTO tipo_proceso_kpi (tipo_proceso_id, kpi_id, orden, es_principal) VALUES
  (13, 1,  1, 1),
  (13, 10, 2, 0),
  (13, 12, 3, 0),
  (13, 13, 4, 0),
  (13, 14, 5, 0);


  CREATE TABLE actas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rodal_id INT NOT NULL DEFAULT 0,
    numero VARCHAR(30) NOT NULL DEFAULT '0',
    vam DECIMAL(12, 4) NOT NULL,
    tarifa DECIMAL(12, 4) NOT NULL,
    extraccion DECIMAL(12, 4) NOT NULL,
    carga DECIMAL(12, 4) NOT NULL,
    periodo VARCHAR(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;