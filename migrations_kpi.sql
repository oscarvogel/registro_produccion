-- =============================================================
-- Script de migración KPI — Registro de Producción Forestal
-- Fecha: 2026-02-24
-- =============================================================
-- NOTA: Las tablas kpi_definicion y tipo_proceso_kpi deben existir
--       antes de ejecutar estos INSERTs.
-- =============================================================

-- ─── 1. Poblar kpi_definicion ────────────────────────────────
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


-- ─── 2. Poblar tipo_proceso_kpi ──────────────────────────────
-- Formato: (tipo_proceso_id, kpi_id, orden, es_principal)

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
